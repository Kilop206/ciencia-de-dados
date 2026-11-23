import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import time

# Configuração da página
st.set_page_config(
    page_title="Painel de Monitoramento de Sensores",
    page_icon="📊",
    layout="wide"
)

def carregar_dados(limite=100):
    conn = sqlite3.connect('sensores.db', timeout=10)
    query = f'''
        SELECT timestamp, sensor_id, temperatura, umidade, pressao 
        FROM leituras_sensores 
        ORDER BY id DESC 
        LIMIT {limite}
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
    return df

st.title("📊 Monitoramento IoT em Tempo Real")

# Barra lateral de controle
st.sidebar.header("Filtros e Controles")
intervalo_atualizacao = st.sidebar.slider("Frequência de Atualização (segundos):", 1, 10, 2)
quantidade_registros = st.sidebar.slider("Histórico de Leituras:", 30, 300, 120)

df = carregar_dados(limite=quantidade_registros)

if df.empty:
    st.info("Aguardando dados... Certifique-se de que o arquivo `simulator.py` está rodando.")
else:
    sensores_disponiveis = df['sensor_id'].unique().tolist()
    sensor_selecionado = st.sidebar.selectbox("Filtrar por Sensor:", ["Todos"] + sensores_disponiveis)

    if sensor_selecionado != "Todos":
        df_filtrado = df[df['sensor_id'] == sensor_selecionado]
    else:
        df_filtrado = df

    # Indicadores dos últimos valores
    st.subheader("Últimas Leituras Registradas")
    ultimos = df_filtrado.groupby('sensor_id').last().reset_index()
    
    cols = st.columns(len(ultimos))
    for idx, row in ultimos.iterrows():
        with cols[idx]:
            st.markdown(f"### {row['sensor_id']}")
            st.metric("🌡️ Temperatura", f"{row['temperatura']} °C")
            st.metric("💧 Umidade", f"{row['umidade']} %")
            st.metric("⏲️ Pressão", f"{row['pressao']} hPa")

    st.markdown("---")

    # Gráficos Dinâmicos
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        fig_temp = px.line(
            df_filtrado, 
            x='timestamp', 
            y='temperatura', 
            color='sensor_id',
            title="Temperatura (°C) ao longo do tempo",
            markers=True
        )
        fig_temp.update_xaxes(title="Horário")
        fig_temp.update_yaxes(title="°C")
        st.plotly_chart(fig_temp, use_container_width=True)

    with col_g2:
        fig_umid = px.line(
            df_filtrado, 
            x='timestamp', 
            y='umidade', 
            color='sensor_id',
            title="Umidade Relativa (%) ao longo do tempo",
            markers=True
        )
        fig_umid.update_xaxes(title="Horário")
        fig_umid.update_yaxes(title="%")
        st.plotly_chart(fig_umid, use_container_width=True)

    # Visualização de dados brutos
    with st.expander("Visualizar Tabela de Registros"):
        st.dataframe(df_filtrado.sort_values('timestamp', ascending=False), use_container_width=True)

# Loop de atualização automática em tempo real
time.sleep(intervalo_atualizacao)
st.rerun()