import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="BI Estratégico BEM LEVE", layout="wide")

# 1. Carregamento Ultra-Seguro
def carregar_dados():
    try:
        # Tenta ler o arquivo. Se falhar, para o app aqui.
        try:
            dados = pd.read_csv('VENDAS_LIMPAS.csv', sep=';')
        except:
            dados = pd.read_csv('VENDAS_CONVERTIDO.csv', sep=';')
        
        # Limpa nomes das colunas (remove espaços)
        dados.columns = [str(c).strip() for c in dados.columns]
        
        # Converte VALOR_LIQUIDO para numero e DATA para data
        dados['VALOR_LIQUIDO'] = pd.to_numeric(dados['VALOR_LIQUIDO'], errors='coerce').fillna(0)
        dados['DATA_NEGOCIACAO'] = pd.to_datetime(dados['DATA_NEGOCIACAO'], errors='coerce')
        
        # Remove linhas sem data
        dados = dados.dropna(subset=['DATA_NEGOCIACAO'])
        
        return dados
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None

df = carregar_dados()

if df is not None:
    # --- FILTRO DE EMPRESA (O PONTO DO ERRO) ---
    # Criamos a lista de forma manual e forçada
    nomes_brutos = df['CLIENTE'].unique()
    lista_final_empresas = []

    for nome in nomes_brutos:
        # Só adiciona se não for nulo e for texto
        if pd.notna(nome):
            lista_final_empresas.append(str(nome))

    # Ordena a lista de textos (agora é impossível dar erro de float vs str)
    lista_final_empresas.sort()

    # --- INTERFACE ---
    st.sidebar.header("🎯 Filtros")
    
    empresas_sel = st.sidebar.multiselect("Selecionar Empresas:", options=lista_final_empresas)
    
    data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
    data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())

    # --- FILTRAGEM ---
    df_f = df.copy()
    if empresas_sel:
        # Forçamos a coluna de filtro a ser string também
        df_f = df_f[df_f['CLIENTE'].astype(str).isin(empresas_sel)]
    
    df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= data_inicio) & 
                (df_f['DATA_NEGOCIACAO'].dt.date <= data_fim)]

    # --- DASHBOARD ---
    if not df_f.empty:
        st.title("📊 Painel de Vendas")
        
        # KPIs
        c1, c2, c3 = st.columns(3)
        fat_total = df_f['VALOR_LIQUIDO'].sum()
        c1.metric("💰 Faturamento Total", f"R$ {fat_total:,.2f}")
        
        vendas_v = df_f.groupby('VENDEDOR')['VALOR_LIQUIDO'].sum()
        if not vendas_v.empty:
            c2.metric("🏆 Melhor Vendedor", str(vendas_v.idxmax()))
        
        c3.metric("🏢 Melhor Cliente", str(df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().idxmax()))

        st.markdown("---")
        
        # Gráfico de Empresas
        st.subheader("🏢 Faturamento por Empresa")
        fat_emp = df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().sort_values(ascending=True).tail(15)
        fig, ax = plt.subplots(figsize=(10, 6))
        # Garantimos que o índice do gráfico seja string
        ax.barh(fat_emp.index.astype(str), fat_emp.values, color='#2A9D8F')
        plt.subplots_adjust(left=0.3)
        st.pyplot(fig)
    else:
        st.info("Nenhum dado para os filtros aplicados.")
