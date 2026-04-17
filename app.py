import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Dashboard Bem Leve", layout="wide")

# 1. Carregamento e Limpeza (Garante que tudo seja lido corretamente)
@st.cache_data
def carregar_dados():
    arquivos = ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']
    df = None
    for arq in arquivos:
        try:
            df = pd.read_csv(arq, sep=';', encoding='latin1')
            break
        except:
            continue
    
    if df is not None:
        df.columns = [str(c).strip() for c in df.columns]
        # Força a coluna CLIENTE a ser texto e trata vazios
        df['CLIENTE'] = df['CLIENTE'].astype(str).replace('nan', 'Não Informado')
        df['VALOR_LIQUIDO'] = pd.to_numeric(df['VALOR_LIQUIDO'], errors='coerce').fillna(0)
        df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
        df = df.dropna(subset=['DATA_NEGOCIACAO'])
        return df
    return None

df = carregar_dados()

if df is not None:
    # --- AQUI ESTAVA O ERRO (LINHA 25) ---
    # Criamos a lista de forma manual, garantindo que TUDO seja texto (str)
    try:
        opcoes_unicas = df['CLIENTE'].unique()
        # Transformamos cada item em texto e filtramos o que for "vazio"
        lista_empresas = sorted([str(x) for x in opcoes_unicas if str(x).lower() != 'nan' and str(x) != ''])
    except Exception as e:
        # Se falhar a ordem, usa a lista sem organizar para o app não cair
        lista_empresas = list(df['CLIENTE'].unique())

    # --- SIDEBAR (FILTROS) ---
    st.sidebar.header("🎯 Filtros")
    # O multiselect agora recebe a lista blindada
    empresas_sel = st.sidebar.multiselect("Selecionar Empresas:", options=lista_empresas)
    
    data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
    data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())

    # --- APLICAR FILTROS ---
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
        c2.metric("🏢 Clientes", len(df_f['CLIENTE'].unique()))

        st.markdown("---")

        # Gráfico (Forçamos o índice a ser string aqui também)
        st.subheader("🏢 Faturamento por Empresa")
        fat_emp = df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().sort_values(ascending=True).tail(15)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh([str(i) for i in fat_emp.index], fat_emp.values, color='#2A9D8F')
        plt.subplots_adjust(left=0.3)
        st.pyplot(fig)
    else:
        st.info("Utilize os filtros para visualizar.")
else:
    st.error("Arquivo de dados não encontrado.")
