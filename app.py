import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Configuração da Página
st.set_page_config(page_title="BI Estratégico", layout="wide")

# 1. Carregamento Blindado
@st.cache_data
def carregar_e_limpar():
    # Tenta ler o arquivo disponível
    try:
        df = pd.read_csv('VENDAS_LIMPAS.csv', sep=';')
    except:
        df = pd.read_csv('VENDAS_CONVERTIDO.csv', sep=';')
    
    # Limpa nomes de colunas
    df.columns = [str(c).strip() for c in df.columns]
    
    # CONVERSÃO FORÇADA: Se houver erro aqui, ele vira 'Não Informado'
    df['CLIENTE'] = df['CLIENTE'].apply(lambda x: str(x) if pd.notna(x) and str(x).lower() != 'nan' else 'Não Informado')
    df['VENDEDOR'] = df['VENDEDOR'].apply(lambda x: str(x) if pd.notna(x) and str(x).lower() != 'nan' else 'Vendedor Externo')
    
    # Valores Numéricos
    df['VALOR_LIQUIDO'] = pd.to_numeric(df['VALOR_LIQUIDO'], errors='coerce').fillna(0)
    
    # Datas
    df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
    df = df.dropna(subset=['DATA_NEGOCIACAO'])
    
    return df

df = carregar_e_limpar()

# --- CRIAÇÃO DA LISTA DE EMPRESAS (PONTO DO ERRO) ---
# Usamos um Set para garantir unicidade e depois listamos apenas Strings reais
nomes_unicos = set()
for item in df['CLIENTE'].values:
    nome_limpo = str(item).strip()
    if nome_limpo and nome_limpo.lower() != 'nan':
        nomes_unicos.add(nome_limpo)

lista_empresas = sorted(list(nomes_unicos))

# --- INTERFACE ---
st.title("📊 Painel Comercial")

with st.sidebar:
    st.header("🎯 Filtros")
    
    # Multiselect blindado
    empresas_sel = st.multiselect("Selecionar Empresas:", options=lista_empresas)
    
    # Datas
    data_inicio = st.date_input("De:", df['DATA_NEGOCIACAO'].min())
    data_fim = st.date_input("Até:", df['DATA_NEGOCIACAO'].max())

# --- FILTRAGEM ---
df_f = df.copy()

# Filtro de Data
df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= data_inicio) & 
            (df_f['DATA_NEGOCIACAO'].dt.date <= data_fim)]

# Filtro de Empresa
if empresas_sel:
    df_f = df_f[df_f['CLIENTE'].isin(empresas_sel)]

# --- EXIBIÇÃO ---
if not df_f.empty:
    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Total Líquido", f"R$ {df_f['VALOR_LIQUIDO'].sum():,.2f}")
    
    vendas_v = df_f.groupby('VENDEDOR')['VALOR_LIQUIDO'].sum()
    c2.metric("🏆 Top Vendedor", str(vendas_v.idxmax()))
    c3.metric("🏢 Qtd Clientes", len(df_f['CLIENTE'].unique()))

    st.markdown("---")

    # Gráfico
    st.subheader("🏢 Faturamento por Empresa")
    analise_emp = df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().sort_values(ascending=True).tail(15)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(analise_emp.index.astype(str), analise_emp.values, color='#2A9D8F')
    plt.subplots_adjust(left=0.3)
    st.pyplot(fig)
else:
    st.info("Nenhum dado encontrado para os filtros selecionados.")
