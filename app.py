import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Configuração da Página
st.set_page_config(page_title="Gestão Estratégica - BEM LEVE", layout="wide")

# Estilo para melhorar a aparência
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

# 1. Carregar Dados
df = pd.read_csv('VENDAS_LIMPAS.csv', sep=';')
df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'])

# --- BARRA LATERAL ---
st.sidebar.title("🎯 Filtros e Metas")
data_inicio = st.sidebar.date_input("Data Inicial", df['DATA_NEGOCIACAO'].min())
data_fim = st.sidebar.date_input("Data Final", df['DATA_NEGOCIACAO'].max())
meta_empresa = st.sidebar.number_input("Meta por Empresa (R$)", value=3000)

# Filtragem de Dados
df_f = df[(df['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df['DATA_NEGOCIACAO'].dt.date <= data_fim)].copy()

# --- CABEÇALHO ---
st.title("📊 Inteligência Comercial")
st.write(f"Análise de **{data_inicio.strftime('%d/%m/%Y')}** a **{data_fim.strftime('%d/%m/%Y')}**")

c1, c2, c3 = st.columns(3)
c1.metric("Faturamento", f"R$ {df_f['FATURAMENTO_LIQUIDO'].sum():,.2f}")
c2.metric("Qtd. de Clientes Atendidos", df_f['CLIENTE'].nunique())
c3.metric("Lucro Estimado", f"R$ {df_f['LUCRO_ESTIMADO'].sum():,.2f}")

st.markdown("---")

# --- RANKING DE EMPRESAS (CLIENTES) ---
st.subheader("🏢 Ranking de Faturamento por Empresa (Clientes)")

# Agrupar dados por Cliente
empresa_data = df_f.groupby('CLIENTE')['FATURAMENTO_LIQUIDO'].sum().sort_values(ascending=True).tail(15)

if not empresa_data.empty:
    # Aumentamos o tamanho lateral (12) para os nomes das empresas caberem
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Cores: Destaque para quem passou da meta de compra
    colors = ['#90E0EF' if x < meta_empresa else '#0077B6' for x in empresa_data.values]
    
    bars = ax.barh(empresa_data.index, empresa_data.values, color=colors)
    
    # Limpeza estética
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.bar_label(bars, fmt=' R$ %.2f', padding=10, fontweight='bold', color='#023E8A')
    
    plt.title("Top 15 Maiores Compradores", fontsize=14, color='#03045E')
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.warning("Sem dados de clientes para este período.")

# --- RANKING DE VENDEDORES (VERSÃO COMPACTA ABAIXO) ---
st.markdown("---")
st.subheader("👥 Performance dos Vendedores")
vendedor_data = df_f.groupby('VENDEDOR')['FATURAMENTO_LIQUIDO'].sum().sort_values(ascending=True)

fig2, ax2 = plt.subplots(figsize=(10, 5))
bars2 = ax2.barh(vendedor_data.index, vendedor_data.values, color='#48CAE4')
ax2.bar_label(bars2, fmt=' R$ %.2f', padding=5)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
st.pyplot(fig2)
