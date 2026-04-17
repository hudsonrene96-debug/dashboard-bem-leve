import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Dashboard Bem Leve", layout="wide")

# 1. Carregamento com Limpeza na Base
@st.cache_data
def carregar_dados():
    try:
        # Tenta carregar os nomes de ficheiros possíveis
        df = None
        for nome in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
            try:
                df = pd.read_csv(nome, sep=';', encoding='latin1')
                break
            except:
                continue
        
        if df is not None:
            # Limpa espaços nos nomes das colunas
            df.columns = [str(c).strip() for c in df.columns]
            
            # Converte valores numéricos e datas
            df['VALOR_LIQUIDO'] = pd.to_numeric(df['VALOR_LIQUIDO'], errors='coerce').fillna(0)
            df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
            df = df.dropna(subset=['DATA_NEGOCIACAO'])
            
            # Força a coluna CLIENTE a ser APENAS texto logo aqui
            df['CLIENTE'] = df['CLIENTE'].astype(str).replace('nan', 'Não Identificado')
            
            return df
    except:
        return None

df = carregar_dados()

if df is not None:
    # --- CRIAÇÃO DA LISTA DE EMPRESAS (PONTO ONDE O ERRO OCORRE) ---
    # Em vez de usar sorted() direto no pandas, usamos um método manual 100% seguro
    try:
        # Criamos uma lista de strings puras, ignorando qualquer coisa que não seja texto
        lista_crua = df['CLIENTE'].unique().tolist()
        lista_limpa = []
        for item in lista_crua:
            item_str = str(item).strip()
            if item_str.lower() != 'nan' and item_str != '':
                lista_limpa.append(item_str)
        
        # Ordenamos a lista de strings (Python puro)
        lista_final_empresas = sorted(lista_limpa)
    except:
        # Se falhar, usa a lista sem ordenar para o site não cair
        lista_final_empresas = [str(x) for x in df['CLIENTE'].unique()]

    # --- SIDEBAR ---
    st.sidebar.header("🎯 Filtros")
    empresas_sel = st.sidebar.multiselect("Selecionar Empresas:", options=lista_final_empresas)
    
    data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
    data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())

    # --- APLICAR FILTROS ---
    df_f = df.copy()
    if empresas_sel:
        df_f = df_f[df_f['CLIENTE'].isin(empresas_sel)]
    
    df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df_f['DATA_NEGOCIACAO'].dt.date <= data_fim)]

    # --- DASHBOARD ---
    if not df_f.empty:
        st.title("📊 BI Estratégico")
        
        # KPIs
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Faturamento Total", f"R$ {df_f['VALOR_LIQUIDO'].sum():,.2f}")
        
        # Gráfico
        st.subheader("🏢 Faturamento por Empresa")
        fat_emp = df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().sort_values(ascending=True).tail(15)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        # Forçamos o eixo do gráfico a ser texto
        ax.barh([str(i) for i in fat_emp.index], fat_emp.values, color='#2A9D8F')
        plt.subplots_adjust(left=0.3)
        st.pyplot(fig)
    else:
        st.info("Selecione os filtros para visualizar.")
else:
    st.error("Erro: Não foi possível ler o ficheiro CSV.")
