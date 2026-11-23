"""Verifica API, saúde InfluxDB e Grafana via HTTP (sem dependências externas)."""
import json
import sys
import urllib.request

TARGETS = {
    "API IIoT": "http://localhost:8000/healthz",
    "InfluxDB": "http://localhost:8086/health",
    "Grafana": "http://localhost:3000/api/health",
}


def main():
    errors = 0
    for name, url in TARGETS.items():
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.load(response)
                print(f"[OK] {name}: {data}")
        except Exception as exc:
            print(f"[FALHOU] {name}: {exc}")
            errors += 1
    if errors:
        print("Obs.: Kafka deve ser verificado com 'docker compose ps' ou seus logs.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
