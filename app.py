import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="BI Estratégico BEM LEVE", layout="wide")

# Carregamento e Limpeza
def carregar_dados():
    try:
        dados = pd.read_csv('VENDAS_LIMPAS.csv', sep=';')
    except:
        dados = pd.read_csv('VENDAS_CONVERTIDO.csv', sep=';')
    
    dados.columns = [c.strip() for c in dados.columns]
    
    # Tratamento preventivo de nulos e tipos
    if 'VALOR_LIQUIDO' in dados.columns:
        dados['VALOR_LIQUIDO'] = pd.to_numeric(dados['VALOR_LIQUIDO'], errors='coerce').fillna(0)
    if 'DATA_NEGOCIACAO' in dados.columns:
        dados['DATA_NEGOCIACAO'] = pd.to_datetime(dados['DATA_NEGOCIACAO'], errors='coerce')
        
    return dados

df = carregar_dados()

# --- SIDEBAR (FILTROS) ---
st.sidebar.header("🎯 Filtros de Análise")

# Linha corrigida para evitar o erro de float vs str
lista_empresas = sorted([str(x) for x in df['CLIENTE'].unique() if pd.notna(x)])

empresas_selecionadas = st.sidebar.multiselect("Selecionar Empresas:", options=lista_empresas)

# Filtro de Data
data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())

# Aplicar Filtros
df_f = df.copy()
if empresas_selecionadas:
    df_f = df_f[df_f['CLIENTE'].astype(str).isin(empresas_selecionadas)]

if data_inicio and data_fim:
    df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df_f['DATA_NEGOCIACAO'].dt.date <= data_fim)]

# --- DASHBOARD ---
if not df_f.empty:
    st.title("📊 Painel de Performance Comercial")
    
    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Faturamento Total", f"R$ {df_f['VALOR_LIQUIDO'].sum():,.2f}")
    
    vendas_v = df_f.groupby('VENDEDOR')['VALOR_LIQUIDO'].sum()
    c2.metric("🏆 Melhor Vendedor", vendas_v.idxmax(), f"R$ {vendas_v.max():,.2f}")
    c3.metric("🏢 Melhor Cliente", df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().idxmax())

    st.markdown("---")

    # Gráfico de Faturamento por Empresa Separadamente
    st.subheader("🏢 Faturamento por Empresa")
    fat_emp = df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().sort_values(ascending=True).tail(20)
    
    fig1, ax1 = plt.subplots(figsize=(12, max(6, len(fat_emp)*0.5)))
    bars1 = ax1.barh(fat_emp.index, fat_emp.values, color='#2A9D8F')
    ax1.bar_label(bars1, fmt=' R$ %.2f', padding=10, fontweight='bold')
    plt.subplots_adjust(left=0.3)
    st.pyplot(fig1)

else:
    st.warning("Selecione os filtros na barra lateral.")
