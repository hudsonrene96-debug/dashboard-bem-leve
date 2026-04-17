import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta

# Configuração de Layout
st.set_page_config(page_title="Executive Dashboard", layout="wide", page_icon="💎")

# CSS para melhorar o visual
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    div[data-testid="stMetric"] { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def carregar_dados_elite():
    for arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            df = pd.read_csv(arq, sep=';', encoding='latin1')
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Dinheiro
            col_v = 'VALOR_LIQUIDO' if 'VALOR_LIQUIDO' in df.columns else 'FATURAMENTO_LIQUIDO'
            df[col_v] = pd.to_numeric(df[col_v], errors='coerce').fillna(0)
            
            # Datas
            df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
            df = df.dropna(subset=['DATA_NEGOCIACAO'])
            
            # Strings
            col_c = 'CLIENTE' if 'CLIENTE' in df.columns else 'NOME'
            df[col_c] = df[col_c].astype(str).replace('nan', 'Indefinido')
            
            return df, col_v, col_c
        except:
            continue
    return None, None, None

df, col_v, col_c = carregar_dados_elite()

if df is not None:
    # --- BARRA LATERAL ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3222/3222800.png", width=80)
        st.title("Menu de Filtros")
        
        # Filtros Rápidos
        st.subheader("Período")
        hoje = datetime.now()
        filtro_data = st.selectbox("Atalhos de Data:", ["Todo o Período", "Este Mês", "Últimos 30 dias", "Últimos 90 dias"])
        
        if filtro_data == "Este Mês":
            d_ini = hoje.replace(day=1).date()
            d_fim = hoje.date()
        elif filtro_data == "Últimos 30 dias":
            d_ini = (hoje - timedelta(days=30)).date()
            d_fim = hoje.date()
        else:
            d_ini, d_fim = df['DATA_NEGOCIACAO'].min().date(), df['DATA_NEGOCIACAO'].max().date()
            
        datas = st.date_input("Intervalo Manual:", [d_ini, d_fim])
        
        st.subheader("Clientes")
        clientes_sel = st.multiselect("Selecionar Clientes:", options=sorted(df[col_c].unique()))

    # Aplicar Filtros
    df_f = df.copy()
    if clientes_sel:
        df_f = df_f[df_f[col_c].isin(clientes_sel)]
    if len(datas) == 2:
        df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= datas[0]) & (df_f['DATA_NEGOCIACAO'].dt.date <= datas[1])]

    # --- CORPO DO DASHBOARD ---
    st.title("💎 BI Executive Analytics")
    
    # KPIs principais
    c1, c2, c3, c4 = st.columns(4)
    fat_total = df_f[col_v].sum()
    c1.metric("Faturamento Líquido", f"R$ {fat_total:,.2f}")
    c2.metric("Qtd. Transações", f"{len(df_f)}")
    c3.metric("Ticket Médio", f"R$ {fat_total/len(df_f) if len(df_f)>0 else 0:,.2f}")
    c4.metric("Clientes no Período", f"{len(df_f[col_c].unique())}")

    st.markdown("---")

    # Gráficos Superiores
    g1, g2 = st.columns([2, 1])

    with g1:
        st.subheader("📈 Evolução de Receita Diária")
        vendas_dia = df_f.groupby(df_f['DATA_NEGOCIACAO'].dt.date)[col_v].sum().reset_index()
        fig_evolucao = px.area(vendas_dia, x='DATA_NEGOCIACAO', y=col_v, 
                              color_discrete_sequence=['#2A9D8F'], 
                              title="Tendência de Receita")
        st.plotly_chart(fig_evolucao, use_container_width=True)

    with g2:
        st.subheader("🍰 Share de Clientes")
        share = df_f.groupby(col_c)[col_v].sum().sort_values(ascending=False).head(5).reset_index()
        fig_pizza = px.pie(share, values=col_v, names=col_c, hole=0.4,
                           color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pizza, use_container_width=True)

    # Gráficos Inferiores
    st.subheader("🏆 Top 15 Clientes por Valor")
    top_c = df_f.groupby(col_c)[col_v].sum().sort_values(ascending=True).tail(15).reset_index()
    fig_bar = px.bar(top_c, x=col_v, y=col_c, text_auto='.2s',
                     color=col_v, color_continuous_scale='Teal')
    st.plotly_chart(fig_bar, use_container_width=True)

    # Tabela com Estilo
    with st.expander("📂 Explorar Base de Dados"):
        st.dataframe(df_f.style.format({col_v: 'R$ {:,.2f}'}), use_container_width=True)

else:
    st.error("Erro crítico ao carregar dados.")
