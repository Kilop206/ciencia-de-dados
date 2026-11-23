"""Verifica o backlog por partição do consumer group (executar no host após pip install)."""
import argparse
from confluent_kafka import Consumer, TopicPartition


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bootstrap", default="localhost:9092")
    p.add_argument("--group", default="iiot-influx-writers")
    p.add_argument("--topic", default="iiot.raw.telemetry")
    args = p.parse_args()
    consumer = Consumer({"bootstrap.servers": args.bootstrap, "group.id": args.group})
    try:
        topic = consumer.list_topics(args.topic, timeout=10).topics[args.topic]
        partitions = [TopicPartition(args.topic, idx) for idx in topic.partitions]
        committed = consumer.committed(partitions, timeout=10)
        for p in committed:
            low, high = consumer.get_watermark_offsets(p, timeout=10)
            if p.offset < 0:
                print(f"partição {p.partition}: sem offset confirmado (high={high})")
            else:
                print(f"partição {p.partition}: lag={max(0, high-p.offset)} high={high} commit={p.offset}")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
