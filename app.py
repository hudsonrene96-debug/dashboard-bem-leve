import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="BI Gestão Estratégica", layout="wide")

# 1. Carregar Dados
def carregar_dados():
    for nome_arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            return pd.read_csv(nome_arq, sep=';')
        except:
            continue
    return None

df = carregar_dados()

if df is None:
    st.error("❌ Arquivo CSV não encontrado no GitHub!")
    st.stop()

# Ajuste de Colunas e Datas
df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')

# --- SIDEBAR (FILTROS) ---
st.sidebar.header("🎯 Filtros de Análise")
data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())

# CORREÇÃO AQUI: Garante que o sorted não trave com valores nulos
lista_empresas = sorted(df['CLIENTE'].dropna().astype(str).unique())
empresas_selecionadas = st.sidebar.multiselect("Selecionar Empresas:", options=lista_empresas, default=None)

# Aplicar Filtros
df_f = df[(df['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df['DATA_NEGOCIACAO'].dt.date <= data_fim)].copy()
if empresas_selecionadas:
    df_f = df_f[df_f['CLIENTE'].astype(str).isin(empresas_selecionadas)]

# ... (restante do código de gráficos que já funcionava)
