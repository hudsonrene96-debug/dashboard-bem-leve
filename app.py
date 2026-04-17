import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Configuração com versão para conferência
st.set_page_config(page_title="BI Bem Leve v2.0", layout="wide")

# 2. CARGA BLINDADA (Mudamos o nome da função para limpar o cache do servidor)
@st.cache_data
def carregar_dados_definitivo_v2():
    arquivos = ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']
    df = None
    for arq in arquivos:
        try:
            df = pd.read_csv(arq, sep=';', encoding='latin1')
            # Limpeza radical de nomes de colunas
            df.columns = [str(c).strip().upper() for c in df.columns]
            break
        except:
            continue
    
    if df is not None:
        # Força conversão de tipos
        col_v = 'VALOR_LIQUIDO' if 'VALOR_LIQUIDO' in df.columns else 'FATURAMENTO_LIQUIDO'
        if col_v in df.columns:
            df[col_v] = pd.to_numeric(df[col_v], errors='coerce').fillna(0)
        
        df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
        df = df.dropna(subset=['DATA_NEGOCIACAO'])
        
        # Identifica coluna de cliente
        col_c = 'CLIENTE' if 'CLIENTE' in df.columns else df.columns[0]
        # Transforma tudo em String para evitar o erro de 'float vs str'
        df[col_c] = df[col_c].astype(str).replace('nan', 'NÃO INFORMADO')
        
        return df, col_v, col_c
    return None, None, None

df, col_valor, col_cliente = carregar_dados_definitivo_v2()

if df is not None:
    # --- PREPARAÇÃO DA LISTA DE FILTRO (SEM ERRO DE TIPO) ---
    # Pegamos os nomes, garantimos que são strings e ordenamos
    nomes_clientes = sorted([str(x) for x in df[col_cliente].unique() if str(x).lower() != 'nan'])

    # --- SIDEBAR ---
    st.sidebar.header("🎯 Filtros")
    sel_clientes = st.sidebar.multiselect("Empresas:", options=nomes_clientes)
    
    # Datas
    d_ini = df['DATA_NEGOCIACAO'].min().date()
    d_fim = df['DATA_NEGOCIACAO'].max().date()
    periodo = st.sidebar.date_input("Período:", [d_ini, d_fim])

    # --- FILTRAGEM ---
    df_f = df.copy()
    if sel_clientes:
        df_f = df_f[df_f[col_cliente].isin(sel_clientes)]
    
    if len(periodo) == 2:
        df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= periodo[0]) & 
                    (df_f['DATA_NEGOCIACAO'].dt.date <= periodo[1])]

    # --- DASHBOARD ---
    st.title("📊 BI Estratégico - Bem Leve (v2.0)")
    
    if not df_f.empty:
        c1, c2 = st.columns(2)
        c1.metric("💰 Total Faturado", f"R$ {df_f[col_valor].sum():,.2f}")
        c2.metric("🏢 Clientes Ativos", len(df_f[col_cliente].unique()))

        st.markdown("---")
        
        # Gráfico Plotly (Interativo)
        st.subheader("🏆 Top 10 Clientes")
        top_10 = df_f.groupby(col_cliente)[col_valor].sum().sort_values(ascending=True).tail(10).reset_index()
        fig = px.bar(top_10, x=col_valor, y=col_cliente, orientation='h', 
                     color=col_valor, color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Ajuste os filtros.")
else:
    st.error("Arquivo não encontrado no GitHub.")
