import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração de Layout
st.set_page_config(page_title="BI Bem Leve | Unidades", layout="wide", page_icon="🏢")

@st.cache_data
def carregar_dados_v5():
    for arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            df = pd.read_csv(arq, sep=';', encoding='latin1')
            # Limpeza padrão: maiúsculas e sem espaços extras
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Conversão financeira
            col_v = 'VALOR_LIQUIDO' if 'VALOR_LIQUIDO' in df.columns else 'FATURAMENTO_LIQUIDO'
            if col_v in df.columns:
                df[col_v] = pd.to_numeric(df[col_v], errors='coerce').fillna(0)
            
            # Conversão de Data
            df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
            df = df.dropna(subset=['DATA_NEGOCIACAO'])
            
            return df, col_v
        except:
            continue
    return None, None

df, col_valor = carregar_dados_v5()

if df is not None:
    # --- LÓGICA DE DETECÇÃO DE COLUNAS ---
    # Procurar coluna de Cliente
    col_cliente = next((c for c in df.columns if 'CLIENTE' in c or 'NOME' in c), df.columns[0])
    
    # Procurar coluna de Empresa/Unidade (Pode ser CODEMPRESA, COD_EMPRESA, UNIDADE, etc)
    col_empresa = next((c for c in df.columns if 'COD' in c and 'EMP' in c or 'EMPRESA' in c), None)

    # --- SIDEBAR ---
    st.sidebar.header("🎯 Filtros de Gestão")
    
    # Filtro de Unidade (Só aparece se encontrar a coluna)
    sel_unidades = []
    if col_empresa:
        lista_unidades = sorted(df[col_empresa].astype(str).unique())
        sel_unidades = st.sidebar.multiselect(f"Unidade ({col_empresa}):", options=lista_unidades)
    
    # Filtro de Cliente
    lista_clientes = sorted([str(x) for x in df[col_cliente].unique() if str(x).lower() != 'nan'])
    sel_clientes = st.sidebar.multiselect("Clientes:", options=lista_clientes)
    
    # Filtro de Data
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
    st.title("📊 BI Estratégico - Controle por Unidade")
    
    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Faturamento Total", f"R$ {df_f[col_valor].sum():,.2f}")
    c2.metric("🏢 Qtd. Clientes", len(df_f[col_cliente].unique()))
    c3.metric("📦 Pedidos", len(df_f))

    st.markdown("---")

    # Layout de Gráficos
    g1, g2 = st.columns(2)

    with g1:
        st.subheader("🏆 Top Clientes")
        top_10 = df_f.groupby(col_cliente)[col_valor].sum().sort_values(ascending=True).tail(10).reset_index()
        fig_clientes = px.bar(top_10, x=col_valor, y=col_cliente, orientation='h', 
                             color=col_valor, color_continuous_scale='Viridis')
        st.plotly_chart(fig_clientes, use_container_width=True)

    with g2:
        if col_empresa:
            st.subheader("🏢 Faturamento por Unidade")
            unid_fat = df_f.groupby(col_empresa)[col_valor].sum().reset_index()
            fig_unid = px.pie(unid_fat, values=col_valor, names=col_empresa, hole=0.4)
            st.plotly_chart(fig_unid, use_container_width=True)
        else:
            st.info("Coluna de Unidade/Empresa não encontrada para gerar o gráfico setorial.")

else:
    st.error("Erro ao carregar os dados. Verifique o CSV no GitHub.")
