import json
from fastapi.testclient import TestClient
from app.main import app

def test_kpis_contract_snapshot():
    client = TestClient(app)
    res = client.get('/v1/kpis')
    assert res.status_code == 200
    data = res.json()
    payload = json.dumps(data, sort_keys=True, separators=(',', ':'))
    import pathlib
    snap = pathlib.Path(__file__).parent / "__snapshots__" / "kpis.json"
    snap.parent.mkdir(exist_ok=True)
    if not snap.exists():
        snap.write_text(payload, encoding='utf-8')
    assert payload == snap.read_text(encoding='utf-8')