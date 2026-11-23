"""Criação explícita dos tópicos, usando apenas um broker (demo)."""
import logging
import os
import time

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("kafka-init")


def main():
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    names = [os.getenv("KAFKA_TOPIC", "iiot.raw.telemetry"),
             os.getenv("KAFKA_DLQ_TOPIC", "iiot.invalid.telemetry")]
    for attempt in range(1, 31):
        try:
            admin = AdminClient({"bootstrap.servers": bootstrap, "socket.timeout.ms": 5000})
            fs = admin.create_topics([NewTopic(name, num_partitions=3,
                                               replication_factor=1) for name in names],
                                     operation_timeout=10)
            for topic, future in fs.items():
                try:
                    future.result(timeout=20)
                    logger.info("Tópico criado: %s", topic)
                except KafkaException as exc:
                    if "TOPIC_ALREADY_EXISTS" in str(exc):
                        logger.info("Tópico já existe: %s", topic)
                    else:
                        raise
            return
        except Exception as exc:
            logger.warning("Kafka não pronto (%s/30): %s", attempt, exc)
            time.sleep(3)
    raise RuntimeError("Não foi possível criar os tópicos Kafka")


if __name__ == "__main__":
    main()
