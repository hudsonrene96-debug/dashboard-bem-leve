import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração de Página
st.set_page_config(page_title="BI Performance | Bem Leve", layout="wide", page_icon="📈")

@st.cache_data
def carregar_dados_v6():
    for arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            df = pd.read_csv(arq, sep=';', encoding='latin1')
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Conversão financeira
            col_v = 'VALOR_LIQUIDO' if 'VALOR_LIQUIDO' in df.columns else 'FATURAMENTO_LIQUIDO'
            if col_v in df.columns:
                df[col_v] = pd.to_numeric(df[col_v], errors='coerce').fillna(0)
            
            # Conversão de Quantidade (para média de produtos)
            col_q = next((c for c in df.columns if 'QTD' in c or 'QUANT' in c or 'ITENS' in c), None)
            if col_q:
                df[col_q] = pd.to_numeric(df[col_q], errors='coerce').fillna(0)
            
            # Datas
            df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
            df = df.dropna(subset=['DATA_NEGOCIACAO'])
            
            return df, col_v, col_q
        except:
            continue
    return None, None, None

df, col_valor, col_qtd = carregar_dados_v6()

if df is not None:
    # Identificação de Cliente e Unidade
    col_cliente = next((c for c in df.columns if 'CLIENTE' in c or 'NOME' in c), df.columns[0])
    col_empresa = next((c for c in df.columns if 'COD' in c and 'EMP' in c or 'EMPRESA' in c), None)

    # --- SIDEBAR ---
    st.sidebar.header("🎯 Filtros de Gestão")
    
    sel_unidades = []
    if col_empresa:
        lista_unidades = sorted(df[col_empresa].astype(str).unique())
        sel_unidades = st.sidebar.multiselect(f"Unidade ({col_empresa}):", options=lista_unidades)
    
    lista_clientes = sorted([str(x) for x in df[col_cliente].unique() if str(x).lower() != 'nan'])
    sel_clientes = st.sidebar.multiselect("Filtrar Clientes:", options=lista_clientes)
    
    d_ini, d_fim = df['DATA_NEGOCIACAO'].min().date(), df['DATA_NEGOCIACAO'].max().date()
    periodo = st.sidebar.date_input("Período:", [d_ini, d_fim])

    # --- APLICAÇÃO DOS FILTROS ---
    df_f = df.copy()
    if sel_unidades:
        df_f = df_f[df_f[col_empresa].astype(str).isin(sel_unidades)]
    if sel_clientes:
        df_f = df_f[df_f[col_cliente].isin(sel_clientes)]
    if len(periodo) == 2:
        df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= periodo[0]) & (df_f['DATA_NEGOCIACAO'].dt.date <= periodo[1])]

    # --- DASHBOARD ---
    st.title("📈 BI Bem Leve - Performance Comercial")
    
    # --- CÁLCULOS DE MÉTRICAS ---
    total_faturamento = df_f[col_valor].sum()
    total_vendas = len(df_f)
    
    # 1. Ticket Médio (Faturamento / Qtd de Vendas)
    ticket_medio = total_faturamento / total_vendas if total_vendas > 0 else 0
    
    # 2. Média de Itens por Venda (Total Itens / Qtd de Vendas)
    if col_qtd:
        total_itens = df_f[col_qtd].sum()
        media_itens = total_itens / total_vendas if total_vendas > 0 else 0
    else:
        media_itens = 0

    # Exibição dos Cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Faturamento Total", f"R$ {total_faturamento:,.2f}")
    m2.metric("📦 Qtd. Pedidos", f"{total_vendas}")
    m3.metric("💳 Ticket Médio", f"R$ {ticket_medio:,.2f}")
    
    if col_qtd:
        m4.metric("🛍️ Média Itens/Pedido", f"{media_itens:.2f}")
    else:
        m4.metric("🏢 Clientes Ativos", len(df_f[col_cliente].unique()))

    st.markdown("---")

    # Gráficos
    g1, g2 = st.columns(2)

    with g1:
        st.subheader("📊 Ticket Médio por Cliente (Top 10)")
        # Calculando o ticket médio por cliente
        tm_cliente = df_f.groupby(col_cliente).apply(lambda x: x[col_valor].sum() / len(x)).sort_values(ascending=True).tail(10).reset_index()
        tm_cliente.columns = [col_cliente, 'TICKET_MEDIO']
        
        fig_tm = px.bar(tm_cliente, x='TICKET_MEDIO', y=col_cliente, orientation='h',
                        color='TICKET_MEDIO', color_continuous_scale='Tealgrn',
                        labels={'TICKET_MEDIO': 'Ticket Médio (R$)'})
        st.plotly_chart(fig_tm, use_container_width=True)

    with g2:
        st.subheader("📅 Evolução Diária de Vendas")
        evolucao = df_f.groupby(df_f['DATA_NEGOCIACAO'].dt.date)[col_valor].sum().reset_index()
        fig_evol = px.line(evolucao, x='DATA_NEGOCIACAO', y=col_valor, markers=True)
        st.plotly_chart(fig_evol, use_container_width=True)

else:
    st.error("Erro ao carregar dados. Verifique o arquivo CSV.")
