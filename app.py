import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="BI Gestão Estratégica", layout="wide")

# 1. Função para carregar dados
def carregar_dados():
    # Tenta os nomes possíveis do arquivo que você subiu
    for nome_arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            return pd.read_csv(nome_arq, sep=';')
        except:
            continue
    return None

df = carregar_dados()

if df is None:
    st.error("❌ Arquivo CSV não encontrado. Verifique o nome no GitHub!")
    st.stop()

# Ajuste exato das colunas baseado no seu print
# Nomes detectados: DATA_NEGOCIACAO, VENDEDOR, CLIENTE, VALOR_LIQUIDO, QUANTIDADE, PRODUTO
df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')

# --- SIDEBAR ---
st.sidebar.header("🎯 Filtros")
data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())

lista_empresas = sorted(df['CLIENTE'].dropna().unique())
empresas_sel = st.sidebar.multiselect("Selecionar Empresas:", options=lista_empresas)

# Aplicar Filtros
df_f = df.copy()
if data_inicio and data_fim:
    df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df_f['DATA_NEGOCIACAO'].dt.date <= data_fim)]
if empresas_sel:
    df_f = df_f[df_f['CLIENTE'].isin(empresas_sel)]

# --- DASHBOARD ---
if not df_f.empty:
    st.title("📊 Painel de Performance Comercial")
    
    # KPIs principais
    c1, c2, c3 = st.columns(3)
    fatur_total = df_f['VALOR_LIQUIDO'].sum()
    vendas_v = df_f.groupby('VENDEDOR')['VALOR_LIQUIDO'].sum()
    
    c1.metric("💰 Faturamento Total", f"R$ {fatur_total:,.2f}")
    c2.metric("🏆 Melhor Vendedor", vendas_v.idxmax(), f"R$ {vendas_v.max():,.2f}")
    c3.metric("🏢 Melhor Cliente", df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().idxmax())

    st.markdown("---")

    # Gráfico 1: Faturamento por Empresa Separadamente
    st.subheader("🏢 Faturamento por Empresa")
    fat_emp = df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().sort_values(ascending=True).tail(15)
    
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    bars1 = ax1.barh(fat_emp.index, fat_emp.values, color='#2A9D8F')
    ax1.bar_label(bars1, fmt=' R$ %.2f', padding=5, fontweight='bold')
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig1)

    # Gráfico 2: Produtos
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🔥 Top 10 Produtos (Mais Vendidos)")
        p_v = df_f.groupby('PRODUTO')['QUANTIDADE'].sum().sort_values(ascending=True).tail(10)
        fig2, ax2 = plt.subplots()
        ax2.barh(p_v.index, p_v.values, color='#457B9D')
        ax2.bar_label(ax2.containers[0], padding=3)
        st.pyplot(fig2)
    with col_b:
        st.subheader("🧊 5 Produtos Menos Vendidos")
        p_m = df_f.groupby('PRODUTO')['QUANTIDADE'].sum().sort_values(ascending=True).head(5)
        fig3, ax3 = plt.subplots()
        ax3.barh(p_m.index, p_m.values, color='#E76F51')
        ax3.bar_label(ax3.containers[0], padding=3)
        st.pyplot(fig3)
else:
    st.warning("Ajuste os filtros ou selecione uma empresa para ver os dados.")
