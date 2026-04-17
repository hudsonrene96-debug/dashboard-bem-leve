import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# Configuração de alta performance
st.set_page_config(page_title="BI Intelligence | Bem Leve", layout="wide", page_icon="💡")

@st.cache_data
def carregar_dados_inteligentes():
    for arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            df = pd.read_csv(arq, sep=';', encoding='latin1')
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Conversão financeira
            for col in ['VALOR_LIQUIDO', 'FATURAMENTO_LIQUIDO', 'LUCRO_ESTIMADO']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Datas e Sazonalidade
            df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
            df = df.dropna(subset=['DATA_NEGOCIACAO'])
            
            # Adicionando inteligência de tempo
            df['DIA_SEMANA'] = df['DATA_NEGOCIACAO'].dt.day_name()
            df['MES'] = df['DATA_NEGOCIACAO'].dt.month_name()
            
            return df
        except:
            continue
    return None

df = carregar_dados_inteligentes()

if df is not None:
    # Identificação de colunas
    col_v = 'VALOR_LIQUIDO' if 'VALOR_LIQUIDO' in df.columns else 'FATURAMENTO_LIQUIDO'
    col_c = 'CLIENTE' if 'CLIENTE' in df.columns else df.columns[0]
    col_l = 'LUCRO_ESTIMADO' if 'LUCRO_ESTIMADO' in df.columns else None

    # --- SIDEBAR COM INTELIGÊNCIA ---
    with st.sidebar:
        st.title("🧠 Inteligência de Filtros")
        
        # Filtro de Clientes (Blindado)
        lista_clientes = sorted([str(x) for x in df[col_c].unique() if str(x).lower() != 'nan'])
        sel_clientes = st.multiselect("Filtrar Clientes:", options=lista_clientes)
        
        # Filtro de Valor (Slider)
        valor_min = float(df[col_v].min())
        valor_max = float(df[col_v].max())
        faixa_preco = st.slider("Filtrar por Valor da Venda (R$)", valor_min, valor_max, (valor_min, valor_max))

    # Aplicação de Filtros
    df_f = df.copy()
    if sel_clientes:
        df_f = df_f[df_f[col_c].isin(sel_clientes)]
    df_f = df_f[(df_f[col_v] >= faixa_preco[0]) & (df_f[col_v] <= faixa_preco[1])]

    # --- DASHBOARD ---
    st.title("💡 BI Intelligence - Bem Leve")
    
    # KPIs principais
    k1, k2, k3, k4 = st.columns(4)
    fat_total = df_f[col_v].sum()
    lucro_total = df_f[col_l].sum() if col_l else 0
    margem = (lucro_total / fat_total * 100) if fat_total > 0 else 0

    k1.metric("Faturamento", f"R$ {fat_total:,.2f}")
    k2.metric("Qtd. Pedidos", len(df_f))
    k3.metric("Ticket Médio", f"R$ {fat_total/len(df_f) if len(df_f)>0 else 0:,.2f}")
    k4.metric("Margem Real", f"{margem:.1f}%")

    st.markdown("---")

    # LINHA 1: Evolução e Lucratividade (Gráfico de Área)
    st.subheader("📊 Performance de Vendas vs Lucro")
    evolucao = df_f.groupby(df_f['DATA_NEGOCIACAO'].dt.date)[[col_v]].sum().reset_index()
    if col_l:
        evol_l = df_f.groupby(df_f['DATA_NEGOCIACAO'].dt.date)[[col_l]].sum().reset_index()
        evolucao = evolucao.merge(evol_l)

    fig_evol = go.Figure()
    fig_evol.add_trace(go.Scatter(x=evolucao['DATA_NEGOCIACAO'], y=evolucao[col_v], name="Venda", fill='tozeroy', line_color='#2A9D8F'))
    if col_l:
        fig_evol.add_trace(go.Scatter(x=evolucao['DATA_NEGOCIACAO'], y=evolucao[col_l], name="Lucro", line_color='#E76F51'))
    st.plotly_chart(fig_evol, use_container_width=True)

    # LINHA 2: Sazonalidade e Market Share
    c_esq, c_dir = st.columns(2)

    with c_esq:
        st.subheader("📅 Vendas por Dia da Semana")
        ordem_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        vendas_dia = df_f.groupby('DIA_SEMANA')[col_v].sum().reindex(ordem_dias).reset_index()
        fig_dia = px.bar(vendas_dia, x='DIA_SEMANA', y=col_v, color=col_v, color_continuous_scale='Mint')
        st.plotly_chart(fig_dia, use_container_width=True)

    with c_dir:
        st.subheader("🥧 Concentração de Faturamento")
        pizza = df_f.groupby(col_c)[col_v].sum().sort_values(ascending=False).head(8).reset_index()
        fig_pizza = px.pie(pizza, values=col_v, names=col_c, hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_pizza, use_container_width=True)

    # Tabela detalhada
    with st.expander("🔍 Explorar Detalhes"):
        st.write(df_f.sort_values(col_v, ascending=False))

else:
    st.error("Erro ao carregar dados.")
