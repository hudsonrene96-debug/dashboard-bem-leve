import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configuração de alta performance
st.set_page_config(page_title="BI Elite | Bem Leve", layout="wide", page_icon="📈")

@st.cache_data
def carregar_dados_v4():
    for arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            df = pd.read_csv(arq, sep=';', encoding='latin1')
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Conversão financeira
            for col in ['VALOR_LIQUIDO', 'FATURAMENTO_LIQUIDO', 'LUCRO_ESTIMADO']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Ajuste de Datas
            df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
            df = df.dropna(subset=['DATA_NEGOCIACAO'])
            
            return df
        except:
            continue
    return None

df = carregar_dados_v4()

if df is not None:
    # Identificação Automática de Colunas
    col_v = 'VALOR_LIQUIDO' if 'VALOR_LIQUIDO' in df.columns else 'FATURAMENTO_LIQUIDO'
    col_c = 'CLIENTE' if 'CLIENTE' in df.columns else df.columns[0]
    col_emp = 'COD_EMPRESA' # A nova coluna solicitada
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.header("🎯 Filtros Estratégicos")
        
        # FILTRO POR COD_EMPRESA (Se existir no arquivo)
        if col_emp in df.columns:
            # Forçamos para string para evitar erros de ordenação
            unidades = sorted(df[col_emp'].astype(str).unique())
            sel_unidades = st.multiselect("Filtrar por Código Empresa:", options=unidades)
        else:
            st.warning("⚠️ Coluna 'COD_EMPRESA' não encontrada no CSV.")
            sel_unidades = []

        # Filtro de Cliente
        lista_clientes = sorted([str(x) for x in df[col_c].unique() if str(x).lower() != 'nan'])
        sel_clientes = st.multiselect("Filtrar Clientes:", options=lista_clientes)
        
        # Filtro de Data
        data_ini, data_fim = df['DATA_NEGOCIACAO'].min().date(), df['DATA_NEGOCIACAO'].max().date()
        periodo = st.date_input("Período:", [data_ini, data_fim])

    # --- APLICAÇÃO DOS FILTROS ---
    df_f = df.copy()
    
    if sel_unidades:
        df_f = df_f[df_f[col_emp].astype(str).isin(sel_unidades)]
    
    if sel_clientes:
        df_f = df_f[df_f[col_c].isin(sel_clientes)]
        
    if len(periodo) == 2:
        df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= periodo[0]) & (df_f['DATA_NEGOCIACAO'].dt.date <= periodo[1])]

    # --- DASHBOARD ---
    st.title("🚀 BI Intelligence - Bem Leve")
    
    # Cards de Resumo
    c1, c2, c3 = st.columns(3)
    fat_total = df_f[col_v].sum()
    c1.metric("💰 Faturamento Total", f"R$ {fat_total:,.2f}")
    c2.metric("🏢 Clientes Ativos", len(df_f[col_c].unique()))
    c3.metric("📦 Qtd. Vendas", len(df_f))

    st.markdown("---")

    # Gráfico 1: Faturamento por Unidade (Se houver COD_EMPRESA)
    if col_emp in df.columns and not df_f.empty:
        st.subheader("🏢 Faturamento por Código de Empresa")
        fat_unidade = df_f.groupby(col_emp)[col_v].sum().reset_index()
        fig_unidade = px.bar(fat_unidade, x=col_emp, y=col_v, 
                             color=col_v, color_continuous_scale='Bluered',
                             labels={col_emp: 'Código Empresa', col_v: 'Total (R$)'})
        st.plotly_chart(fig_unidade, use_container_width=True)

    # Gráfico 2: Top Clientes
    st.subheader("🏆 Ranking de Clientes")
    top_c = df_f.groupby(col_c)[col_v].sum().sort_values(ascending=True).tail(15).reset_index()
    fig_rank = px.bar(top_c, x=col_v, y=col_c, orientation='h', color=col_v, color_continuous_scale='Viridis')
    st.plotly_chart(fig_rank, use_container_width=True)

else:
    st.error("Erro ao carregar os dados. Verifique se o arquivo está no GitHub.")
