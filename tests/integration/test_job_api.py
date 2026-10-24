import io

from fastapi.testclient import TestClient

from chainbreaker.api.app import app


def test_job_api_rejects_cross_tenant_lookup():
    client = TestClient(app)
    response = client.get("/api/jobs/nonexistent", headers={"X-Organization-ID": "another-org"})
    assert response.status_code == 404


def test_event_api_validates_pagination():
    client = TestClient(app)
    response = client.get("/api/events?limit=10000")
    assert response.status_code == 422
