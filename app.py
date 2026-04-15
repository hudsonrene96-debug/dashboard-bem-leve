import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="BI Estratégico BEM LEVE", layout="wide")

# 1. Carregar Dados
df = pd.read_csv('VENDAS_LIMPAS.csv', sep=';')
df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'])

# --- SIDEBAR (FILTROS) ---
st.sidebar.title("🎯 Filtros Estratégicos")

# Filtro de Data
data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())

# NOVO: Filtro por Empresa (Multi-seleção)
lista_empresas = sorted(df['CLIENTE'].unique())
empresas_selecionadas = st.sidebar.multiselect(
    "Selecionar Empresas Específicas:",
    options=lista_empresas,
    default=None, # Começa vazio para mostrar todas, ou você pode escolher
    help="Se deixar vazio, o dashboard mostrará todas as empresas."
)

# --- APLICAÇÃO DOS FILTROS ---
df_f = df[(df['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df['DATA_NEGOCIACAO'].dt.date <= data_fim)].copy()

if empresas_selecionadas:
    df_f = df_f[df_f['CLIENTE'].isin(empresas_selecionadas)]

# --- CÁLCULOS ESTRATÉGICOS ---
if not df_f.empty:
    # Identificar Melhor Vendedor do filtro atual
    vendas_por_vendedor = df_f.groupby('VENDEDOR')['FATURAMENTO_LIQUIDO'].sum()
    melhor_vendedor = vendas_por_vendedor.idxmax()
    valor_vendedor = vendas_por_vendedor.max()
    
    # Identificar Melhor Cliente do filtro atual
    vendas_por_cliente = df_f.groupby('CLIENTE')['FATURAMENTO_LIQUIDO'].sum()
    top_cliente = vendas_por_cliente.idxmax()
    valor_top_cliente = vendas_por_cliente.max()

    # --- TOPO: INDICADORES DINÂMICOS ---
    st.title("📊 Inteligência por Empresa e Segmento")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Faturamento no Filtro", f"R$ {df_f['FATURAMENTO_LIQUIDO'].sum():,.2f}")
    c2.metric("🏆 Melhor Vendedor (Nesta Seleção)", melhor_vendedor, f"R$ {valor_vendedor:,.2f}")
    c3.metric("🏢 Empresa Líder", top_cliente, f"R$ {valor_top_cliente:,.2f}")

    st.markdown("---")

    # --- GRÁFICO 1: FATURAMENTO DETALHADO POR EMPRESA ---
    st.subheader("🏢 Faturamento por Empresa Separadamente")
    faturamento_empresa = df_f.groupby('CLIENTE')['FATURAMENTO_LIQUIDO'].sum().sort_values(ascending=True)
    
    fig1, ax1 = plt.subplots(figsize=(12, max(6, len(faturamento_empresa)*0.4)))
    bars1 = ax1.barh(faturamento_empresa.index, faturamento_empresa.values, color='#457B9D')
    ax1.bar_label(bars1, fmt=' R$ %.2f', padding=5, fontweight='bold')
    st.pyplot(fig1)

    # --- GRÁFICO 2: PRODUTOS E VOLUME ---
    col_v1, col_v2 = st.columns(2)

    with col_v1:
        st.subheader("📦 Produtos Mais Vendidos (Qtd)")
        mais_vendidos = df_f.groupby('PRODUTO')['QUANTIDADE'].sum().sort_values(ascending=True).tail(10)
        fig2, ax2 = plt.subplots()
        bars2 = ax2.barh(mais_vendidos.index, mais_vendidos.values, color='#2a9d8f')
        ax2.bar_label(bars2, padding=3)
        st.pyplot(fig2)

    with col_v2:
        st.subheader("📉 Produtos Menos Vendidos (Qtd)")
        menos_vendidos = df_f.groupby('PRODUTO')['QUANTIDADE'].sum().sort_values(ascending=True).head(5)
        fig3, ax3 = plt.subplots()
        bars3 = ax3.barh(menos_vendidos.index, menos_vendidos.values, color='#e76f51')
        ax3.bar_label(bars3, padding=3)
        st.pyplot(fig3)

else:
    st.warning("Nenhum dado encontrado para os filtros selecionados. Tente ajustar as datas ou empresas.")
