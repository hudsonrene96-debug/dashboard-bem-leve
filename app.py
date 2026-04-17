import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Dashboard Bem Leve", layout="wide")

# 1. Carregamento com Limpeza Forçada
@st.cache_data
def carregar_dados_v100(): # Mudamos o nome para forçar novo cache
    for arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            df = pd.read_csv(arq, sep=';', encoding='latin1')
            df.columns = [str(c).strip() for c in df.columns]
            
            # Limpeza radical: transforma TUDO em string antes de qualquer operação
            df['CLIENTE'] = df['CLIENTE'].astype(str).replace('nan', 'Não Informado')
            df['VALOR_LIQUIDO'] = pd.to_numeric(df['VALOR_LIQUIDO'], errors='coerce').fillna(0)
            df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
            df = df.dropna(subset=['DATA_NEGOCIACAO'])
            return df
        except:
            continue
    return None

df = carregar_dados_v100()

if df is not None:
    # --- MÉTODO MANUAL PARA EVITAR O TYPEERROR ---
    # Criamos a lista de empresas sem usar o sorted() do Pandas/Numpy
    lista_opcoes = []
    try:
        # Extraímos os valores únicos como strings puras
        unicos = [str(x).strip() for x in df['CLIENTE'].unique() if pd.notna(x)]
        # Removemos qualquer item que seja 'nan' ou vazio
        lista_opcoes = [x for x in unicos if x.lower() != 'nan' and x != '']
        # Ordenação segura em Python puro
        lista_opcoes.sort()
    except:
        # Se ainda assim der erro, usamos a lista sem ordenar para não travar
        lista_opcoes = list(df['CLIENTE'].unique())

    # --- SIDEBAR ---
    st.sidebar.header("🎯 Filtros")
    empresas_sel = st.sidebar.multiselect("Filtrar Empresas:", options=lista_opcoes)
    
    data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
    data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())

    # --- FILTRAGEM ---
    df_f = df.copy()
    if empresas_sel:
        df_f = df_f[df_f['CLIENTE'].isin(empresas_sel)]
    
    df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= data_inicio) & 
                (df_f['DATA_NEGOCIACAO'].dt.date <= data_fim)]

    # --- DASHBOARD ---
    if not df_f.empty:
        st.title("📊 Painel Comercial - Bem Leve")
        
        c1, c2 = st.columns(2)
        c1.metric("💰 Faturamento Total", f"R$ {df_f['VALOR_LIQUIDO'].sum():,.2f}")
        c2.metric("🏢 Clientes Ativos", len(df_f['CLIENTE'].unique()))

        st.markdown("---")

        # Gráfico forçando conversão de índice para string
        st.subheader("🏢 Faturamento por Empresa")
        fat_emp = df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().sort_values(ascending=True).tail(15)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh([str(i) for i in fat_emp.index], fat_emp.values, color='#2A9D8F')
        plt.subplots_adjust(left=0.3)
        st.pyplot(fig)
    else:
        st.info("Ajuste os filtros para visualizar os dados.")
else:
    st.error("Erro ao carregar os dados. Verifique se o arquivo CSV está no GitHub.")
