import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Gestão de Elite - BEM LEVE", layout="wide")

# 1. Carregar Dados
df = pd.read_csv('VENDAS_LIMPAS.csv', sep=';')
df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'])

# --- SIDEBAR ---
st.sidebar.header("Configurações de Meta")
meta_vendedor = st.sidebar.number_input("Meta por Vendedor (R$)", value=5000.0)
margem_minima = st.sidebar.slider("Margem Mínima Aceitável (%)", 0, 100, 15)

# Filtro de Data
data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())

# Filtrar dados
mask = (df['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df['DATA_NEGOCIACAO'].dt.date <= data_fim)
df_f = df.loc[mask].copy()
df_f['MARGEM_%'] = (df_f['LUCRO_ESTIMADO'] / df_f['FATURAMENTO_LIQUIDO'].replace(0, 1)) * 100

# --- TOPO: KPIs ---
st.title("🚀 Painel de Gestão Avançada")
c1, c2, c3 = st.columns(3)
c1.metric("Faturamento Total", f"R$ {df_f['FATURAMENTO_LIQUIDO'].sum():,.2f}")
c2.metric("Lucro Estimado", f"R$ {df_f['LUCRO_ESTIMADO'].sum():,.2f}")
c3.metric("Margem Média", f"{df_f['MARGEM_%'].mean():.1f}%")

# --- GRÁFICO 1: VENDEDORES COM LINHA DE META ---
st.subheader("🏆 Ranking de Vendedores vs Meta")
vend_rank = df_f.groupby('VENDEDOR')['FATURAMENTO_LIQUIDO'].sum().sort_values(ascending=True)

fig1, ax1 = plt.subplots(figsize=(10, 6))
# Cores dinâmicas: Verde se bateu a meta, Azul se não
cores = ['#2ecc71' if v >= meta_vendedor else '#3498db' for v in vend_rank.values]
bars = ax1.barh(vend_rank.index, vend_rank.values, color=cores)
ax1.bar_label(bars, fmt='R$ %.2f', padding=5, fontweight='bold')

# Adiciona linha de meta
ax1.axvline(meta_vendedor, color='red', linestyle='--', label=f'Meta (R$ {meta_vendedor})')
ax1.legend()
st.pyplot(fig1)

# --- GRÁFICO 2: ALERTA DE MARGEM ---
st.subheader("⚠️ Alerta de Rentabilidade por Produto")
prod_margem = df_f.groupby('PRODUTO')['MARGEM_%'].mean().sort_values(ascending=True)

fig2, ax2 = plt.subplots(figsize=(10, 6))
# Cores dinâmicas: Vermelho se abaixo da margem mínima
cores_p = ['#e74c3c' if v < margem_minima else '#27ae60' for v in prod_margem.values]
bars2 = ax2.barh(prod_margem.index, prod_margem.values, color=cores_p)
ax2.bar_label(bars2, fmt='%.1f%%', padding=5)
ax1.axvline(margem_minima, color='black', linestyle=':', label='Margem Mínima')
st.pyplot(fig2)

st.info(f"Dica: Os itens em **vermelho** estão com rentabilidade abaixo de {margem_minima}%. Revise custos ou preços!")
