import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="BI Elite | Bem Leve", layout="wide")

@st.cache_data
def carregar_dados_blindados():
    for arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            df = pd.read_csv(arq, sep=';', encoding='latin1')
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Converte valores financeiros
            for col in ['VALOR_LIQUIDO', 'FATURAMENTO_LIQUIDO', 'LUCRO_ESTIMADO']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Converte datas
            df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
            df = df.dropna(subset=['DATA_NEGOCIACAO'])
            
            # Identifica colunas
            col_v = 'VALOR_LIQUIDO' if 'VALOR_LIQUIDO' in df.columns else 'FATURAMENTO_LIQUIDO'
            col_c = 'CLIENTE' if 'CLIENTE' in df.columns else df.columns[0]
            col_l = 'LUCRO_ESTIMADO' if 'LUCRO_ESTIMADO' in df.columns else None
            
            # GARANTIA TOTAL: Força a coluna de cliente a ser string pura
            df[col_c] = df[col_c].astype(str).fillna('INDEFINIDO')
            
            return df, col_v, col_c, col_l
        except:
            continue
    return None, None, None, None

df, col_v, col_c, col_l = carregar_dados_blindados()

if df is not None:
    # --- AQUI É ONDE O ERRO MORRE ---
    # 1. Pegamos os valores únicos
    clientes_raw = df[col_c].unique()
    
    # 2. Criamos uma lista nova convertendo CADA item para string e removendo 'nan'
    lista_limpa = []
    for c in clientes_raw:
        nome = str(c).strip()
        if nome.lower() != 'nan' and nome != '':
            lista_limpa.append(nome)
    
    # 3. Ordenamos a lista já garantida como texto
    lista_final_clientes = sorted(lista_limpa)

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("📊 Filtros")
        # Usamos a lista_final_clientes que acabamos de blindar
        sel_clientes = st.multiselect("Filtrar Clientes:", options=lista_final_clientes)
        
        data_min, data_max = df['DATA_NEGOCIACAO'].min().date(), df['DATA_NEGOCIACAO'].max().date()
        datas = st.date_input("Período", [data_min, data_max])

    # Filtragem
    df_f = df.copy()
    if sel_clientes:
        df_f = df_f[df_f[col_c].isin(sel_clientes)]
    if len(datas) == 2:
        df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= datas[0]) & (df_f['DATA_NEGOCIACAO'].dt.date <= datas[1])]

    # --- DASHBOARD ---
    st.title("📈 Performance Comercial")
    
    # KPIs
    k1, k2, k3 = st.columns(3)
    k1.metric("Faturamento", f"R$ {df_f[col_v].sum():,.2f}")
    k2.metric("Vendas", len(df_f))
    if col_l:
        k3.metric("Lucro", f"R$ {df_f[col_l].sum():,.2f}")

    # Gráfico de Ranking
    st.subheader("🏆 Top Clientes")
    ranking = df_f.groupby(col_c)[col_v].sum().sort_values(ascending=True).tail(15).reset_index()
    fig = px.bar(ranking, x=col_v, y=col_c, orientation='h', color=col_v, color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

    # Tabela
    with st.expander("Ver dados brutos"):
        st.write(df_f)
else:
    st.error("Não foi possível carregar os dados. Verifique o arquivo CSV.")
