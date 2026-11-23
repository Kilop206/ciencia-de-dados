"""Enfileira um cenário na API simulada (stdlib; sem dependências externas)."""
import argparse
import json
import urllib.request


def main():
    parser = argparse.ArgumentParser(description="Injetar falha na próxima leitura da API IIoT")
    parser.add_argument("scenario", choices=["overheat", "vibration", "invalid", "duplicate"])
    parser.add_argument("--api", default="http://localhost:8000")
    args = parser.parse_args()
    request = urllib.request.Request(
        f"{args.api.rstrip('/')}/api/v1/scenarios/{args.scenario}", data=b"{}",
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=5) as response:
        print(json.dumps(json.load(response), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
