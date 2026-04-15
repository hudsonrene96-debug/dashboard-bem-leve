import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="BI Estratégico BEM LEVE", layout="wide")

# 1. Função para carregar dados com limpeza profunda
def carregar_dados():
    for nome_arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            dados = pd.read_csv(nome_arq, sep=';')
            # Limpa espaços nos nomes das colunas
            dados.columns = [c.strip() for c in dados.columns]
            
            # VACINA CONTRA ERRO DE TIPO:
            # Garante que CLIENTE, VENDEDOR e PRODUTO sejam sempre TEXTO (str)
            # e substitui valores vazios (NaN) por "Não Informado"
            for col in ['CLIENTE', 'VENDEDOR', 'PRODUTO']:
                if col in dados.columns:
                    dados[col] = dados[col].fillna('Não Informado').astype(str)
            
            # Garante que VALOR_LIQUIDO e QUANTIDADE sejam NUMÉRICOS
            if 'VALOR_LIQUIDO' in dados.columns:
                dados['VALOR_LIQUIDO'] = pd.to_numeric(dados['VALOR_LIQUIDO'], errors='coerce').fillna(0)
            if 'QUANTIDADE' in dados.columns:
                dados['QUANTIDADE'] = pd.to_numeric(dados['QUANTIDADE'], errors='coerce').fillna(0)
                
            return dados
        except:
            continue
    return None

df = carregar_dados()

if df is None:
    st.error("❌ Arquivo CSV não encontrado no GitHub!")
    st.stop()

# Ajuste de Datas
df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')

# --- SIDEBAR ---
st.sidebar.header("🎯 Filtros de Análise")
data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())

# Agora o sorted vai funcionar 100% porque tudo virou texto lá em cima
lista_empresas = sorted(df['CLIENTE'].unique())
empresas_sel = st.sidebar.multiselect("Selecionar Empresas:", options=lista_empresas)

# Aplicar Filtros
df_f = df.copy()
if data_inicio and data_fim:
    df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df_f['DATA_NEGOCIACAO'].dt.date <= data_fim)]
if empresas_sel:
    df_f = df_f[df_f['CLIENTE'].isin(empresas_sel)]

# --- DASHBOARD ---
if not df_f.empty:
    st.title("📊 Painel de Performance Comercial")
    
    # KPIs SUPERIORES
    c1, c2, c3 = st.columns(3)
    fatur_total = df_f['VALOR_LIQUIDO'].sum()
    vendas_v = df_f.groupby('VENDEDOR')['VALOR_LIQUIDO'].sum()
    
    c1.metric("💰 Faturamento Total", f"R$ {fatur_total:,.2f}")
    c2.metric("🏆 Melhor Vendedor", vendas_v.idxmax(), f"R$ {vendas_v.max():,.2f}")
    c3.metric("🏢 Melhor Cliente", df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().idxmax())

    st.markdown("---")

    # --- GRÁFICO DE EMPRESAS ---
    st.subheader("🏢 Faturamento por Empresa")
    fat_emp = df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().sort_values(ascending=True).tail(20)
    
    altura_dinamica = max(6, len(fat_emp) * 0.5)
    fig1, ax1 = plt.subplots(figsize=(12, altura_dinamica))
    bars1 = ax1.barh(fat_emp.index, fat_emp.values, color='#2A9D8F')
    ax1.bar_label(bars1, fmt=' R$ %.2f', padding=10, fontweight='bold')
    
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    plt.subplots_adjust(left=0.3) 
    st.pyplot(fig1)

    # --- PRODUTOS ---
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🔥 Top 10 Produtos")
        p_v = df_f.groupby('PRODUTO')['QUANTIDADE'].sum().sort_values(ascending=True).tail(10)
        fig2, ax2 = plt.subplots()
        ax2.barh(p_v.index, p_v.values, color='#457B9D')
        ax2.bar_label(ax2.containers[0], padding=3)
        st.pyplot(fig2)
    with col_b:
        st.subheader("🧊 5 Menos Vendidos")
        p_m = df_f.groupby('PRODUTO')['QUANTIDADE'].sum().sort_values(ascending=True).head(5)
        fig3, ax3 = plt.subplots()
        ax3.barh(p_m.index, p_m.values, color='#E76F51')
        ax3.bar_label(ax3.containers[0], padding=3)
        st.pyplot(fig3)
else:
    st.warning("Ajuste os filtros para visualizar os dados.")
