import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="BI Estratégico BEM LEVE", layout="wide")

# 1. Carregar Dados
df = pd.read_csv('VENDAS_LIMPAS.csv', sep=';')
df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'])

# --- SIDEBAR (FILTROS) ---
st.sidebar.title("🎯 Filtros")
data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())

df_f = df[(df['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df['DATA_NEGOCIACAO'].dt.date <= data_fim)].copy()

# --- CÁLCULOS ESTRATÉGICOS ---
if not df_f.empty:
    melhor_cliente = df_f.groupby('CLIENTE')['FATURAMENTO_LIQUIDO'].sum().idxmax()
    valor_melhor_cliente = df_f.groupby('CLIENTE')['FATURAMENTO_LIQUIDO'].sum().max()
    produto_mais_vendido = df_f.groupby('PRODUTO')['QUANTIDADE'].sum().idxmax()
    
    # --- TOPO: INDICADORES ---
    st.title("🚀 Inteligência de Vendas")
    c1, c2, c3 = st.columns(3)
    c1.metric("🏆 Melhor Cliente", melhor_cliente, f"R$ {valor_melhor_cliente:,.2f}")
    c2.metric("📦 Produto Campeão", produto_mais_vendido)
    c3.metric("💰 Faturamento Total", f"R$ {df_f['FATURAMENTO_LIQUIDO'].sum():,.2f}")

    st.markdown("---")

    # --- GRÁFICO 1: QUANTIDADE DE PRODUTOS POR CLIENTE ---
    st.subheader("🛒 Volume de Itens por Cliente (Quem levou mais produtos)")
    # Agrupa por cliente e soma a quantidade de itens
    vol_cliente = df_f.groupby('CLIENTE')['QUANTIDADE'].sum().sort_values(ascending=True).tail(15)
    
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    bars1 = ax1.barh(vol_cliente.index, vol_cliente.values, color='#457B9D')
    ax1.bar_label(bars1, padding=5, fontweight='bold')
    ax1.set_xlabel("Quantidade Total de Itens")
    st.pyplot(fig1)

    # --- GRÁFICO 2: PRODUTOS MAIS E MENOS VENDIDOS ---
    col_prod1, col_prod2 = st.columns(2)

    with col_prod1:
        st.subheader("🔥 Top 10 Mais Vendidos")
        mais_vendidos = df_f.groupby('PRODUTO')['QUANTIDADE'].sum().sort_values(ascending=True).tail(10)
        fig2, ax2 = plt.subplots()
        bars2 = ax2.barh(mais_vendidos.index, mais_vendidos.values, color='#2a9d8f')
        ax2.bar_label(bars2, padding=3)
        st.pyplot(fig2)

    with col_prod2:
        st.subheader("🧊 5 Menos Vendidos (Alerta de Estoque)")
        # Filtramos apenas produtos com venda > 0 para ser realista
        menos_vendidos = df_f.groupby('PRODUTO')['QUANTIDADE'].sum().sort_values(ascending=True).head(5)
        fig3, ax3 = plt.subplots()
        bars3 = ax3.barh(menos_vendidos.index, menos_vendidos.values, color='#e76f51')
        ax3.bar_label(bars3, padding=3)
        st.pyplot(fig3)

else:
    st.error("Ops! Sem dados para o período selecionado.")
