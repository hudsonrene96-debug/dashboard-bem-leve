import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Dashboard Bem Leve", layout="wide")

# Forçamos o Streamlit a ignorar o cache antigo mudando o nome da função
def carregar_dados_novos_v100():
    try:
        # Tenta carregar os ficheiros
        df = None
        for nome in ['VENDAS_LIMPAS.csv', 'VENDAS_CONVERTIDO.csv', 'dados.csv']:
            try:
                df = pd.read_csv(nome, sep=';', encoding='latin1')
                break
            except:
                continue
        
        if df is not None:
            df.columns = [str(c).strip() for c in df.columns]
            
            # Limpeza radical de tipos
            df['CLIENTE'] = df['CLIENTE'].astype(str).replace('nan', 'Não Informado')
            df['VALOR_LIQUIDO'] = pd.to_numeric(df['VALOR_LIQUIDO'], errors='coerce').fillna(0)
            df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'], errors='coerce')
            df = df.dropna(subset=['DATA_NEGOCIACAO'])
            return df
    except:
        return None

df = carregar_dados_novos_v100()

if df is not None:
    # --- FILTRO DE CLIENTE SEM COMANDO SORTED NO PANDAS ---
    # Criamos a lista de forma 100% manual e segura contra erros de tipo
    lista_opcoes = []
    try:
        unicos = df['CLIENTE'].unique()
        for u in unicos:
            val = str(u).strip()
            if val.lower() != 'nan' and val != '':
                lista_opcoes.append(val)
        
        # Tentamos ordenar. Se o Python der erro de tipo, ele pula a ordenação
        lista_opcoes.sort()
    except:
        # Se falhar a ordem, usa a lista como está para não travar o app
        lista_opcoes = [str(x) for x in df['CLIENTE'].unique()]

    # --- SIDEBAR ---
    st.sidebar.header("🎯 Filtros")
    
    # O multiselect recebe a lista que já foi limpa no loop acima
    empresas_sel = st.sidebar.multiselect("Filtrar Empresas:", options=lista_opcoes)
    
    data_inicio = st.sidebar.date_input("Início", df['DATA_NEGOCIACAO'].min())
    data_fim = st.sidebar.date_input("Fim", df['DATA_NEGOCIACAO'].max())

    # --- APLICAR FILTROS ---
    df_f = df.copy()
    if empresas_sel:
        df_f = df_f[df_f['CLIENTE'].isin(empresas_sel)]
    
    df_f = df_f[(df_f['DATA_NEGOCIACAO'].dt.date >= data_inicio) & (df_f['DATA_NEGOCIACAO'].dt.date <= data_fim)]

    # --- DASHBOARD ---
    if not df_f.empty:
        st.title("📊 BI Estratégico - Bem Leve")
        
        c1, c2 = st.columns(2)
        c1.metric("💰 Faturamento Total", f"R$ {df_f['VALOR_LIQUIDO'].sum():,.2f}")
        c2.metric("🏢 Clientes Atendidos", len(df_f['CLIENTE'].unique()))

        st.markdown("---")

        # Gráfico forçando strings
        st.subheader("🏢 Faturamento por Empresa")
        fat_emp = df_f.groupby('CLIENTE')['VALOR_LIQUIDO'].sum().sort_values(ascending=True).tail(15)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        # Forçamos o índice a ser string no gráfico também
        ax.barh([str(i) for i in fat_emp.index], fat_emp.values, color='#2A9D8F')
        plt.subplots_adjust(left=0.3)
        st.pyplot(fig)
    else:
        st.info("Utilize os filtros laterais para carregar os dados.")
else:
    st.error("Erro: Não foi possível carregar o ficheiro de dados.")
