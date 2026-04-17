import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração de Página
st.set_page_config(page_title="BI Performance Max | Bem Leve", layout="wide", page_icon="🏆")

@st.cache_data
def carregar_dados_v7():
    for arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            df = pd.read_csv(arq, sep=';', encoding='latin1')
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Conversão financeira
            col_v = 'VALOR_LIQUIDO' if 'VALOR_LIQUIDO' in df.columns else 'FATURAMENTO_LIQUIDO'
            if col_v in df.columns:
                df[col_v] = pd.to_numeric(df[col_v], errors='coerce').fillna(0)
            
            # Conversão de Quantidade
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

df, col_valor, col_qtd = carregar_dados_v7()

if df is not None:
    # --- DETECÇÃO AUTOMÁTICA DE NOVAS COLUNAS ---
    col_cliente = next((c for c in df.columns if 'CLIENTE' in c or 'NOME' in c), df.columns[0])
    col_empresa = next((c for c in df.columns if 'COD' in c and 'EMP' in c or 'EMPRESA' in c), None)
    col_vendedor = next((c for c in df.columns if 'VENDEDOR' in c or 'REPRESENTANTE' in c), None)
    col_produto = next((c for c in df.columns if 'PRODUTO' in c or 'DESCRICAO' in c or 'ITEM' in c), None)

    # --- SIDEBAR ---
    st.sidebar.header("🎯 Filtros de Gestão")
    
    sel_unidades = []
    if col_empresa:
        lista_unidades = sorted(df[col_empresa].astype(str).unique())
        sel_unidades = st.sidebar.multiselect(f"Unidade ({col_empresa}):", options=lista_unidades)
    
    if col_vendedor:
        vendedores = sorted(df[col_vendedor].astype(str).unique())
        sel_vendedores = st.sidebar.multiselect("Filtrar Vendedora:", options=vendedores)
    
    d_ini, d_fim = df['DATA_NEGOCIACAO'].min().date(), df['DATA_NEGOCIACAO'].max().date()
    periodo = st.sidebar.date_input("Período:", [d_ini, d_fim])

    # --- APLICAÇÃO DOS FILTROS ---
    df_f = df.copy()
    if sel_unidades:
        df_f = df_f[df_f[col_empresa].astype(str).isin(sel_unidades)]
    if col_vendedor and sel_vendedores:
        df_f = df_f[df_f[col_vendedor].astype(str).isin(sel_vendedores)]
    if len(periodo) == 2:
        df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= periodo[0]) & (df_f['DATA_NEGOCIACAO'].dt.date <= periodo[1])]

    # --- DASHBOARD ---
    st.title("🏆 BI Bem Leve - Performance Max")
    
    # Cálculos Principais
    total_faturamento = df_f[col_valor].sum()
    total_vendas = len(df_f)
    ticket_medio = total_faturamento / total_vendas if total_vendas > 0 else 0
    
    # 1. MELHOR VENDEDORA
    if col_vendedor:
        venda_por_vendedor = df_f.groupby(col_vendedor)[col_valor].sum().sort_values(ascending=False)
        melhor_vendedora = venda_por_vendedor.index[0] if not venda_por_vendedor.empty else "N/A"
    else:
        melhor_vendedora = "Coluna não encontrada"

    # Cards de Resumo
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Faturamento Total", f"R$ {total_faturamento:,.2f}")
    m2.metric("💳 Ticket Médio", f"R$ {ticket_medio:,.2f}")
    m3.metric("🥇 Melhor Vendedora", melhor_vendedora)
    
    if col_qtd:
        media_itens = df_f[col_qtd].sum() / total_vendas if total_vendas > 0 else 0
        m4.metric("🛍️ Média Itens/Pedido", f"{media_itens:.2f}")
    else:
        m4.metric("📦 Qtd. Pedidos", f"{total_vendas}")

    st.markdown("---")

    # --- LINHA 1 DE GRÁFICOS (Rankings) ---
    g1, g2 = st.columns(2)

    with g1:
        st.subheader("📊 Faturamento por Vendedor")
        if col_vendedor:
            fat_vend = df_f.groupby(col_vendedor)[col_valor].sum().sort_values(ascending=True).tail(10).reset_index()
            fig_vend = px.bar(fat_vend, x=col_valor, y=col_vendedor, orientation='h', 
                             color=col_valor, color_continuous_scale='Blues', text_auto='.2s')
            st.plotly_chart(fig_vend, use_container_width=True)
        else:
            st.info("Coluna de Vendedor não encontrada.")

    with g2:
        st.subheader("📦 Top 10 Produtos Mais Vendidos")
        if col_produto:
            # Ranking por faturamento ou por quantidade (se existir)
            col_rank = col_qtd if col_qtd else col_valor
            top_prod = df_f.groupby(col_produto)[col_rank].sum().sort_values(ascending=True).tail(10).reset_index()
            fig_prod = px.bar(top_prod, x=col_rank, y=col_produto, orientation='h',
                             color=col_rank, color_continuous_scale='Reds', text_auto='.2s')
            st.plotly_chart(fig_prod, use_container_width=True)
        else:
            st.info("Coluna de Produto não encontrada.")

    # --- LINHA 2 DE GRÁFICOS (Evolução e Unidades) ---
    st.markdown("---")
    g3, g4 = st.columns(2)

    with g3:
        st.subheader("🏆 Melhores Clientes")
        top_c = df_f.groupby(col_cliente)[col_valor].sum().sort_values(ascending=True).tail(10).reset_index()
        fig_cli = px.bar(top_c, x=col_valor, y=col_cliente, orientation='h', color_continuous_scale='Viridis')
        st.plotly_chart(fig_cli, use_container_width=True)

    with g4:
        st.subheader("📅 Evolução Diária")
        evolucao = df_f.groupby(df_f['DATA_NEGOCIACAO'].dt.date)[col_valor].sum().reset_index()
        fig_line = px.line(evolucao, x='DATA_NEGOCIACAO', y=col_valor, markers=True)
        st.plotly_chart(fig_line, use_container_width=True)

else:
    st.error("Erro ao carregar dados.")
