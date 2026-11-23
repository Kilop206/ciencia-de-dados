import random
import sqlite3
import time
from datetime import datetime

DB_NAME = "telemetria_fabril.db"


def obter_turno(hora):
    if 6 <= hora < 14:
        return "Manhã"
    elif 14 <= hora < 22:
        return "Tarde"
    return "Noite"


def init_db():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    cursor = conn.cursor()
    # Modo WAL obrigatório para concorrência segura entre escrita e leitura
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leituras_sensores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            id_maquina TEXT,
            turno TEXT,
            temperatura_operacao_c REAL,
            vibracao_mms REAL,
            corrente_eletrica_a REAL,
            rotacao_rpm REAL,
            pressao_hidraulica_bar REAL
        );
    ''')
    conn.commit()
    conn.close()


def simular_sensores():
    init_db()
    print(f"Simulador industrial iniciado ({DB_NAME}). Pressione Ctrl+C para encerrar.")

    # Estado base das 5 máquinas conforme o dataset original
    maquinas = {
        "Torno_CNC_01":         {"temp": 71.0, "vib": 4.2, "corr": 39.0, "rpm": 1495.0, "press": 115.0},
        "Prensa_Hidraulica_02": {"temp": 75.0, "vib": 4.3, "corr": 32.0, "rpm": 1495.0, "press": 152.0},
        "Fresadora_CNC_03":     {"temp": 66.0, "vib": 5.5, "corr": 46.0, "rpm": 1495.0, "press": 145.0},
        "Injetora_Plastico_04": {"temp": 72.0, "vib": 2.0, "corr": 40.0, "rpm": 1495.0, "press": 158.0},
        "Robo_Solda_05":        {"temp": 82.0, "vib": 3.2, "corr": 41.0, "rpm": 1495.0, "press": 88.0},
    }

    while True:
        try:
            conn = sqlite3.connect(DB_NAME, timeout=10)
            cursor = conn.cursor()

            agora = datetime.now()
            timestamp = agora.strftime("%Y-%m-%d %H:%M:%S")
            turno = obter_turno(agora.hour)

            for id_maquina, estado in maquinas.items():
                # 15% de chance de ocorrer um pico de sobrecarga térmica/vibracional
                pico_sobrecarga = random.random() < 0.15

                if pico_sobrecarga:
                    temp = round(random.uniform(92.0, 112.0), 2)
                    vib = round(random.uniform(7.5, 11.5), 2)
                    corr = round(random.uniform(52.0, 68.0), 2)
                    rpm = round(estado["rpm"] + random.uniform(-120.0, -30.0), 2)
                    press = round(estado["press"] + random.uniform(15.0, 35.0), 2)
                else:
                    # Oscilação suave em regime normal de operação
                    temp = round(max(55.0, min(88.0, estado["temp"] + random.uniform(-1.2, 1.2))), 2)
                    vib = round(max(0.8, min(6.2, estado["vib"] + random.uniform(-0.35, 0.35))), 2)
                    corr = round(max(25.0, min(49.0, estado["corr"] + random.uniform(-1.5, 1.5))), 2)
                    rpm = round(max(1350.0, min(1600.0, estado["rpm"] + random.uniform(-8.0, 8.0))), 2)
                    press = round(max(75.0, min(170.0, estado["press"] + random.uniform(-2.5, 2.5))), 2)

                    estado["temp"] = temp
                    estado["vib"] = vib
                    estado["corr"] = corr
                    estado["rpm"] = rpm
                    estado["press"] = press

                cursor.execute('''
                    INSERT INTO leituras_sensores (
                        timestamp, id_maquina, turno,
                        temperatura_operacao_c, vibracao_mms,
                        corrente_eletrica_a, rotacao_rpm, pressao_hidraulica_bar
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (timestamp, id_maquina, turno, temp, vib, corr, rpm, press))

            conn.commit()
            conn.close()

            print(f"[{agora.strftime('%H:%M:%S')}] Leituras gravadas para 5 máquinas (Turno: {turno})")
            time.sleep(2)

        except sqlite3.OperationalError as e:
            print(f"Aviso de concorrência SQLite: {e}")
            time.sleep(1)

        except KeyboardInterrupt:
            print("\nSimulação encerrada pelo usuário.")
            break


if __name__ == "__main__":
    simular_sensores()