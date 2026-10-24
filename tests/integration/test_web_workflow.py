from fastapi.testclient import TestClient

from chainbreaker.api.app import app
from chainbreaker.web.app import demo_run


def test_dashboard_exposes_metrics_replay_and_logged_human_decision():
    run = demo_run()
    client = TestClient(app)
    assert client.get("/").status_code == 200
    assert client.get("/metrics").status_code == 200
    assert client.get("/resilience").status_code == 200
    assert client.get("/recreate").status_code == 200
    assert client.get("/database").status_code == 200
    assert client.get("/history").status_code == 200
    assert client.get(f"/api/incidents/{run['run_id']}/stix").status_code == 200
    assert client.get(f"/api/incidents/{run['run_id']}/sigma").status_code == 200
    assert client.get(f"/runs/{run['run_id']}/replay").status_code == 200
    response = client.post(
        f"/api/incidents/{run['run_id']}/containment/decisions",
        json={"action_id": run["containment"].recommended_action_id, "decision": "deferred", "actor": "analyst-1", "reason": "reviewing service impact"},
    )
    assert response.status_code == 200
    assert response.json()["executed"] is False
