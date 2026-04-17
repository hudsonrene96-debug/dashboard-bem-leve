import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="BI Estratégico", layout="wide")

# Função de carga com "filtro de sujeira"
@st.cache_data
def carregar_e_limpar_dados():
    df = None
    for arq in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
        try:
            df = pd.read_csv(arq, sep=';', encoding='latin1')
            break
        except:
            continue
    
    if df is not None:
        # Limpa nomes de colunas
        df.columns = [str(c).strip() for c in df.columns]
        
        # Garante que CLIENTE seja texto e remove nulos reais
        df['CLIENTE'] = df['CLIENTE'].astype(str).replace('nan', 'Não Informado')
        df['VALOR_LIQUIDO'] = pd.to_numeric(df['VALOR_LIQUIDO'], errors='coerce').fillna(0)
        df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
        df = df.dropna(subset=['DATA_NEGOCIACAO'])
        return df
    return None

df = carregar_e_limpar_dados()

if df is not None:
    # --- MÉTODO MANUAL PARA EVITAR TYPEERROR ---
    # Criamos a lista apenas com o que for estritamente texto (str)
    opcoes = df['CLIENTE'].unique().tolist()
    lista_final = []
    
    for item in opcoes:
        # Só entra na lista se for texto e não for vazio
        valor_str = str(item).strip()
        if valor_str.lower() != 'nan' and valor_str != '':
            lista_final.append(valor_str)
    
    # Ordenação segura: se falhar, o dashboard NÃO trava
    try:
        lista_final.sort()
    except:
        pass 

    # --- SIDEBAR ---
    st.sidebar.header("🎯 Filtros")
    empresas_sel = st.sidebar.multiselect("Filtrar Empresas:", options=lista_final)
    
    # Filtro de Data
    data_min = df['DATA_NEGOCIACAO'].min()
    data_max = df['DATA_NEGOCIACAO'].max()
    data_inicio = st.sidebar.date_input("Início", data_min)
    data_fim = st.sidebar.date_input("Fim", data_max)

    # --- APLICAR FILTROS ---
    df_f = df.copy()
    if empresas_sel:
        df_f = df_f[df_f['CLIENTE'].isin(empresas_sel)]
    
    df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= data_inicio) & 
                (df_f['DATA_NEGOCIACAO'].dt.date <= data_fim)]

    # --- DASHBOARD ---
    if not df_f.empty:
        st.title("📊 BI de Vendas")
        
        col1, col2 = st.columns(2)
        col1.metric("💰 Faturamento", f"R$ {df_f['VALOR_LIQUIDO'].sum():,.2f}")
        col2.metric("📦 Pedidos", len(df_f))

        st.markdown("---")
        
        # Gráfico com proteção de tipo
        st.subheader("🏢 Faturamento por Cliente")
        dados_grafico = df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().sort_values().tail(15)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        # Forçamos o eixo a ser string aqui também
        ax.barh([str(i) for i in dados_grafico.index], dados_grafico.values, color='#2A9D8F')
        plt.subplots_adjust(left=0.3)
        st.pyplot(fig)
    else:
        st.warning("Selecione filtros para exibir os dados.")
else:
    st.error("Arquivo não encontrado. Verifique se o CSV está na mesma pasta do código.")
