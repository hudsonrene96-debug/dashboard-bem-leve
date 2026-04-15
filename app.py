import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns

# Configuração da página para ocupar a tela toda
st.set_page_config(page_title="Gestão Estratégica BEM LEVE", layout="wide")

# 1. Carregar Dados
df = pd.read_csv('VENDAS_CONVERTIDO.csv', sep=';')
df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'])

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1570/1570887.png", width=100)
st.sidebar.title("Filtros Estratégicos")

# Seletor de Data
data_inicio = st.sidebar.date_input("Data Inicial", df['DATA_NEGOCIACAO'].min())
data_fim = st.sidebar.date_input("Data Final", df['DATA_NEGOCIACAO'].max())

# Filtrando os dados
df_f = df[(df['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df['DATA_NEGOCIACAO'].dt.date <= data_fim)].copy()

# Cálculo de Margem
df_f['MARGEM_%'] = (df_f['LUCRO_ESTIMADO'] / df_f['FATURAMENTO_LIQUIDO'].replace(0, 1)) * 100

st.title("🚀 Painel de Controle BEM LEVE")
st.write(f"Análise de **{data_inicio.strftime('%d/%m/%Y')}** até **{data_fim.strftime('%d/%m/%Y')}**")

# --- LINHA 1: VENDEDORES ---
st.subheader("🏆 Melhores Vendedores (Ranking por Faturamento)")
vend_rank = df_f.groupby('VENDEDOR')['FATURAMENTO_LIQUIDO'].sum().sort_values(ascending=True)

fig1, ax1 = plt.subplots(figsize=(12, len(vend_rank)*0.4)) # Ajusta altura conforme nº de vendedores
bars = ax1.barh(vend_rank.index, vend_rank.values, color='#3498db')
ax1.bar_label(bars, fmt='R$ %.2f', padding=5, fontweight='bold', fontsize=10)
plt.title("Faturamento Total por Vendedor")
st.pyplot(fig1)

# --- LINHA 2: PRODUTOS (LADO A LADO) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📦 Volume: Mais Vendidos (Qtd)")
    prod_qtd = df_f.groupby('PRODUTO')['QUANTIDADE'].sum().sort_values(ascending=True).tail(10)
    fig2, ax2 = plt.subplots(figsize=(10, 8))
    bars2 = ax2.barh(prod_qtd.index, prod_qtd.values, color='#f1c40f')
    ax2.bar_label(bars2, fmt='%d un', padding=5, fontweight='bold')
    st.pyplot(fig2)

with col2:
    st.subheader("💹 Rentabilidade: Top Margens (%)")
    # Apenas produtos com faturamento relevante para não distorcer a margem
    prod_margem = df_f.groupby('PRODUTO')['MARGEM_%'].mean().sort_values(ascending=True).tail(10)
    fig3, ax3 = plt.subplots(figsize=(10, 8))
    bars3 = ax3.barh(prod_margem.index, prod_margem.values, color='#2ecc71')
    ax3.bar_label(bars3, fmt='%.1f%%', padding=5, fontweight='bold')
    st.pyplot(fig3)

# --- TABELA DE DADOS ---
if st.checkbox("Mostrar tabela de dados brutos"):
    st.write(df_f)
