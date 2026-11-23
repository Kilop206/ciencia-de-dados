import sqlite3
import time
from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Monitoramento Industrial & IA",
    page_icon="🏭",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
BANCO_DADOS = BASE_DIR / "telemetria_fabril.db"
MODELO_ENERGIA_PATH = BASE_DIR / "modelo_regressao_energia.pkl"
MODELO_FALHA_PATH = BASE_DIR / "modelo_arvore_falha.pkl"

FEATURES = [
    "temperatura_operacao_c",
    "vibracao_mms",
    "corrente_eletrica_a",
    "rotacao_rpm",
    "pressao_hidraulica_bar",
]


@st.cache_resource
def carregar_modelos():
    modelo_energia = joblib.load(MODELO_ENERGIA_PATH)
    modelo_falha = joblib.load(MODELO_FALHA_PATH)
    return modelo_energia, modelo_falha


def carregar_dados(limite=150):
    if not BANCO_DADOS.exists():
        return pd.DataFrame()

    conn = sqlite3.connect(f"{BANCO_DADOS.as_uri()}?mode=ro", uri=True, timeout=10)
    try:
        tabela = conn.execute('''
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'leituras_sensores'
        ''').fetchone()
        if tabela is None:
            return pd.DataFrame()

        df = pd.read_sql_query('''
            SELECT id, timestamp, id_maquina, turno,
                   temperatura_operacao_c, vibracao_mms,
                   corrente_eletrica_a, rotacao_rpm, pressao_hidraulica_bar
            FROM leituras_sensores
            ORDER BY id DESC
            LIMIT ?
        ''', conn, params=(limite,))
    finally:
        conn.close()

    if df.empty:
        return df

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.sort_values(["timestamp", "id"]).reset_index(drop=True)


def aplicar_inferencia(df, modelo_energia, modelo_falha):
    X = df[FEATURES]
    df["consumo_previsto_kwh"] = modelo_energia.predict(X)
    # .round().astype(int) garante compatibilidade caso o modelo seja Classifier ou Regressor
    df["status_falha_previsto"] = modelo_falha.predict(X).round().astype(int)
    df["situacao"] = df["status_falha_previsto"].map({0: "Operação Normal", 1: "Alerta de Falha"})
    return df


def exibir_grafico(df, metrica, titulo, unidade):
    figura = px.line(
        df,
        x="timestamp",
        y=metrica,
        color="id_maquina",
        title=titulo,
        markers=True,
        labels={"timestamp": "Horário", metrica: unidade, "id_maquina": "Equipamento"},
        hover_data={"timestamp": "|%d/%m/%Y %H:%M:%S", metrica: ":.2f"},
    )
    figura.update_xaxes(tickformat="%H:%M:%S")
    st.plotly_chart(figura, use_container_width=True)


st.title("🏭 Monitoramento Industrial em Tempo Real com IA")

# Carregar modelos de IA
if not MODELO_ENERGIA_PATH.exists() or not MODELO_FALHA_PATH.exists():
    st.error("Modelos `.pkl` não encontrados. Execute primeiro a Etapa 2 (`train_models.py`).")
    st.stop()

modelo_energia, modelo_falha = carregar_modelos()

# Barra lateral (Sidebar)
st.sidebar.header("Filtros e Controles")
intervalo_atualizacao = st.sidebar.slider("Intervalo de atualização (segundos)", 1, 10, 2)
quantidade_registros = st.sidebar.slider("Total de leituras no histórico", 50, 300, 150)

df = carregar_dados(limite=quantidade_registros)
maquinas_disponiveis = sorted(df["id_maquina"].unique()) if not df.empty else []
maquina_selecionada = st.sidebar.selectbox("Filtrar por equipamento", ["Todas"] + maquinas_disponiveis)

if df.empty:
    st.info("Aguardando telemetria. Execute `python simulator.py` em outro terminal para iniciar.")
