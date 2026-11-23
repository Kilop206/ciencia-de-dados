import pytest
from pipeline.publisher import validate_api_response
from pipeline.schema import parse_telemetry
from iiot_api.app import generate_event


def test_publisher_accepts_api_contract():
    data = {"source": "iiot-simulator", "events": [generate_event("MAQ-01")]}
    events = validate_api_response(data)
    assert len(events) == 1
    assert parse_telemetry(events[0])["machine_id"] == "MAQ-01"


@pytest.mark.parametrize("data", [None, {}, {"events": "x"}, {"events": [123]}])
def test_publisher_rejects_invalid_api_contract(data):
    with pytest.raises(ValueError):
        validate_api_response(data)


def test_grafana_files_present():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    assert (root/"grafana/dashboards/industrial.json").is_file()
    assert (root/"grafana/provisioning/datasources/influxdb.yml").is_file()
