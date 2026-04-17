import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da página
st.set_page_config(page_title="BI Bem Leve", layout="wide", page_icon="📈")

# 1. Função de Carga (A mesma que você já validou)
@st.cache_data
def carregar_dados():
    for arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            df = pd.read_csv(arq, sep=';', encoding='latin1')
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Valores
            col_valor = 'VALOR_LIQUIDO' if 'VALOR_LIQUIDO' in df.columns else 'FATURAMENTO_LIQUIDO'
            if col_valor in df.columns:
                df[col_valor] = pd.to_numeric(df[col_valor], errors='coerce').fillna(0)
            
            # Lucro (Opcional)
            if 'LUCRO_ESTIMADO' in df.columns:
                df['LUCRO_ESTIMADO'] = pd.to_numeric(df['LUCRO_ESTIMADO'], errors='coerce').fillna(0)
            
            # Datas
            df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
            df = df.dropna(subset=['DATA_NEGOCIACAO'])
            return df, col_valor
        except:
            continue
    return None, None

df, col_vendas = carregar_dados()

if df is not None:
    # --- Identificação de Coluna de Cliente ---
    possiveis_nomes = ['CLIENTE', 'NOME_CLIENTE', 'PARCEIRO', 'NOME']
    col_cliente = 'CLIENTE'
    for p in possiveis_nomes:
        if p in df.columns:
            col_cliente = p
            break

    # --- Sidebar ---
    st.sidebar.header("🎯 Filtros")
    try:
        opcoes = [str(x).strip() for x in df[col_cliente].unique() if pd.notna(x)]
        lista_empresas = sorted([x for x in opcoes if x.lower() != 'nan' and x != ''])
    except:
        lista_empresas = sorted(list(df[col_cliente].astype(str).unique()))

    empresas_sel = st.sidebar.multiselect("Selecionar Empresas:", options=lista_empresas)
    data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
    data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())

    # --- Filtragem ---
    df_f = df.copy()
    if empresas_sel:
        df_f = df_f[df_f[col_cliente].astype(str).isin(empresas_sel)]
    df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df_f['DATA_NEGOCIACAO'].dt.date <= data_fim)]

    # --- DASHBOARD VISUAL ---
    if not df_f.empty:
        st.title("📊 BI Estratégico - Bem Leve")
        
        # Linha 1: Métricas
        c1, c2, c3 = st.columns(3)
        total_venda = df_f[col_vendas].sum()
        c1.metric("💰 Faturamento Total", f"R$ {total_venda:,.2f}")
        
        if 'LUCRO_ESTIMADO' in df_f.columns:
            total_lucro = df_f['LUCRO_ESTIMADO'].sum()
            margem = (total_lucro / total_venda * 100) if total_venda > 0 else 0
            c2.metric("💵 Lucro Estimado", f"R$ {total_lucro:,.2f}")
            c3.metric("📈 Margem Média", f"{margem:.1f}%")
        else:
            c2.metric("🏢 Qtd. Clientes", len(df_f[col_cliente].unique()))
            c3.metric("📦 Qtd. Vendas", len(df_f))

        st.markdown("---")

        # Linha 2: Gráficos Interativos
        col_esq, col_dir = st.columns(2)

        with col_esq:
            st.subheader("🏢 Top Clientes por Valor")
            fat_emp = df_f.groupby(col_cliente)[col_vendas].sum().sort_values(ascending=True).tail(10).reset_index()
            fig_bar = px.bar(fat_emp, x=col_vendas, y=col_cliente, orientation='h', 
                             text_auto='.2s', color=col_vendas, color_continuous_scale='Viridis')
            fig_bar.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_dir:
            st.subheader("🍰 Participação de Mercado (Top 5)")
            share = df_f.groupby(col_cliente)[col_vendas].sum().sort_values(ascending=False).head(5).reset_index()
            fig_pie = px.pie(share, values=col_vendas, names=col_cliente, hole=0.4)
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)

        # Tabela Detalhada
        with st.expander("📄 Ver Dados Detalhados"):
            st.dataframe(df_f.sort_values('DATA_NEGOCIACAO', ascending=False), use_container_width=True)
    else:
        st.info("Ajuste os filtros para carregar os dados.")
else:
    st.error("❌ Erro ao carregar arquivo. Verifique o CSV no GitHub.")
