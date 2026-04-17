import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Dashboard Bem Leve", layout="wide")

# 1. Função de Carga Inteligente
@st.cache_data
def carregar_dados():
    # Tenta encontrar o arquivo no seu GitHub
    for arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            df = pd.read_csv(arq, sep=';', encoding='latin1')
            
            # LIMPEZA DE COLUNAS: Remove espaços e deixa tudo em MAIÚSCULO para facilitar
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Garante tipos básicos para evitar erros de comparação
            # Se a coluna 'VALOR_LIQUIDO' não existir, tenta 'FATURAMENTO_LIQUIDO'
            col_valor = 'VALOR_LIQUIDO' if 'VALOR_LIQUIDO' in df.columns else 'FATURAMENTO_LIQUIDO'
            if col_valor in df.columns:
                df[col_valor] = pd.to_numeric(df[col_valor], errors='coerce').fillna(0)
            
            # Datas
            df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
            df = df.dropna(subset=['DATA_NEGOCIACAO'])
            
            return df, col_valor
        except:
            continue
    return None, None

df, col_vendas = carregar_dados()

if df is not None:
    # --- BUSCA INTELIGENTE PELA COLUNA DE CLIENTE ---
    # Tentamos os nomes mais comuns. Se não achar, pega a primeira coluna de texto
    possiveis_nomes = ['CLIENTE', 'NOME_CLIENTE', 'PARCEIRO', 'NOME']
    col_cliente = 'CLIENTE' # Padrão
    for p in possiveis_nomes:
        if p in df.columns:
            col_cliente = p
            break

    # --- CRIAÇÃO DA LISTA DE FILTRO (ANTI-ERRO) ---
    try:
        # Forçamos tudo para string e removemos o que for 'nan'
        opcoes = [str(x).strip() for x in df[col_cliente].unique() if pd.notna(x)]
        lista_empresas = sorted([x for x in opcoes if x.lower() != 'nan' and x != ''])
    except:
        lista_empresas = sorted(list(df[col_cliente].astype(str).unique()))

    # --- SIDEBAR ---
    st.sidebar.header("🎯 Filtros")
    empresas_sel = st.sidebar.multiselect("Selecionar Empresas:", options=lista_empresas)
    
    data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
    data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())

    # --- FILTRAGEM ---
    df_f = df.copy()
    if empresas_sel:
        df_f = df_f[df_f[col_cliente].astype(str).isin(empresas_sel)]
    
    df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df_f['DATA_NEGOCIACAO'].dt.date <= data_fim)]

    # --- DASHBOARD ---
    if not df_f.empty:
        st.title("📊 BI Estratégico - Bem Leve")
        
        c1, c2 = st.columns(2)
        total = df_f[col_vendas].sum() if col_vendas in df_f.columns else 0
        c1.metric("💰 Faturamento Total", f"R$ {total:,.2f}")
        c2.metric("🏢 Qtd. Clientes", len(df_f[col_cliente].unique()))

        st.markdown("---")

        # Gráfico
        st.subheader("🏢 Faturamento por Empresa")
        fat_emp = df_f.groupby(col_cliente)[col_vendas].sum().sort_values(ascending=True).tail(15)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh([str(i) for i in fat_emp.index], fat_emp.values, color='#2A9D8F')
        plt.subplots_adjust(left=0.3)
        st.pyplot(fig)
    else:
        st.info("Ajuste os filtros para carregar os dados.")
else:
    st.error("❌ Coluna 'CLIENTE' não encontrada ou arquivo corrompido. Verifique o CSV.")
