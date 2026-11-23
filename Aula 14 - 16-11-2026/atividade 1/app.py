import sqlite3
import time

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Monitoramento da Qualidade do Ar",
    page_icon="🌿",
    layout="wide",
)

BANCO_DADOS = Path(__file__).resolve().with_name("qualidade_ar.db")


def carregar_dados(limite=120):
    if not BANCO_DADOS.exists():
        return pd.DataFrame()

    # Abre o banco em modo somente leitura e fecha a conexão antes de renderizar.
    conn = sqlite3.connect(f"{BANCO_DADOS.as_uri()}?mode=ro", uri=True, timeout=10)
    try:
        tabela = conn.execute('''
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'leituras_sensores'
        ''').fetchone()
        if tabela is None:
            return pd.DataFrame()

        df = pd.read_sql_query('''
            SELECT id, timestamp, sala_id, co2, pm25, umidade, temperatura
            FROM leituras_sensores
            ORDER BY id DESC
            LIMIT ?
        ''', conn, params=(limite,))
    finally:
        conn.close()

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.sort_values(["timestamp", "id"])


def exibir_grafico(df, metrica, titulo, unidade):
    figura = px.line(
        df,
        x="timestamp",
        y=metrica,
        color="sala_id",
        title=titulo,
        markers=True,
        labels={"timestamp": "Horário", metrica: unidade, "sala_id": "Sala"},
        hover_data={"timestamp": "|%d/%m/%Y %H:%M:%S", metrica: ":.2f"},
    )
    figura.update_xaxes(tickformat="%H:%M:%S")
    st.plotly_chart(figura)


st.title("🌿 Qualidade do Ar em Tempo Real")

st.sidebar.header("Filtros e Controles")
intervalo_atualizacao = st.sidebar.slider("Intervalo de atualização (segundos)", 1, 10, 2)
quantidade_registros = st.sidebar.slider("Total de leituras no histórico", 30, 300, 120)

df = carregar_dados(limite=quantidade_registros)
salas_disponiveis = sorted(df["sala_id"].unique()) if not df.empty else []
sala_selecionada = st.sidebar.selectbox("Filtrar por sala", ["Todos"] + salas_disponiveis)

if df.empty:
    st.info("Aguardando leituras. Execute `simulator.py` para iniciar a simulação.")
else:
    df_filtrado = df if sala_selecionada == "Todos" else df[df["sala_id"] == sala_selecionada]

    st.subheader("Últimas leituras por sala")
    ultimos = df_filtrado.groupby("sala_id").last().reset_index()
    for coluna, (_, leitura) in zip(st.columns(len(ultimos)), ultimos.iterrows()):
        with coluna:
            st.markdown(f"### {leitura['sala_id']}")
            st.metric("CO₂", f"{leitura['co2']:.2f} ppm")
            st.metric("Material particulado PM2,5", f"{leitura['pm25']:.2f} µg/m³")
            st.metric("Umidade relativa", f"{leitura['umidade']:.2f} %")
            st.metric("Temperatura", f"{leitura['temperatura']:.2f} °C")

    coluna_co2, coluna_pm25 = st.columns(2)
    with coluna_co2:
        exibir_grafico(df_filtrado, "co2", "Concentração de CO₂ ao longo do tempo", "CO₂ (ppm)")
    with coluna_pm25:
        exibir_grafico(df_filtrado, "pm25", "Concentração de PM2,5 ao longo do tempo", "PM2,5 (µg/m³)")

    with st.expander("Visualizar tabela de registros"):
        st.dataframe(
            df_filtrado.sort_values(["timestamp", "id"], ascending=False),
            hide_index=True,
            column_order=["timestamp", "sala_id", "co2", "pm25", "umidade", "temperatura"],
            column_config={
                "timestamp": st.column_config.DatetimeColumn("Horário", format="DD/MM/YYYY HH:mm:ss"),
                "sala_id": "Sala",
                "co2": st.column_config.NumberColumn("CO₂ (ppm)", format="%.2f"),
                "pm25": st.column_config.NumberColumn("PM2,5 (µg/m³)", format="%.2f"),
                "umidade": st.column_config.NumberColumn("Umidade (%)", format="%.2f"),
                "temperatura": st.column_config.NumberColumn("Temperatura (°C)", format="%.2f"),
            },
        )

time.sleep(intervalo_atualizacao)
st.rerun()
