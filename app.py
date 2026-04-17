import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Dashboard Bem Leve", layout="wide")

# 1. CARREGAMENTO COM BLOQUEIO DE ERRO
@st.cache_data
def carregar_dados_blindados():
    try:
        # Tenta abrir o arquivo disponível
        for arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
            try:
                dados = pd.read_csv(arq, sep=';', encoding='latin1')
                break
            except:
                continue
        
        # Limpeza de nomes de colunas
        dados.columns = [str(c).strip() for c in dados.columns]
        
        # Converte VALOR_LIQUIDO (dinheiro) para número
        dados['VALOR_LIQUIDO'] = pd.to_numeric(dados['VALOR_LIQUIDO'], errors='coerce').fillna(0)
        
        # Converte DATAS
        dados['DATA_NEGOCIACAO'] = pd.to_datetime(dados['DATA_NEGOCIACAO'], errors='coerce')
        dados = dados.dropna(subset=['DATA_NEGOCIACAO'])
        
        return dados
    except:
        return None

df = carregar_dados_blindados()

if df is not None:
    # --- CRIAÇÃO DA LISTA DE EMPRESAS (SEM USAR SORTED NO PANDAS) ---
    # Aqui é onde o erro acontece. Vamos contornar totalmente:
    lista_final = []
    try:
        # Pegamos os valores brutos e transformamos em texto um por um
        todos_clientes = df['CLIENTE'].unique()
        for c in todos_clientes:
            nome_texto = str(c).strip()
            if nome_texto.lower() != 'nan' and nome_texto != '':
                lista_final.append(nome_texto)
        
        # Ordenamos a lista de strings (Python puro é mais seguro que Pandas)
        lista_final.sort()
    except:
        # Se ainda assim der erro, mostra sem ordem mas não trava
        lista_final = [str(x) for x in df['CLIENTE'].unique()]

    # --- SIDEBAR (FILTROS) ---
    st.sidebar.header("🎯 Filtros")
    empresas_sel = st.sidebar.multiselect("Selecionar Empresas:", options=lista_final)
    
    data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
    data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())

    # --- APLICAR FILTROS ---
    df_f = df.copy()
    if empresas_sel:
        # Filtro forçado comparando apenas textos
        df_f = df_f[df_f['CLIENTE'].astype(str).isin(empresas_sel)]
    
    df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df_f['DATA_NEGOCIACAO'].dt.date <= data_fim)]

    # --- DASHBOARD ---
    if not df_f.empty:
        st.title("📊 BI Estratégico")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Faturamento Total", f"R$ {df_f['VALOR_LIQUIDO'].sum():,.2f}")
        
        # Gráfico de Empresas
        st.subheader("🏢 Top Clientes/Empresas")
        fat_emp = df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().sort_values(ascending=True).tail(15)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        # Forçamos o índice do gráfico a ser string para não bugar no Matplotlib
        ax.barh([str(i) for i in fat_emp.index], fat_emp.values, color='#2A9D8F')
        plt.subplots_adjust(left=0.3)
        st.pyplot(fig)
    else:
        st.warning("⚠️ Selecione filtros válidos.")
else:
    st.error("❌ Arquivo não encontrado ou corrompido.")
