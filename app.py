import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="BI Gestão Estratégica", layout="wide")

# 1. Função para carregar dados
def carregar_dados():
    for nome_arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            return pd.read_csv(nome_arq, sep=';')
        except:
            continue
    return None

df = carregar_dados()

if df is None:
    st.error("❌ Nenhum arquivo CSV encontrado no GitHub! Verifique se subiu o arquivo corretamente.")
    st.stop()

# Limpar nomes das colunas
df.columns = [c.strip().upper() for c in df.columns]

# --- MAPEAMENTO MANUAL SEGURO ---
# Aqui vamos tentar encontrar as colunas. Se falhar, usaremos a posição (índice)
def buscar_coluna(lista_palavras, colunas_df):
    for p in lista_palavras:
        for c in colunas_df:
            if p in c:
                return c
    return colunas_df[0] # Se não achar, pega a primeira só pra não travar

try:
    col_cliente = buscar_coluna(['CLIENTE', 'NOME', 'EMPRESA'], df.columns)
    col_vendedor = buscar_coluna(['VENDEDOR', 'CONSULTOR', 'REP'], df.columns)
    col_faturamento = buscar_coluna(['FATURAMENTO', 'VALOR', 'LIQUIDO', 'TOTAL'], df.columns)
    col_data = buscar_coluna(['DATA', 'NEGOCIACAO', 'EMISSAO'], df.columns)
    col_produto = buscar_coluna(['PRODUTO', 'DESCRICAO', 'ITEM'], df.columns)
    col_qtd = buscar_coluna(['QUANTIDADE', 'QTD', 'UNIDADES', 'VOLUME'], df.columns)
except Exception as e:
    st.error(f"Erro ao identificar colunas: {e}. Colunas detectadas: {list(df.columns)}")
    st.stop()

# Converter data
df[col_data] = pd.to_datetime(df[col_data], errors='coerce')

# --- SIDEBAR ---
st.sidebar.header("🎯 Filtros")
data_inicio = st.sidebar.date_input("Início", df[col_data].min() if not df[col_data].isnull().all() else None)
data_fim = st.sidebar.date_input("Fim", df[col_data].max() if not df[col_data].isnull().all() else None)

lista_empresas = sorted(df[col_cliente].unique())
empresas_sel = st.sidebar.multiselect("Selecionar Empresas:", options=lista_empresas)

# Filtro
df_f = df.copy()
if data_inicio and data_fim:
    df_f = df_f[(df_f[col_data].dt.date >= data_inicio) & (df_f[col_data].dt.date <= data_fim)]
if empresas_sel:
    df_f = df_f[df_f[col_cliente].isin(empresas_sel)]

# --- DASHBOARD ---
if not df_f.empty:
    st.title("📊 Painel de Performance")
    
    # KPIs
    c1, c2, c3 = st.columns(3)
    fatur_total = df_f[col_faturamento].sum()
    vendas_v = df_f.groupby(col_vendedor)[col_faturamento].sum()
    
    c1.metric("💰 Faturamento", f"R$ {fatur_total:,.2f}")
    c2.metric("🏆 Melhor Vendedor", vendas_v.idxmax(), f"R$ {vendas_v.max():,.2f}")
    c3.metric("🏢 Melhor Cliente", df_f.groupby(col_cliente)[col_faturamento].sum().idxmax())

    st.markdown("---")

    # Gráfico Empresa
    st.subheader("🏢 Faturamento por Empresa")
    fat_emp = df_f.groupby(col_cliente)[col_faturamento].sum().sort_values(ascending=True).tail(15)
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.barh(fat_emp.index, fat_emp.values, color='#2A9D8F')
    plt.tight_layout()
    st.pyplot(fig1)

    # Gráfico Produtos
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🔥 Top Produtos")
        p_v = df_f.groupby(col_produto)[col_qtd].sum().sort_values(ascending=True).tail(10)
        fig2, ax2 = plt.subplots()
        ax2.barh(p_v.index, p_v.values, color='#457B9D')
        st.pyplot(fig2)
    with col_b:
        st.subheader("🧊 Menos Vendidos")
        p_m = df_f.groupby(col_produto)[col_qtd].sum().sort_values(ascending=True).head(5)
        fig3, ax3 = plt.subplots()
        ax3.barh(p_m.index, p_m.values, color='#E76F51')
        st.pyplot(fig3)
else:
    st.warning("Ajuste os filtros para visualizar os dados.")
