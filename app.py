import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da página para um visual mais profissional
st.set_page_config(page_title="BI Estratégico | Bem Leve", layout="wide", page_icon="📊")

# --- CSS Personalizado para Cards ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 24px; color: #2A9D8F; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def carregar_dados_v2():
    for arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            df = pd.read_csv(arq, sep=';', encoding='latin1')
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Identificação automática de colunas de valor e cliente
            col_v = 'VALOR_LIQUIDO' if 'VALOR_LIQUIDO' in df.columns else 'FATURAMENTO_LIQUIDO'
            col_c = 'CLIENTE' if 'CLIENTE' in df.columns else df.columns[0]
            
            df[col_v] = pd.to_numeric(df[col_v], errors='coerce').fillna(0)
            df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
            df[col_c] = df[col_c].astype(str).replace('nan', 'Indefinido')
            
            return df.dropna(subset=['DATA_NEGOCIACAO']), col_v, col_c
        except:
            continue
    return None, None, None

df, col_vendas, col_cliente = carregar_dados_v2()

if df is not None:
    # --- BARRA LATERAL ---
    with st.sidebar:
        st.title("🛡️ Filtros")
        
        # Filtro de Data Dinâmico
        data_min, data_max = df['DATA_NEGOCIACAO'].min().date(), df['DATA_NEGOCIACAO'].max().date()
        datas = st.date_input("Selecione o Período", [data_min, data_max])
        
        # Filtro de Cliente com Busca
        lista_clientes = sorted(df[col_cliente].unique())
        clientes_sel = st.multiselect("Filtrar Clientes:", options=lista_clientes)

    # Aplicação dos Filtros
    df_f = df.copy()
    if clientes_sel:
        df_f = df_f[df_f[col_cliente].isin(clientes_sel)]
    if len(datas) == 2:
        df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= datas[0]) & (df_f['DATA_NEGOCIACAO'].dt.date <= datas[1])]

    # --- DASHBOARD ---
    st.title("🚀 Business Intelligence - Bem Leve")
    
    # 1. LINHA DE MÉTRICAS (KPIs)
    m1, m2, m3, m4 = st.columns(4)
    fat_total = df_f[col_vendas].sum()
    ticket_med = fat_total / len(df_f) if len(df_f) > 0 else 0
    
    m1.metric("Faturamento Total", f"R$ {fat_total:,.2f}")
    m2.metric("Nº de Vendas", f"{len(df_f)}")
    m3.metric("Ticket Médio", f"R$ {ticket_med:,.2f}")
    m4.metric("Qtd. Clientes Ativos", f"{len(df_f[col_cliente].unique())}")

    st.markdown("---")

    # 2. LINHA DE GRÁFICOS
    g1, g2 = st.columns(2)

    with g1:
        st.subheader("🏢 Top 10 Clientes")
        top_10 = df_f.groupby(col_cliente)[col_vendas].sum().sort_values(ascending=True).tail(10).reset_index()
        fig_bar = px.bar(top_10, x=col_vendas, y=col_cliente, orientation='h',
                         color=col_vendas, color_continuous_scale='Viridis',
                         labels={col_vendas: 'Faturamento (R$)', col_cliente: 'Empresa'})
        fig_bar.update_layout(showlegend=False, height=400, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    with g2:
        st.subheader("📈 Tendência Diária")
        vendas_dia = df_f.groupby(df_f['DATA_NEGOCIACAO'].dt.date)[col_vendas].sum().reset_index()
        fig_line = px.line(vendas_dia, x='DATA_NEGOCIACAO', y=col_vendas,
                           labels={'DATA_NEGOCIACAO': 'Data', col_vendas: 'Total (R$)'})
        fig_line.update_traces(line_color='#2A9D8F', line_width=3)
        fig_line.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_line, use_container_width=True)

    # 3. DETALHAMENTO
    with st.expander("🔍 Ver Detalhamento dos Dados"):
        st.dataframe(df_f[[col_cliente, 'DATA_NEGOCIACAO', col_vendas]].sort_values('DATA_NEGOCIACAO', ascending=False), use_container_width=True)

else:
    st.error("Erro ao carregar os dados. Verifique o arquivo CSV no seu GitHub.")
