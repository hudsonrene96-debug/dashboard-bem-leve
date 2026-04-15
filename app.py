import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="BI Estratégico BEM LEVE", layout="wide")

# 1. Carregamento com Limpeza Total
def carregar_dados():
    try:
        # Tenta carregar o arquivo disponível
        dados = pd.read_csv('VENDAS_LIMPAS.csv', sep=';')
    except:
        try:
            dados = pd.read_csv('VENDAS_CONVERTIDO.csv', sep=';')
        except:
            return None
    
    # Limpa colunas e força tipos
    dados.columns = [c.strip() for c in dados.columns]
    
    # FORÇA TUDO QUE É NOME PARA STRING E REMOVE VAZIOS
    dados['CLIENTE'] = dados['CLIENTE'].astype(str).replace('nan', 'Não Informado')
    dados['VENDEDOR'] = dados['VENDEDOR'].astype(str).replace('nan', 'Não Informado')
    dados['PRODUTO'] = dados['PRODUTO'].astype(str).replace('nan', 'Não Informado')
    
    # Garante números
    if 'VALOR_LIQUIDO' in dados.columns:
        dados['VALOR_LIQUIDO'] = pd.to_numeric(dados['VALOR_LIQUIDO'], errors='coerce').fillna(0)
    
    # Garante Datas
    dados['DATA_NEGOCIACAO'] = pd.to_datetime(dados['DATA_NEGOCIACAO'], errors='coerce')
    dados = dados.dropna(subset=['DATA_NEGOCIACAO'])
    
    return dados

df = carregar_dados()

if df is None:
    st.error("Arquivo não encontrado no GitHub!")
    st.stop()

# --- SIDEBAR ---
st.sidebar.header("🎯 Filtros")

# SOLUÇÃO DEFINITIVA PARA O ERRO DE TIPO:
# Criamos uma lista garantindo que cada item é uma string limpa
try:
    opcoes_empresas = df['CLIENTE'].unique().tolist()
    # Filtramos apenas o que for texto real e ordenamos
    lista_empresas = sorted([str(x) for x in opcoes_empresas if x and str(x).lower() != 'nan'])
except Exception as e:
    # Se ainda assim der erro, usamos a lista sem ordenar para não travar o app
    lista_empresas = df['CLIENTE'].unique().tolist()

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
    
    # Vendedores (Proteção contra erro se vazio)
    vendas_v = df_f.groupby('VENDEDOR')['VALOR_LIQUIDO'].sum()
    if not vendas_v.empty:
        c2.metric("🏆 Melhor Vendedor", vendas_v.idxmax(), f"R$ {vendas_v.max():,.2f}")
        c3.metric("🏢 Melhor Cliente", df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().idxmax())

    st.markdown("---")

    # Gráfico Empresa
    st.subheader("🏢 Faturamento por Empresa")
    fat_emp = df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().sort_values(ascending=True).tail(15)
    fig1, ax1 = plt.subplots(figsize=(12, 7))
    bars = ax1.barh(fat_emp.index, fat_emp.values, color='#2A9D8F')
    ax1.bar_label(bars, fmt=' R$ %.2f', padding=10, fontweight='bold')
    plt.subplots_adjust(left=0.3)
    st.pyplot(fig1)
else:
    st.warning("Sem dados para os filtros aplicados.")
