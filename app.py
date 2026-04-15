import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Configuração da Página
st.set_page_config(page_title="Gestão BEM LEVE - PF vs PJ", layout="wide")

# 1. Carregar Dados
df = pd.read_csv('VENDAS_LIMPAS.csv', sep=';')
df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'])

# --- LÓGICA DE CLASSIFICAÇÃO PF/PJ ---
# Criamos uma coluna nova baseada em palavras-chave comuns de empresas
def classificar_tipo(nome):
    nome = str(nome).upper()
    termos_pj = ['LTDA', 'ME', 'S/A', 'SA', 'LIMITADA', 'CONSTRUTORA', 'SERVICOS', 'EPP', 'MEI']
    if any(termo in nome for termo in termos_pj):
        return 'Pessoa Jurídica (PJ)'
    return 'Pessoa Física (PF)'

df['TIPO_CLIENTE'] = df['CLIENTE'].apply(classificar_tipo)

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.title("🎯 Filtros Estratégicos")

# FILTRO DE TIPO DE PESSOA (O que você pediu)
tipo_filtro = st.sidebar.multiselect(
    "Filtrar por Tipo de Cliente:",
    options=['Pessoa Física (PF)', 'Pessoa Jurídica (PJ)'],
    default=['Pessoa Física (PF)', 'Pessoa Jurídica (PJ)']
)

# Filtro de Data
data_inicio = st.sidebar.date_input("Data Inicial", df['DATA_NEGOCIACAO'].min())
data_fim = st.sidebar.date_input("Data Final", df['DATA_NEGOCIACAO'].max())

# --- APLICAR FILTROS ---
df_f = df[
    (df['TIPO_CLIENTE'].isin(tipo_filtro)) &
    (df['DATA_NEGOCIACAO'].dt.date >= data_inicio) & 
    (df['DATA_NEGOCIACAO'].dt.date <= data_fim)
].copy()

# --- DASHBOARD ---
st.title("📊 BI Especializado - Pessoa Física e Jurídica")

# KPIs de Resumo
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Faturamento Filtrado", f"R$ {df_f['FATURAMENTO_LIQUIDO'].sum():,.2f}")
with c2:
    st.metric("Total de Pedidos", len(df_f))
with c3:
    st.metric("Ticket Médio", f"R$ {df_f['FATURAMENTO_LIQUIDO'].mean():,.2f}")

st.markdown("---")

# --- RANKING DE EMPRESAS/CLIENTES ---
st.subheader("🏢 Ranking de Clientes (Baseado no Filtro)")
cliente_data = df_f.groupby('CLIENTE')['FATURAMENTO_LIQUIDO'].sum().sort_values(ascending=True).tail(10)

if not cliente_data.empty:
    fig, ax = plt.subplots(figsize=(12, 6))
    # Cor azul para PF e Verde para PJ (se houver ambos)
    bars = ax.barh(cliente_data.index, cliente_data.values, color='#0077B6')
    ax.bar_label(bars, fmt=' R$ %.2f', padding=5, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)

# --- RANKING DE VENDEDORES ---
st.subheader("👥 Performance de Vendedores no Segmento")
vend_data = df_f.groupby('VENDEDOR')['FATURAMENTO_LIQUIDO'].sum().sort_values(ascending=True)

fig2, ax2 = plt.subplots(figsize=(10, 5))
bars2 = ax2.barh(vend_data.index, vend_data.values, color='#48CAE4')
ax2.bar_label(bars2, fmt=' R$ %.2f', padding=5)
st.pyplot(fig2)

# Tabela de Conferência
if st.checkbox("Ver lista de vendas filtradas"):
    st.dataframe(df_f[['DATA_NEGOCIACAO', 'CLIENTE', 'TIPO_CLIENTE', 'FATURAMENTO_LIQUIDO']])
