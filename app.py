import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns

# Configuração da Página
st.set_page_config(page_title="Dashboard BEM LEVE", layout="wide")

# CSS para deixar os cards bonitos
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 1. Carregar Dados
df = pd.read_csv('VENDAS_LIMPAS.csv', sep=';')
df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'])

# --- SIDEBAR ---
st.sidebar.title("🛠️ Opções")
data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())
meta = st.sidebar.number_input("Definir Meta (R$)", value=5000)

# Filtragem
df_f = df[(df['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df['DATA_NEGOCIACAO'].dt.date <= data_fim)].copy()

# --- TOPO: INDICADORES ---
st.title("📈 Performance de Vendas")
c1, c2, c3 = st.columns(3)
c1.metric("Faturamento Líquido", f"R$ {df_f['FATURAMENTO_LIQUIDO'].sum():,.20f}".replace(',','v').replace('.',',').replace('v','.'))
c2.metric("Total de Vendas", f"{len(df_f)} pedidos")
c3.metric("Lucro Total", f"R$ {df_f['LUCRO_ESTIMADO'].sum():,.2f}")

st.markdown("---")

# --- RANKING DE VENDEDORES (DESIGN LIMPO) ---
st.subheader("🏆 Ranking de Performance por Vendedor")

# Agrupar e preparar dados
vend_data = df_f.groupby('VENDEDOR')['FATURAMENTO_LIQUIDO'].sum().sort_values(ascending=True)

if not vend_data.empty:
    fig, ax = plt.subplots(figsize=(10, 6))
    # Paleta de cores suave
    colors = ['#A8DADC' if x < meta else '#457B9D' for x in vend_data.values]
    
    bars = ax.barh(vend_data.index, vend_data.values, color=colors, edgecolor='none')
    
    # Estética do gráfico
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#cccccc')
    ax.spines['left'].set_color('#cccccc')
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    # Adicionar linha de meta discreta
    ax.axvline(meta, color='#E63946', linestyle='--', alpha=0.6, label=f"Meta: R${meta}")
    
    # Rótulos de valor nas barras
    ax.bar_label(bars, fmt=' R$ %.2f', padding=8, color='#1D3557', fontweight='bold')
    
    plt.title("Faturamento Acumulado no Período", fontsize=12, pad=20, color='#1D3557')
    st.pyplot(fig)
else:
    st.warning("Nenhum dado encontrado para o período selecionado.")

# --- SEÇÃO INFERIOR ---
st.subheader("📦 Visão de Produtos")
col_p1, col_p2 = st.columns(2)

with col_p1:
    top_prod = df_f.groupby('PRODUTO')['QUANTIDADE'].sum().sort_values(ascending=False).head(5)
    st.write("**Top 5 Produtos (Volume)**")
    st.dataframe(top_prod, use_container_width=True)

with col_p2:
    st.write("**Dica do Especialista**")
    st.info("Os vendedores em azul escuro superaram ou estão próximos da meta definida. Considere bonificações para este grupo!")
