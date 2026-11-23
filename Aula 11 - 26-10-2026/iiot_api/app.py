"""API HTTP de telemetria IIoT simulada para uma apresentação reproduzível.

Todas as leituras são fictícias; NÃO representa equipamento industrial real.
"""
import os
import random
from collections import deque
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, HTTPException

app = FastAPI(title="IIoT Simulator API - Grupo 3", version="1.0.0")
_scenarios: deque[str] = deque()
_lock = Lock()
_last_event: dict | None = None
VALID_SCENARIOS = {"overheat", "vibration", "invalid", "duplicate"}


def generate_event(machine_id: str, scenario: str = "normal") -> dict:
    """Gera telemetria com timestamp UTC e ID único."""
    result = {
        "event_id": str(uuid4()),
        "machine_id": machine_id,
        "line_id": "linha-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": round(random.uniform(48, 72), 2),
        "vibration_mm_s": round(random.uniform(1.0, 4.1), 2),
        "current_a": round(random.uniform(6, 13), 2),
    }
    if scenario == "overheat":
        result["temperature_c"] = 95.0
    elif scenario == "vibration":
        result["vibration_mm_s"] = 9.2
    elif scenario == "invalid":
        result["temperature_c"] = "ERRO_SENSOR"
    return result


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/api/v1/telemetry")
def telemetry():
    """Retorna uma amostra de cada máquina; cenário pendente sobrepõe um evento."""
    global _last_event
    with _lock:
        scenario = _scenarios.popleft() if _scenarios else "normal"
        if scenario == "duplicate" and _last_event is not None:
            return {"source": "iiot-simulator", "events": [dict(_last_event)]}
        machines = max(1, min(20, int(os.getenv("IIOT_MACHINE_COUNT", "3"))))
        events = [generate_event(f"MAQ-{i:02d}", scenario if i == 1 else "normal")
                  for i in range(1, machines + 1)]
        _last_event = dict(events[0])
        return {"source": "iiot-simulator", "events": events}


@app.post("/api/v1/scenarios/{scenario}")
def inject_scenario(scenario: str):
    """Enfileira um cenário a ser consumido na próxima requisição GET."""
    if scenario not in VALID_SCENARIOS:
        raise HTTPException(status_code=400, detail=f"Cenário inválido: {scenario}")
    with _lock:
        _scenarios.append(scenario)
        queued = len(_scenarios)
    return {"status": "queued", "scenario": scenario, "pending": queued}


@app.get("/api/v1/scenarios")
def scenarios():
    with _lock:
        return {"available": sorted(VALID_SCENARIOS), "pending": len(_scenarios)}
