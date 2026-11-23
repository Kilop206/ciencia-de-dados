from datetime import datetime, timezone
import json
import pytest

from pipeline.schema import InvalidTelemetry, parse_telemetry
from iiot_api.app import generate_event


def base():
    return {
        "event_id": "abc", "machine_id": "MAQ-01", "line_id": "linha-01",
        "timestamp": "2026-10-26T12:00:00Z",
        "temperature_c": 62.5, "vibration_mm_s": 2.0, "current_a": 12.0,
    }


def test_parse_bytes_and_utc():
    data = parse_telemetry(json.dumps(base()).encode())
    assert data["timestamp"] == datetime(2026,10,26,12,tzinfo=timezone.utc)
    assert data["alert"] == 0


@pytest.mark.parametrize("field,value", [
    ("temperature_c", "BAD"), ("current_a", -10), ("vibration_mm_s", False),
    ("temperature_c", float("nan")), ("machine_id", ""),
    ("timestamp", "2026-10-26T12:00:00"),
])
def test_reject_invalid(field,value):
    event = base()
    event[field] = value
    with pytest.raises(InvalidTelemetry):
        parse_telemetry(event)


def test_reject_malformed_json():
    with pytest.raises(InvalidTelemetry):
        parse_telemetry(b"broken")


def test_overheat_triggers_alert():
    data = parse_telemetry({**base(), "temperature_c": 95})
    assert data["alert"] == 1


def test_vibration_triggers_alert():
    data = parse_telemetry({**base(), "vibration_mm_s": 9.2})
    assert data["alert"] == 1


def test_generate_event_has_expected_fields():
    data = parse_telemetry(generate_event("MAQ-03"))
    assert data["machine_id"] == "MAQ-03"
