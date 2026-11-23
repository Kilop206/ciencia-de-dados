"""Validação e transformação puras para facilitar testes de unidade."""
import json
import math
from datetime import datetime, timezone


class InvalidTelemetry(ValueError):
    pass


def parse_telemetry(raw: bytes | str | dict) -> dict:
    if isinstance(raw, bytes):
        try:
            raw = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise InvalidTelemetry("payload não é UTF-8") from exc
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (json.JSONDecodeError, TypeError) as exc:
            raise InvalidTelemetry("JSON malformado") from exc
    if not isinstance(raw, dict):
        raise InvalidTelemetry("esperado objeto JSON")
    for key in ("event_id", "machine_id", "line_id", "timestamp"):
        if not isinstance(raw.get(key), str) or not raw[key].strip():
            raise InvalidTelemetry(f"campo obrigatório inválido: {key}")
    try:
        dt = datetime.fromisoformat(raw["timestamp"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise InvalidTelemetry("timestamp inválido") from exc
    if dt.tzinfo is None:
        raise InvalidTelemetry("timestamp precisa conter timezone")
    dt = dt.astimezone(timezone.utc)
    fields = {}
    bounds = {"temperature_c": (-40, 200), "vibration_mm_s": (0, 100), "current_a": (0, 200)}
    for name, (min_v, max_v) in bounds.items():
        value = raw.get(name)
        if isinstance(value, bool) or not isinstance(value, (float, int)):
            raise InvalidTelemetry(f"campo numérico inválido: {name}")
        if not math.isfinite(value) or not min_v <= value <= max_v:
            raise InvalidTelemetry(f"valor fora do intervalo: {name}")
        fields[name] = float(value)
    fields["alert"] = int(fields["temperature_c"] >= 80 or
                          fields["vibration_mm_s"] >= 6 or
                          fields["current_a"] >= 20)
    return {
        "event_id": raw["event_id"],
        "machine_id": raw["machine_id"],
        "line_id": raw["line_id"],
        "timestamp": dt,
        **fields,
    }