else:
    df = aplicar_inferencia(df, modelo_energia, modelo_falha)
    df_filtrado = df if maquina_selecionada == "Todas" else df[df["id_maquina"] == maquina_selecionada]

    # Última leitura de cada equipamento filtrado
    ultimos = df_filtrado.groupby("id_maquina").last().reset_index()

    # Banners de Alerta Operacional
    maquinas_em_falha = ultimos[ultimos["status_falha_previsto"] == 1]["id_maquina"].tolist()
    if maquinas_em_falha:
        st.error(
            f"🚨 ALERTA DE RISCO DE FALHA DETECTADO PELA IA: **{', '.join(maquinas_em_falha)}** — "
            "Verifique temperatura, vibração e carga operacional imediatamente!"
        )
    else:
        st.success("✅ Todos os equipamentos monitorados operam dentro dos parâmetros normais.")

    # KPIs por equipamento
    st.subheader("Indicadores Operacionais em Tempo Real")
    colunas_kpi = st.columns(len(ultimos))
    for coluna, (_, leitura) in zip(colunas_kpi, ultimos.iterrows()):
        with coluna:
            icone_status = "🔴" if leitura["status_falha_previsto"] == 1 else "🟢"
            st.markdown(f"#### {icone_status} {leitura['id_maquina']}")
            st.caption(f"Status IA: **{leitura['situacao']}** | Turno: {leitura['turno']}")
            st.metric("Temperatura", f"{leitura['temperatura_operacao_c']:.2f} °C")
            st.metric("Vibração", f"{leitura['vibracao_mms']:.2f} mm/s")
            st.metric("Corrente Elétrica", f"{leitura['corrente_eletrica_a']:.2f} A")
            st.metric("Consumo Previsto", f"{leitura['consumo_previsto_kwh']:.2f} kWh")

    st.divider()

    # Gráficos Temporais Interativos (Plotly)
    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
        exibir_grafico(
            df_filtrado,
            "consumo_previsto_kwh",
            "Consumo Energético Previsto (kWh) ao Longo do Tempo",
            "Consumo (kWh)",
        )
    with col_graf2:
        exibir_grafico(
            df_filtrado,
            "temperatura_operacao_c",
            "Evolução da Temperatura de Operação (°C)",
            "Temperatura (°C)",
        )

    exibir_grafico(
        df_filtrado,
        "vibracao_mms",
        "Evolução da Vibração Mecânica (mm/s)",
        "Vibração (mm/s)",
    )

    # Tabela expansível com dados brutos + predições
    with st.expander("Visualizar tabela de leituras e predições em tempo real"):
        st.dataframe(
            df_filtrado.sort_values(["timestamp", "id"], ascending=False),
            hide_index=True,
            use_container_width=True,
            column_order=[
                "timestamp",
                "id_maquina",
                "turno",
                "situacao",
                "consumo_previsto_kwh",
                "temperatura_operacao_c",
                "vibracao_mms",
                "corrente_eletrica_a",
                "rotacao_rpm",
                "pressao_hidraulica_bar",
            ],
            column_config={
                "timestamp": st.column_config.DatetimeColumn("Horário", format="DD/MM/YYYY HH:mm:ss"),
                "id_maquina": "Equipamento",
                "turno": "Turno",
                "situacao": "Diagnóstico IA",
                "consumo_previsto_kwh": st.column_config.NumberColumn("Consumo Previsto (kWh)", format="%.2f"),
                "temperatura_operacao_c": st.column_config.NumberColumn("Temperatura (°C)", format="%.2f"),
                "vibracao_mms": st.column_config.NumberColumn("Vibração (mm/s)", format="%.2f"),
                "corrente_eletrica_a": st.column_config.NumberColumn("Corrente (A)", format="%.2f"),
                "rotacao_rpm": st.column_config.NumberColumn("Rotação (RPM)", format="%.2f"),
                "pressao_hidraulica_bar": st.column_config.NumberColumn("Pressão (bar)", format="%.2f"),
            },
        )

time.sleep(intervalo_atualizacao)
st.rerun()
