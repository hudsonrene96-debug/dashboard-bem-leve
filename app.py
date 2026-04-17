import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configuração de alta fidelidade
st.set_page_config(page_title="BI Elite | Bem Leve", layout="wide", page_icon="💎")

# CSS para deixar os números bonitos
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #2A9D8F; }
    .stPlotlyChart { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def carregar_dados_blindados():
    for arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            df = pd.read_csv(arq, sep=';', encoding='latin1')
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Conversão financeira ultra-segura
            for col in ['VALOR_LIQUIDO', 'FATURAMENTO_LIQUIDO', 'LUCRO_ESTIMADO']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Datas
            df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
            df = df.dropna(subset=['DATA_NEGOCIACAO'])
            
            return df
        except:
            continue
    return None

df = carregar_dados_blindados()

if df is not None:
    # --- Identificação Automática de Colunas ---
    col_v = 'VALOR_LIQUIDO' if 'VALOR_LIQUIDO' in df.columns else 'FATURAMENTO_LIQUIDO'
    col_c = 'CLIENTE' if 'CLIENTE' in df.columns else df.columns[0]
    col_l = 'LUCRO_ESTIMADO' if 'LUCRO_ESTIMADO' in df.columns else None

    # --- Sidebar Refinada ---
    with st.sidebar:
        st.title("🛡️ Filtros BI")
        # Lista blindada contra TypeError
        lista_clientes = sorted([str(x) for x in df[col_c].unique() if str(x).lower() != 'nan' and str(x) != ''])
        sel_clientes = st.multiselect("Filtrar Clientes:", options=lista_clientes)
        
        data_ini, data_fim = df['DATA_NEGOCIACAO'].min().date(), df['DATA_NEGOCIACAO'].max().date()
        periodo = st.date_input("Período de Análise:", [data_ini, data_fim])

    # Aplicar Filtros
    df_f = df.copy()
    if sel_clientes:
        df_f = df_f[df_f[col_c].isin(sel_clientes)]
    if len(periodo) == 2:
        df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= periodo[0]) & (df_f['DATA_NEGOCIACAO'].dt.date <= periodo[1])]

    # --- DASHBOARD ---
    st.title("🚀 Business Intelligence - Bem Leve")
    
    # KPIs Superiores
    k1, k2, k3, k4 = st.columns(4)
    fat_total = df_f[col_v].sum()
    lucro_total = df_f[col_l].sum() if col_l else 0
    margem = (lucro_total / fat_total * 100) if fat_total > 0 else 0
    
    k1.metric("Faturamento", f"R$ {fat_total:,.2f}")
    if col_l:
        k2.metric("Lucro Estimado", f"R$ {lucro_total:,.2f}")
        k3.metric("Margem Média", f"{margem:.1f}%")
    k4.metric("Qtd. Vendas", len(df_f))

    st.markdown("---")

    # Linha de Gráficos
    g1, g2 = st.columns([2, 1])

    with g1:
        st.subheader("📈 Evolução de Vendas e Lucratividade")
        evolucao = df_f.groupby(df_f['DATA_NEGOCIACAO'].dt.date)[[col_v]].sum().reset_index()
        if col_l:
            evolucao_l = df_f.groupby(df_f['DATA_NEGOCIACAO'].dt.date)[[col_l]].sum().reset_index()
            evolucao = evolucao.merge(evolucao_l)

        fig_evol = go.Figure()
        fig_evol.add_trace(go.Scatter(x=evolucao['DATA_NEGOCIACAO'], y=evolucao[col_v], name="Vendas", fill='tozeroy', line_color='#2A9D8F'))
        if col_l:
            fig_evol.add_trace(go.Scatter(x=evolucao['DATA_NEGOCIACAO'], y=evolucao[col_l], name="Lucro", line_color='#E76F51'))
        
        fig_evol.update_layout(template='plotly_white', height=400, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_evol, use_container_width=True)

    with g2:
        st.subheader("🍕 Mix de Clientes (Top 5)")
        mix = df_f.groupby(col_c)[col_v].sum().sort_values(ascending=False).head(5).reset_index()
        fig_pie = px.pie(mix, values=col_v, names=col_c, hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Ranking Final
    st.subheader("🏆 Ranking Geral de Empresas")
    ranking = df_f.groupby(col_c)[col_v].sum().sort_values(ascending=True).tail(15).reset_index()
    fig_rank = px.bar(ranking, x=col_v, y=col_c, orientation='h', text_auto='.2s', color=col_v, color_continuous_scale='GnBu')
    fig_rank.update_layout(template='plotly_white', height=500)
    st.plotly_chart(fig_rank, use_container_width=True)

else:
    st.error("Erro ao processar a base de dados.")
