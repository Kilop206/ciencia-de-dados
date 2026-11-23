from fastapi.testclient import TestClient
from iiot_api import app as api_module


def test_api_returns_multiple_industrial_events():
    with api_module._lock:
        api_module._scenarios.clear()
    client = TestClient(api_module.app)
    r = client.get("/api/v1/telemetry")
    assert r.status_code == 200
    data = r.json()
    assert data["source"] == "iiot-simulator"
    assert len(data["events"]) >= 1


def test_inject_overheat_and_invalid():
    client = TestClient(api_module.app)
    with api_module._lock:
        api_module._scenarios.clear()
    assert client.post("/api/v1/scenarios/overheat").status_code == 200
    data = client.get("/api/v1/telemetry").json()
    assert data["events"][0]["temperature_c"] == 95.0
    assert client.post("/api/v1/scenarios/invalid").status_code == 200
    data = client.get("/api/v1/telemetry").json()
    assert data["events"][0]["temperature_c"] == "ERRO_SENSOR"


def test_duplicate_preserves_id_and_timestamp():
    client = TestClient(api_module.app)
    with api_module._lock:
        api_module._scenarios.clear()
    normal = client.get("/api/v1/telemetry").json()["events"][0]
    client.post("/api/v1/scenarios/duplicate")
    repeated = client.get("/api/v1/telemetry").json()["events"][0]
    assert repeated == normal


def test_reject_unknown_scenario():
    assert TestClient(api_module.app).post("/api/v1/scenarios/foo").status_code == 400
