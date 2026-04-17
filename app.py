import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# Configuração de Página Elite
st.set_page_config(page_title="BI Elite | Bem Leve", layout="wide", page_icon="📈")

@st.cache_data
def carregar_dados_v3():
    for arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            df = pd.read_csv(arq, sep=';', encoding='latin1')
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Conversão de Valores Financeiros
            for col in ['VALOR_LIQUIDO', 'FATURAMENTO_LIQUIDO', 'LUCRO_ESTIMADO']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Ajuste de Datas
            df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
            df = df.dropna(subset=['DATA_NEGOCIACAO'])
            
            # Identificação de Colunas Chave
            col_v = 'VALOR_LIQUIDO' if 'VALOR_LIQUIDO' in df.columns else 'FATURAMENTO_LIQUIDO'
            col_c = 'CLIENTE' if 'CLIENTE' in df.columns else df.columns[0]
            col_l = 'LUCRO_ESTIMADO' if 'LUCRO_ESTIMADO' in df.columns else None
            
            df[col_c] = df[col_c].astype(str).replace('nan', 'Indefinido')
            return df, col_v, col_c, col_l
        except:
            continue
    return None, None, None, None

df, col_v, col_c, col_l = carregar_dados_v3()

if df is not None:
    # --- BARRA LATERAL (filtros inteligentes) ---
    with st.sidebar:
        st.header("📊 Filtros Avançados")
        
        # Filtro de Data
        data_min, data_max = df['DATA_NEGOCIACAO'].min().date(), df['DATA_NEGOCIACAO'].max().date()
        datas = st.date_input("Período", [data_min, data_max])
        
        # Filtro de Cliente
        clientes = sorted(df[col_c].unique())
        sel_clientes = st.multiselect("Clientes Específicos", options=clientes)

    # Aplicação de Filtros
    df_f = df.copy()
    if sel_clientes:
        df_f = df_f[df_f[col_c].isin(sel_clientes)]
    if len(datas) == 2:
        df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= datas[0]) & (df_f['DATA_NEGOCIACAO'].dt.date <= datas[1])]

    # --- DASHBOARD ---
    st.title("📈 BI Elite - Performance Comercial")
    
    # KPIs Modernos
    k1, k2, k3, k4 = st.columns(4)
    fat_total = df_f[col_v].sum()
    lucro_total = df_f[col_l].sum() if col_l else 0
    margem = (lucro_total / fat_total * 100) if fat_total > 0 else 0

    k1.metric("Faturamento", f"R$ {fat_total:,.2f}")
    if col_l:
        k2.metric("Lucro Estimado", f"R$ {lucro_total:,.2f}")
        k3.metric("Margem Média", f"{margem:.1f}%")
    k4.metric("Nº de Vendas", len(df_f))

    st.markdown("---")

    # LINHA 1: Tendência e Mix
    g1, g2 = st.columns([2, 1])

    with g1:
        st.subheader("📅 Evolução Diária (Venda vs Lucro)")
        # Agrupamento diário
        daily = df_f.groupby(df_f['DATA_NEGOCIACAO'].dt.date)[[col_v]].sum().reset_index()
        if col_l:
            daily_l = df_f.groupby(df_f['DATA_NEGOCIACAO'].dt.date)[[col_l]].sum().reset_index()
            daily = daily.merge(daily_l)

        fig_evol = go.Figure()
        fig_evol.add_trace(go.Scatter(x=daily['DATA_NEGOCIACAO'], y=daily[col_v], name="Vendas", fill='tozeroy', line_color='#2A9D8F'))
        if col_l:
            fig_evol.add_trace(go.Scatter(x=daily['DATA_NEGOCIACAO'], y=daily[col_l], name="Lucro", line_color='#E76F51'))
        
        fig_evol.update_layout(template='plotly_white', height=400, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_evol, use_container_width=True)

    with g2:
        st.subheader("🍕 Market Share Interno")
        share = df_f.groupby(col_c)[col_v].sum().sort_values(ascending=False).head(5).reset_index()
        fig_pie = px.pie(share, values=col_v, names=col_c, hole=0.5, color_discrete_sequence=px.colors.qualitative.T10)
        fig_pie.update_layout(height=400, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    # LINHA 2: Ranking
    st.markdown("---")
    st.subheader("🏆 Ranking de Clientes (Top 20)")
    ranking = df_f.groupby(col_c)[col_v].sum().sort_values(ascending=True).tail(20).reset_index()
    fig_rank = px.bar(ranking, x=col_v, y=col_c, orientation='h', 
                      color=col_v, color_continuous_scale='GnBu', 
                      text_auto='.2s')
    fig_rank.update_layout(template='plotly_white', height=600)
    st.plotly_chart(fig_rank, use_container_width=True)

    # TABELA FINAL
    with st.expander("📄 Base de Dados Completa"):
        st.dataframe(df_f.sort_values('DATA_NEGOCIACAO', ascending=False), use_container_width=True)

else:
    st.error("Erro crítico: Verifique os nomes das colunas no seu CSV.")
