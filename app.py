import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="BI Gestão Estratégica", layout="wide")

# 1. Carregar Dados com Tratamento de Erro
try:
    df = pd.read_csv('VENDAS_LIMPAS.csv', sep=';')
except:
    try:
        df = pd.read_csv('VENDAS_CONVERTIDO.csv', sep=';')
    except:
        st.error("❌ Arquivo CSV não encontrado no GitHub. Verifique o nome!")
        st.stop()

# Limpar espaços invisíveis nos nomes das colunas
df.columns = [c.strip() for c in df.columns]

# --- IDENTIFICAÇÃO AUTOMÁTICA DE COLUNAS ---
# Isso evita o erro de "KeyError" caso o nome mude um pouco
col_cliente = [c for c in df.columns if 'CLIENTE' in c.upper()][0]
col_vendedor = [c for c in df.columns if 'VENDEDOR' in c.upper()][0]
col_faturamento = [c for c in df.columns if 'FATURAMENTO' in c.upper()][0]
col_data = [c for c in df.columns if 'DATA' in c.upper()][0]
col_produto = [c for c in df.columns if 'PRODUTO' in c.upper()][0]
col_qtd = [c for c in df.columns if 'QUANTIDADE' in c.upper() or 'QTD' in c.upper()][0]

df[col_data] = pd.to_datetime(df[col_data])

# --- SIDEBAR ---
st.sidebar.header("🎯 Filtros")
data_inicio = st.sidebar.date_input("Início", df[col_data].min())
data_fim = st.sidebar.date_input("Fim", df[col_data].max())

lista_empresas = sorted(df[col_cliente].unique())
empresas_sel = st.sidebar.multiselect("Selecionar Empresas:", options=lista_empresas)

# Aplicar Filtros
df_f = df[(df[col_data].dt.date >= data_inicio) & (df[col_data].dt.date <= data_fim)].copy()
if empresas_sel:
    df_f = df_f[df_f[col_cliente].isin(empresas_sel)]

# --- DASHBOARD ---
if not df_f.empty:
    st.title("📊 Painel de Performance Comercial")
    
    # KPIs
    c1, c2, c3 = st.columns(3)
    faturamento_total = df_f[col_faturamento].sum()
    vendas_vend = df_f.groupby(col_vendedor)[col_faturamento].sum()
    
    c1.metric("💰 Faturamento Total", f"R$ {faturamento_total:,.2f}")
    c2.metric("🏆 Melhor Vendedor", vendas_vend.idxmax(), f"R$ {vendas_vend.max():,.2f}")
    c3.metric("🏢 Melhor Cliente", df_f.groupby(col_cliente)[col_faturamento].sum().idxmax())

    st.markdown("---")

    # Gráfico 1: Faturamento por Empresa
    st.subheader("🏢 Faturamento Detalhado por Empresa")
    faturamento_empresa = df_f.groupby(col_cliente)[col_faturamento].sum().sort_values(ascending=True).tail(15)
    fig1, ax1 = plt.subplots(figsize=(10, max(5, len(faturamento_empresa)*0.4)))
    bars1 = ax1.barh(faturamento_empresa.index, faturamento_empresa.values, color='#2A9D8F')
    ax1.bar_label(bars1, fmt=' R$ %.2f', padding=5, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig1)

    # Gráficos de Produtos
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🔥 Top Produtos")
        mais_v = df_f.groupby(col_produto)[col_qtd].sum().sort_values(ascending=True).tail(10)
        fig2, ax2 = plt.subplots()
        ax2.barh(mais_v.index, mais_v.values, color='#457B9D')
        ax2.bar_label(ax2.containers[0], padding=3)
        st.pyplot(fig2)
    with col_b:
        st.subheader("🧊 Menos Vendidos")
        menos_v = df_f.groupby(col_produto)[col_qtd].sum().sort_values(ascending=True).head(5)
        fig3, ax3 = plt.subplots()
        ax3.barh(menos_v.index, menos_v.values, color='#E76F51')
        ax3.bar_label(ax3.containers[0], padding=3)
        st.pyplot(fig3)
else:
    st.warning("Nenhum dado encontrado para os filtros aplicados.")
