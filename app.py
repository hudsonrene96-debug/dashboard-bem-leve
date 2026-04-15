import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Configuração da Página
st.set_page_config(page_title="BI Gestão Estratégica", layout="wide")

# 1. Carregar Dados
# AJUSTE IMPORTANTE: Verifique se o nome no GitHub é exatamente este:
try:
    df = pd.read_csv('VENDAS_LIMPAS.csv', sep=';')
except FileNotFoundError:
    # Caso você tenha renomeado para outro nome, ele tentará carregar o original
    df = pd.read_csv('VENDAS_CONVERTIDO.csv', sep=';')

df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'])

# --- SIDEBAR (FILTROS) ---
st.sidebar.header("🎯 Filtros de Análise")
data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())

# Filtro de Empresa
lista_empresas = sorted(df['CLIENTE'].unique())
empresas_selecionadas = st.sidebar.multiselect("Selecionar Empresas:", options=lista_empresas, default=None)

# Aplicar Filtros
df_f = df[(df['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df['DATA_NEGOCIACAO'].dt.date <= data_fim)].copy()

if empresas_selecionadas:
    df_f = df_f[df_f['CLIENTE'].isin(empresas_selecionadas)]

# --- CÁLCULOS ---
if not df_f.empty:
    faturamento_total = df_f['FATURAMENTO_LIQUIDO'].sum()
    melhor_cliente = df_f.groupby('CLIENTE')['FATURAMENTO_LIQUIDO'].sum().idxmax()
    
    # Melhor vendedor baseado no faturamento filtrado
    vendas_vendedor = df_f.groupby('VENDEDOR')['FATURAMENTO_LIQUIDO'].sum()
    melhor_vendedor = vendas_vendedor.idxmax()
    valor_vendedor = vendas_vendedor.max()

    # --- LAYOUT SUPERIOR ---
    st.title("📊 Painel de Performance Comercial")
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Faturamento Selecionado", f"R$ {faturamento_total:,.2f}")
    c2.metric("🏆 Melhor Vendedor", melhor_vendedor, f"R$ {valor_vendedor:,.2f}")
    c3.metric("🏢 Melhor Cliente", melhor_cliente)

    st.markdown("---")

    # --- GRÁFICO 1: FATURAMENTO POR EMPRESA ---
    st.subheader("🏢 Faturamento Detalhado por Empresa")
    faturamento_empresa = df_f.groupby('CLIENTE')['FATURAMENTO_LIQUIDO'].sum().sort_values(ascending=True).tail(15)
    
    # Ajuste dinâmico da altura para não cortar nomes
    altura = max(5, len(faturamento_empresa) * 0.4)
    fig1, ax1 = plt.subplots(figsize=(10, altura))
    bars1 = ax1.barh(faturamento_empresa.index, faturamento_empresa.values, color='#2A9D8F')
    ax1.bar_label(bars1, fmt=' R$ %.2f', padding=5, fontweight='bold')
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig1)

    # --- GRÁFICO 2: PRODUTOS ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Top 10 Produtos (Mais Vendidos)")
        mais_v = df_f.groupby('PRODUTO')['QUANTIDADE'].sum().sort_values(ascending=True).tail(10)
        fig2, ax2 = plt.subplots()
        ax2.barh(mais_v.index, mais_v.values, color='#457B9D')
        ax2.bar_label(ax2.containers[0], padding=3)
        plt.tight_layout()
        st.pyplot(fig2)

    with col2:
        st.subheader("🧊 5 Produtos Menos Vendidos")
        menos_v = df_f.groupby('PRODUTO')['QUANTIDADE'].sum().sort_values(ascending=True).head(5)
        fig3, ax3 = plt.subplots()
        ax3.barh(menos_v.index, menos_v.values, color='#E76F51')
        ax3.bar_label(ax3.containers[0], padding=3)
        plt.tight_layout()
        st.pyplot(fig3)

else:
    st.warning("Nenhum dado encontrado para o filtro selecionado.")
