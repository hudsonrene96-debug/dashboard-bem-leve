import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="BI Estratégico BEM LEVE", layout="wide")

# 1. Carregamento com Limpeza de Tipos
def carregar_dados():
    try:
        dados = pd.read_csv('VENDAS_LIMPAS.csv', sep=';')
    except:
        try:
            dados = pd.read_csv('VENDAS_CONVERTIDO.csv', sep=';')
        except:
            return None
    
    dados.columns = [c.strip() for c in dados.columns]
    
    # TRATAMENTO DE CHOQUE: Remove nulos e converte tudo para string imediatamente
    dados['CLIENTE'] = dados['CLIENTE'].fillna('Nao Informado').astype(str)
    
    if 'VALOR_LIQUIDO' in dados.columns:
        dados['VALOR_LIQUIDO'] = pd.to_numeric(dados['VALOR_LIQUIDO'], errors='coerce').fillna(0)
    
    dados['DATA_NEGOCIACAO'] = pd.to_datetime(dados['DATA_NEGOCIACAO'], errors='coerce')
    dados = dados.dropna(subset=['DATA_NEGOCIACAO'])
    
    return dados

df = carregar_dados()

if df is None:
    st.error("Arquivo não encontrado!")
    st.stop()

# --- SIDEBAR ---
st.sidebar.header("🎯 Filtros")

# SOLUÇÃO DEFINITIVA PARA O ERRO DE TIPO (TypeError)
def obter_lista_limpa(series):
    # 1. Pega os valores únicos
    valores = series.unique()
    # 2. Converte cada um para string, remove espaços e ignora o que for vazio/'nan'
    lista_str = []
    for v in valores:
        v_str = str(v).strip()
        if v_str.lower() != 'nan' and v_str != '':
            lista_str.append(v_str)
    # 3. Retorna a lista ordenada (agora garantido que só tem string)
    return sorted(lista_str)

try:
    lista_empresas = obter_lista_limpa(df['CLIENTE'])
except:
    # Caso de emergência: se ainda der erro, pega sem ordenar
    lista_empresas = list(df['CLIENTE'].astype(str).unique())

empresas_sel = st.sidebar.multiselect("Selecionar Empresas:", options=lista_empresas)

# Filtro de Data
data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())

# --- APLICAÇÃO DOS FILTROS ---
df_f = df.copy()
df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df_f['DATA_NEGOCIACAO'].dt.date <= data_fim)]

if empresas_sel:
    df_f = df_f[df_f['CLIENTE'].isin(empresas_sel)]

# --- DASHBOARD ---
if not df_f.empty:
    st.title("📊 Painel de Performance Comercial")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Faturamento Total", f"R$ {df_f['VALOR_LIQUIDO'].sum():,.2f}")
    
    # Vendedores
    vendas_v = df_f.groupby('VENDEDOR')['VALOR_LIQUIDO'].sum()
    if not vendas_v.empty:
        c2.metric("🏆 Melhor Vendedor", str(vendas_v.idxmax()), f"R$ {vendas_v.max():,.2f}")
        c3.metric("🏢 Melhor Cliente", str(df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().idxmax()))

    st.markdown("---")

    # Gráfico Empresa
    st.subheader("🏢 Faturamento por Empresa")
    fat_emp = df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().sort_values(ascending=True).tail(15)
    
    fig1, ax1 = plt.subplots(figsize=(12, 7))
    bars = ax1.barh(fat_emp.index.astype(str), fat_emp.values, color='#2A9D8F')
    ax1.bar_label(bars, fmt=' R$ %.2f', padding=10, fontweight='bold')
    plt.subplots_adjust(left=0.3)
    st.pyplot(fig1)
else:
    st.warning("Sem dados para os filtros aplicados.")
