"""Consulta uma API HTTP IIoT e publica cada evento bruto no Apache Kafka."""
import json
import logging
import os
import time

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("publisher")


def validate_api_response(data: object) -> list[dict]:
    if not isinstance(data, dict) or not isinstance(data.get("events"), list):
        raise ValueError("API deve retornar um objeto com lista 'events'")
    if not all(isinstance(event, dict) for event in data["events"]):
        raise ValueError("Cada item de 'events' deve ser um objeto")
    return data["events"]


def main():
    from confluent_kafka import Producer
    api_url = os.getenv("IIOT_API_URL", "http://localhost:8000/api/v1/telemetry")
    interval = max(.1, float(os.getenv("POLL_INTERVAL_SECONDS", "1")))
    topic = os.getenv("KAFKA_TOPIC", "iiot.raw.telemetry")
    server = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    producer = Producer({"bootstrap.servers": server, "client.id": "iiot-http-publisher",
                         "acks": "all", "enable.idempotence": True,
                         "message.timeout.ms": 15000})
    session = requests.Session()
    try:
        while True:
            try:
                response = session.get(api_url, timeout=5)
                response.raise_for_status()
                events = validate_api_response(response.json())
                errors = []
                def callback(error, message):
                    if error is not None:
                        errors.append(str(error))
                for event in events:
                    producer.produce(topic, key=str(event.get("machine_id", "UNKNOWN")),
                                     value=json.dumps(event).encode("utf-8"), on_delivery=callback)
                outstanding = producer.flush(timeout=20)
                if outstanding or errors:
                    raise RuntimeError(f"Mensagens pendentes={outstanding}, erros={errors}")
                log.info("API -> Kafka: %d eventos publicados (topic=%s)", len(events), topic)
            except (requests.RequestException, ValueError, RuntimeError, BufferError) as exc:
                log.warning("Falha de publicação (nova tentativa no próximo ciclo): %s", exc)
            time.sleep(interval)
    except KeyboardInterrupt:
        log.info("Publisher interrompido")
    finally:
        producer.flush(10)
        session.close()


if __name__ == "__main__":
    main()
