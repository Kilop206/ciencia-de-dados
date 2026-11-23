"""Consome Kafka, valida os eventos e grava no InfluxDB (offset manual).

Sem transação distribuída Kafka/InfluxDB: oferece ao menos uma tentativa de
processamento, não uma garantia formal de exatamente-uma-vez.
"""
import logging
import os
import time
from datetime import datetime, timezone

from confluent_kafka import Consumer, Producer, TopicPartition
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from pipeline.schema import InvalidTelemetry, parse_telemetry

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("consumer")


def build_telemetry_point(data: dict) -> Point:
    # Mesmo evento repetido gera a MESMA série/timestamp e sobrescreve os fields.
    return (Point("iiot_telemetry")
            .tag("machine_id", data["machine_id"])
            .tag("line_id", data["line_id"])
            .field("temperature_c", data["temperature_c"])
            .field("vibration_mm_s", data["vibration_mm_s"])
            .field("current_a", data["current_a"])
            .field("alert", data["alert"])
            .time(data["timestamp"], WritePrecision.NS))


def build_quality_point(outcome: str) -> Point:
    return (Point("pipeline_events")
            .tag("outcome", outcome)
            .field("count", 1)
            .time(time.time_ns(), WritePrecision.NS))


def send_dlq(producer: Producer, topic: str, original: bytes, reason: str):
    """Publica original na DLQ. Só retorna após confirmação de entrega."""
    errors = []
    def on_delivery(err, msg):
        if err is not None:
            errors.append(str(err))
    producer.produce(topic, value=original, headers={"reason": reason[:500]},
                     on_delivery=on_delivery)
    outstanding = producer.flush(timeout=15)
    if errors or outstanding:
        raise RuntimeError(f"DLQ não confirmada: {errors}, pendentes={outstanding}")


def process_message(message: bytes, write_api, bucket: str, org: str,
                    dlq_producer: Producer, dlq_topic: str) -> str:
    try:
        data = parse_telemetry(message)
    except InvalidTelemetry as exc:
        # Persistir qualidade e enviar à DLQ; se algo falhar, offset NÃO será confirmado.
        write_api.write(bucket=bucket, org=org, record=build_quality_point("invalid"))
        send_dlq(dlq_producer, dlq_topic, message, str(exc))
        log.warning("Evento inválido -> DLQ: %s", exc)
        return "invalid"
    write_api.write(bucket=bucket, org=org,
                    record=[build_telemetry_point(data), build_quality_point("accepted")])
    if data["alert"]:
        log.warning("ANOMALIA: máquina %s temp=%s vib=%s corrente=%s",
                    data["machine_id"], data["temperature_c"],
                    data["vibration_mm_s"], data["current_a"])
    else:
        log.info("Persistido %s temp=%.1f°C", data["machine_id"], data["temperature_c"])
    return "accepted"


def main():
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = os.getenv("KAFKA_TOPIC", "iiot.raw.telemetry")
    dlq = os.getenv("KAFKA_DLQ_TOPIC", "iiot.invalid.telemetry")
    group = os.getenv("KAFKA_GROUP_ID", "iiot-influx-writers")
    org = os.getenv("INFLUXDB_ORG", "grupo3")
    bucket = os.getenv("INFLUXDB_BUCKET", "industrial")
    token = os.environ["INFLUXDB_TOKEN"]
    client = Consumer({"bootstrap.servers": bootstrap, "group.id": group,
                       "enable.auto.commit": False,
                       "auto.offset.reset": "earliest"})
    dlq_producer = Producer({"bootstrap.servers": bootstrap,
                             "acks": "all", "enable.idempotence": True})
    with InfluxDBClient(url=os.getenv("INFLUXDB_URL", "http://localhost:8086"),
                        token=token, org=org, timeout=10000) as influx:
        writer = influx.write_api(write_options=SYNCHRONOUS)
        client.subscribe([topic])
        log.info("Aguardando %s em %s", topic, bootstrap)
        try:
            while True:
                msg = client.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    log.error("Kafka: %s", msg.error())
                    continue
                try:
                    process_message(msg.value() or b"", writer, bucket, org,
                                    dlq_producer, dlq)
                    client.commit(message=msg, asynchronous=False)
                except Exception as exc:
                    log.exception("Falha no destino/offset, repetir o evento: %s", exc)
                    try:
                        client.seek(TopicPartition(msg.topic(), msg.partition(), msg.offset()))
                    except Exception as seek_exc:
                        log.warning("Seek falhou (rebalance?): %s", seek_exc)
                        # Não confirmar mensagens posteriores em uma partição com falha.
                        raise
                    time.sleep(3)
        except KeyboardInterrupt:
            log.info("Consumer encerrado")
        finally:
            client.close()
            dlq_producer.flush(10)


if __name__ == "__main__":
    main()
