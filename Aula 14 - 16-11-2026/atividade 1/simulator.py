import random
import sqlite3
import time

from datetime import datetime
from pathlib import Path


BANCO_DADOS = Path(__file__).resolve().with_name("qualidade_ar.db")


def init_db(conn):
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS leituras_sensores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            sala_id TEXT NOT NULL,
            co2 REAL NOT NULL,
            pm25 REAL NOT NULL,
            umidade REAL NOT NULL,
            temperatura REAL NOT NULL
        );
    ''')


def simular_sensores():
    salas = {
        "Sala A": {"co2": 650.0, "pm25": 12.0, "umidade": 55.0, "temperatura": 24.0},
        "Sala B": {"co2": 950.0, "pm25": 21.0, "umidade": 48.0, "temperatura": 26.5},
        "Sala C": {"co2": 520.0, "pm25": 7.0, "umidade": 62.0, "temperatura": 22.0},
    }

    conn = sqlite3.connect(BANCO_DADOS, timeout=10)
    try:
        init_db(conn)
        print("Simulador de qualidade do ar em execução. Pressione Ctrl+C para encerrar.")

        while True:
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                with conn:
                    for sala_id, dados in salas.items():
                        co2 = round(max(400, dados["co2"] + random.uniform(-22, 22)), 2)
                        pm25 = round(max(0, dados["pm25"] + random.uniform(-1.2, 1.2)), 2)
                        umidade = round(max(0, min(100, dados["umidade"] + random.uniform(-0.8, 0.8))), 2)
                        temperatura = round(dados["temperatura"] + random.uniform(-0.4, 0.4), 2)

                        conn.execute('''
                            INSERT INTO leituras_sensores
                                (timestamp, sala_id, co2, pm25, umidade, temperatura)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (timestamp, sala_id, co2, pm25, umidade, temperatura))

                        dados.update(co2=co2, pm25=pm25, umidade=umidade, temperatura=temperatura)

                print(f"[{timestamp}] Novas leituras inseridas")
                time.sleep(2)
            except sqlite3.OperationalError as erro:
                print(f"Erro ao gravar leituras: {erro}")
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nSimulação finalizada.")
    finally:
        conn.close()


if __name__ == "__main__":
    simular_sensores()
