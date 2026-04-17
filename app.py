import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da página para ocupar a tela toda e ter um ícone legal
st.set_page_config(page_title="BI Estratégico | Bem Leve", layout="wide", page_icon="📈")

# --- ESTILIZAÇÃO CSS (Para deixar os cards bonitos) ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #2A9D8F; }
    .stPlotlyChart { border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def carregar_dados_premium():
    for arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            df = pd.read_csv(arq, sep=';', encoding='latin1')
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Identificação automática de colunas
            col_valor = 'VALOR_LIQUIDO' if 'VALOR_LIQUIDO' in df.columns else 'FATURAMENTO_LIQUIDO'
            if col_valor in df.columns:
                df[col_valor] = pd.to_numeric(df[col_valor], errors='coerce').fillna(0)
            
            df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
            df = df.dropna(subset=['DATA_NEGOCIACAO'])
            
            # Limpeza de nomes
            col_c = 'CLIENTE' if 'CLIENTE' in df.columns else df.columns[0]
            df[col_c] = df[col_c].astype(str).replace('nan', 'Não Informado')
            
            return df, col_valor, col_c
        except:
            continue
    return None, None, None

df, col_vendas, col_cliente = carregar_dados_premium()

if df is not None:
    # --- PROCESSAMENTO DE FILTROS ---
    opcoes_clientes = sorted([str(x) for x in df[col_cliente].unique() if str(x).lower() != 'nan'])
    
    with st.sidebar:
        st.title("⚙️ Configurações")
        st.markdown("Use os filtros abaixo para refinar a análise.")
        empresas_sel = st.multiselect("Filtrar por Empresa:", options=opcoes_clientes)
        
        # Filtro de Data Dinâmico
        data_min, data_max = df['DATA_NEGOCIACAO'].min().date(), df['DATA_NEGOCIACAO'].max().date()
        periodo = st.date_input("Período de Análise:", [data_min, data_max])

    # Aplicando filtros
    df_f = df.copy()
    if empresas_sel:
        df_f = df_f[df_f[col_cliente].isin(empresas_sel)]
    
    if len(periodo) == 2:
        df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= periodo[0]) & (df_f['DATA_NEGOCIACAO'].dt.date <= periodo[1])]

    # --- DASHBOARD VISUAL ---
    st.title("📊 BI de Performance Comercial")
    st.markdown(f"Exibindo dados de **{periodo[0].strftime('%d/%m/%Y')}** até **{periodo[1].strftime('%d/%m/%Y')}**")

    # Linha 1: Métricas Principais
    m1, m2, m3, m4 = st.columns(4)
    faturamento_total = df_f[col_vendas].sum()
    ticket_medio = faturamento_total / len(df_f) if len(df_f) > 0 else 0
    
    m1.metric("Faturamento Total", f"R$ {faturamento_total:,.2f}")
    m2.metric("Qtd. Pedidos", f"{len(df_f):,}")
    m3.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
    m4.metric("Clientes Ativos", f"{len(df_f[col_cliente].unique())}")

    st.markdown("---")

    # Linha 2: Gráficos
    g1, g2 = st.columns([1, 1])

    with g1:
        st.subheader("🏢 Top 10 Clientes por Volume")
        top_clientes = df_f.groupby(col_cliente)[col_vendas].sum().sort_values(ascending=True).tail(10).reset_index()
        fig_barra = px.bar(
            top_clientes, 
            x=col_vendas, 
            y=col_cliente, 
            orientation='h',
            color=col_vendas,
            color_continuous_scale='Viridis',
            labels={col_vendas: 'Faturamento (R$)', col_cliente: 'Empresa'},
            template='plotly_white'
        )
        fig_barra.update_layout(showlegend=False, height=450)
        st.plotly_chart(fig_barra, use_container_width=True)

    with g2:
        st.subheader("📈 Evolução de Vendas no Tempo")
        # Agrupando por dia para o gráfico de linha
        evolucao = df_f.groupby(df_f['DATA_NEGOCIACAO'].dt.date)[col_vendas].sum().reset_index()
        fig_linha = px.line(
            evolucao, 
            x='DATA_NEGOCIACAO', 
            y=col_vendas,
            labels={'DATA_NEGOCIACAO': 'Data', col_vendas: 'Total Vendido'},
            template='plotly_white'
        )
        fig_linha.update_traces(line_color='#2A9D8F', line_width=3)
        fig_linha.update_layout(height=450)
        st.plotly_chart(fig_linha, use_container_width=True)

    # Linha 3: Tabela de Dados Detalhada
    with st.expander("📄 Visualizar Tabela de Dados Detalhada"):
        st.dataframe(df_f.sort_values('DATA_NEGOCIACAO', ascending=False), use_container_width=True)

else:
    st.error("Não foi possível carregar os dados. Verifique seu CSV.")
