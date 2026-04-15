import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="BI Estratégico", layout="wide")

# 1. Carregamento com Limpeza de Caracteres Especiais
@st.cache_data
def carregar_dados_limpos():
    arquivos = ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']
    df = None
    for arq in arquivos:
        try:
            df = pd.read_csv(arq, sep=';', encoding='utf-8')
            break
        except:
            try:
                df = pd.read_csv(arq, sep=';', encoding='latin1')
                break
            except:
                continue
    
    if df is not None:
        df.columns = [str(c).strip() for c in df.columns]
        
        # LIMPEZA RADICAL DE NOMES: Remove nulos, converte pra string e remove espaços extras
        df['CLIENTE'] = df['CLIENTE'].apply(lambda x: str(x).strip() if pd.notna(x) else "Não Informado")
        df['VENDEDOR'] = df['VENDEDOR'].apply(lambda x: str(x).strip() if pd.notna(x) else "Vendedor")
        
        # Números e Datas
        df['VALOR_LIQUIDO'] = pd.to_numeric(df['VALOR_LIQUIDO'], errors='coerce').fillna(0)
        df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
        df = df.dropna(subset=['DATA_NEGOCIACAO'])
        
        return df
    return None

df = carregar_dados_limpos()

if df is not None:
    # --- CONSTRUÇÃO DA LISTA DE EMPRESAS SEM USAR SORTED NO PANDAS ---
    # Pegamos os valores, transformamos em set (únicos) e ordenamos manualmente
    nomes_brutos = df['CLIENTE'].unique().tolist()
    lista_empresas = []
    for n in nomes_brutos:
        if n and str(n).lower() != 'nan':
            lista_empresas.append(str(n))
    
    # Ordenação manual (Python puro é mais tolerante que o Pandas)
    lista_empresas.sort()

    # --- SIDEBAR ---
    st.sidebar.header("🎯 Filtros")
    
    # Multiselect usando a lista limpa
    empresas_sel = st.sidebar.multiselect("Selecionar Empresas:", options=lista_empresas)
    
    data_inicio = st.sidebar.date_input("De:", df['DATA_NEGOCIACAO'].min())
    data_fim = st.sidebar.date_input("Até:", df['DATA_NEGOCIACAO'].max())

    # --- FILTRAGEM ---
    df_f = df.copy()
    df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df_f['DATA_NEGOCIACAO'].dt.date <= data_fim)]
    
    if empresas_sel:
        # Filtro forçado por string
        df_f = df_f[df_f['CLIENTE'].astype(str).isin(empresas_sel)]

    # --- DASHBOARD ---
    if not df_f.empty:
        st.title("📊 Painel Comercial")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Faturamento", f"R$ {df_f['VALOR_LIQUIDO'].sum():,.2f}")
        
        vendas = df_f.groupby('VENDEDOR')['VALOR_LIQUIDO'].sum()
        if not vendas.empty:
            c2.metric("🏆 Vendedor", str(vendas.idxmax()))
        
        c3.metric("🏢 Clientes", len(df_f['CLIENTE'].unique()))

        st.markdown("---")

        # Gráfico
        st.subheader("🏢 Faturamento por Empresa")
        fat_emp = df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().sort_values(ascending=True).tail(15)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        # Forçamos o índice a ser string no gráfico para evitar erros de renderização
        ax.barh([str(i) for i in fat_emp.index], fat_emp.values, color='#2A9D8F')
        plt.subplots_adjust(left=0.3)
        st.pyplot(fig)
    else:
        st.info("Nenhum dado encontrado.")
else:
    st.error("Não foi possível carregar os dados. Verifique os arquivos CSV.")
