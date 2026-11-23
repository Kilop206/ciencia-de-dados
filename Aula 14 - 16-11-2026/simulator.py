import random
import sqlite3
import time

from datetime import datetime


def init_db():
    conn = sqlite3.connect("sensores.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS leituras_sensores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            sensor_id TEXT,
            temperatura REAL,
            umidade REAL,
            pressao REAL
        );
    ''')
    conn.commit()
    conn.close()

def simular_sensores() :
    init_db()
    print("Simulador de sensores em execução. Pressione Ctrl+C para encerrar")

    sensores = {
        'Sensor_A':  {'temp': 24.0, 'umid': 55.0, 'press': 1013.25},
        'Sensor_B':  {'temp': 28.5, 'umid': 48.0, 'press': 1012.80},
        'Sensor_C':  {'temp': 21.0, 'umid': 62.0, 'press': 1014.18}
    }

    while True :
        try :
            conn = sqlite3.connect('sensores.db', timeout=10)
            cursor = conn.cursor()

            for sensor_id, dados in sensores.items():
                # Simula pequena oscilação continua nos valores
                temp = round(dados['temp'] + random.uniform(-0.4, 0.4), 2)
                umid = round(max(0, min(100, dados['umid'] + random.uniform(-0.8, 0.8))), 2)
                press = round(dados['press'] + random.uniform(-0.15, 0.15), 2)

                dados['temp'] = temp
                dados['umid'] = umid
                dados['press'] = press

                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                cursor.execute('''
                    INSERT INTO leituras_sensores (timestamp, sensor_id, temperatura, umidade, pressao)
                    VALUES (?, ?, ?, ?, ?)
                ''', (timestamp, sensor_id, temp, umid, press))

            conn.commit()
            conn.close()

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Novas leituras inseridas")
            time.sleep(2)

        except sqlite3.OperationalError as e :
            print(f'Aviso de concorrência: {e}')
            time.sleep(1)

        except KeyboardInterrupt :
            print("\nSimulação finalizada.")
            break

if __name__ == "__main__" :
    simular_sensores()