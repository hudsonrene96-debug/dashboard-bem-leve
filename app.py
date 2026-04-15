import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="BI Estratégico BEM LEVE", layout="wide")

# 1. Carregar Dados
def carregar_dados():
    for nome_arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            return pd.read_csv(nome_arq, sep=';')
        except:
            continue
    return None

df = carregar_dados()

if df is None:
    st.error("❌ Arquivo CSV não encontrado no GitHub!")
    st.stop()

# Ajuste de Colunas (Nomes detectados no seu print)
df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')

# --- SIDEBAR ---
st.sidebar.header("🎯 Filtros de Análise")
data_inicio = st.sidebar.date_input("Data Início", df['DATA_NEGOCIACAO'].min())
data_fim = st.sidebar.date_input("Data Fim", df['DATA_NEGOCIACAO'].max())

lista_empresas = sorted(df['CLIENTE'].dropna().unique())
empresas_sel = st.sidebar.multiselect("Filtrar Empresas Específicas:", options=lista_empresas)

# Filtro Lógico
df_f = df.copy()
if data_inicio and data_fim:
    df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df_f['DATA_NEGOCIACAO'].dt.date <= data_fim)]
if empresas_sel:
    df_f = df_f[df_f['CLIENTE'].isin(empresas_sel)]

# --- DASHBOARD ---
if not df_f.empty:
    st.title("📊 Painel de Performance Comercial")
    
    # KPIs SUPERIORES
    c1, c2, c3 = st.columns(3)
    fatur_total = df_f['VALOR_LIQUIDO'].sum()
    vendas_v = df_f.groupby('VENDEDOR')['VALOR_LIQUIDO'].sum()
    melhor_vendedor = vendas_v.idxmax()
    valor_vendedor = vendas_v.max()
    
    c1.metric("💰 Faturamento Total", f"R$ {fatur_total:,.2f}")
    c2.metric("🏆 Melhor Vendedor", melhor_vendedor, f"R$ {valor_vendedor:,.2f}")
    c3.metric("🏢 Melhor Cliente", df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().idxmax())

    st.markdown("---")

    # --- GRÁFICO DE EMPRESAS SEPARADAS ---
    st.subheader("🏢 Faturamento Detalhado por Empresa")
    
    # Agrupamos e pegamos as 15 maiores para não poluir
    fat_emp = df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().sort_values(ascending=True).tail(15)
    
    # Aumentamos a altura proporcionalmente ao número de empresas (0.6 por barra)
    altura_dinamica = max(6, len(fat_emp) * 0.6)
    fig1, ax1 = plt.subplots(figsize=(12, altura_dinamica))
    
    bars1 = ax1.barh(fat_emp.index, fat_emp.values, color='#2A9D8F', edgecolor='white', linewidth=1)
    
    # Adicionar os valores na frente das barras com bom espaçamento
    ax1.bar_label(bars1, fmt=' R$ %.2f', padding=10, fontweight='bold', fontsize=10)
    
    # Limpeza do gráfico para focar no nome da empresa
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['bottom'].set_color('#cccccc')
    ax1.tick_params(axis='y', labelsize=11)
    
    plt.tight_layout()
    st.pyplot(fig1)

    # --- SEÇÃO DE PRODUTOS ---
    st.markdown("---")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🔥 Top 10 Produtos")
        p_v = df_f.groupby('PRODUTO')['QUANTIDADE'].sum().sort_values(ascending=True).tail(10)
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        ax2.barh(p_v.index, p_v.values, color='#457B9D')
        ax2.bar_label(ax2.containers[0], padding=3)
        plt.tight_layout()
        st.pyplot(fig2)
        
    with col_b:
        st.subheader("🧊 5 Menos Vendidos")
        p_m = df_f.groupby('PRODUTO')['QUANTIDADE'].sum().sort_values(ascending=True).head(5)
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        ax3.barh(p_m.index, p_m.values, color='#E76F51')
        ax3.bar_label(ax3.containers[0], padding=3)
        plt.tight_layout()
        st.pyplot(fig3)

else:
    st.warning("⚠️ Selecione um período ou empresa válida nos filtros laterais.")
