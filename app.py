import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="BI Estratégico BEM LEVE", layout="wide")

# 1. Função de Carregamento com Limpeza Agressiva
def carregar_dados():
    arquivo = None
    for nome in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            arquivo = pd.read_csv(nome, sep=';')
            break
        except:
            continue
    
    if arquivo is not None:
        # Limpa nomes de colunas
        arquivo.columns = [c.strip() for c in arquivo.columns]
        
        # TRATAMENTO DE CHOQUE: Garante que CLIENTE seja sempre texto e sem nulos
        arquivo['CLIENTE'] = arquivo['CLIENTE'].fillna('Não Informado').astype(str)
        arquivo['VENDEDOR'] = arquivo['VENDEDOR'].fillna('Não Informado').astype(str)
        
        # Garante que VALOR_LIQUIDO seja número
        if 'VALOR_LIQUIDO' in arquivo.columns:
            arquivo['VALOR_LIQUIDO'] = pd.to_numeric(arquivo['VALOR_LIQUIDO'], errors='coerce').fillna(0)
            
        # Garante que DATA_NEGOCIACAO seja data válida
        if 'DATA_NEGOCIACAO' in arquivo.columns:
            arquivo['DATA_NEGOCIACAO'] = pd.to_datetime(arquivo['DATA_NEGOCIACAO'], errors='coerce')
            # Remove linhas onde a data é impossível de ler (NaT)
            arquivo = arquivo.dropna(subset=['DATA_NEGOCIACAO'])
            
        return arquivo
    return None

df = carregar_dados()

if df is None:
    st.error("❌ Erro: Arquivo de dados não encontrado no GitHub.")
    st.stop()

# --- SIDEBAR (FILTROS) ---
st.sidebar.header("🎯 Filtros de Análise")

# Filtro de Data (Seguro)
min_data = df['DATA_NEGOCIACAO'].min()
max_data = df['DATA_NEGOCIACAO'].max()
data_inicio = st.sidebar.date_input("Início", min_data)
data_fim = st.sidebar.date_input("Fim", max_data)

# Filtro de Empresa (Blindado contra erro de tipo)
# Criamos a lista de nomes únicos, garantindo que são strings e ordenando
lista_empresas = sorted(df['CLIENTE'].unique().tolist())
empresas_sel = st.sidebar.multiselect("Selecionar Empresas:", options=lista_empresas)

# --- APLICAR FILTROS ---
df_f = df.copy()

# Filtro por data
df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= data_inicio) & 
            (df_f['DATA_NEGOCIACAO'].dt.date <= data_fim)]

# Filtro por empresa
if empresas_sel:
    df_f = df_f[df_f['CLIENTE'].isin(empresas_sel)]

# --- DASHBOARD ---
if not df_f.empty:
    st.title("📊 Painel de Performance Comercial")
    
    # KPIs
    c1, c2, c3 = st.columns(3)
    fatur_total = df_f['VALOR_LIQUIDO'].sum()
    vendas_v = df_f.groupby('VENDEDOR')['VALOR_LIQUIDO'].sum()
    
    c1.metric("💰 Faturamento Total", f"R$ {fatur_total:,.2f}")
    c2.metric("🏆 Melhor Vendedor", vendas_v.idxmax(), f"R$ {vendas_v.max():,.2f}")
    c3.metric("🏢 Melhor Cliente", df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().idxmax())

    st.markdown("---")

    # Gráfico Empresa (Ajustado para nomes longos)
    st.subheader("🏢 Faturamento por Empresa")
    fat_emp = df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().sort_values(ascending=True).tail(20)
    
    fig1, ax1 = plt.subplots(figsize=(12, max(6, len(fat_emp)*0.5)))
    bars1 = ax1.barh(fat_emp.index, fat_emp.values, color='#2A9D8F')
    ax1.bar_label(bars1, fmt=' R$ %.2f', padding=10, fontweight='bold')
    
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    plt.subplots_adjust(left=0.3) 
    st.pyplot(fig1)

else:
    st.warning("⚠️ Ajuste os filtros para exibir os dados.")
