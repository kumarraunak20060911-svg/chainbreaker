from chainbreaker.ingest.service import ingest_rows
from chainbreaker.settings import Settings
from chainbreaker.storage.engine import initialize_schema
from chainbreaker.storage.persistent import ensure_development_organization, persist_events
from chainbreaker.scenarios.generator import central_district_rows


def test_persistence_is_idempotent_and_tenant_scoped(tmp_path):
    settings = Settings(
        database_url=f"sqlite+pysqlite:///{tmp_path / 'chainbreaker.sqlite3'}",
        sqlite_test_url=f"sqlite+pysqlite:///{tmp_path / 'chainbreaker.sqlite3'}",
        upload_directory=tmp_path / "uploads",
        report_directory=tmp_path / "reports",
        environment="test",
    )
    initialize_schema(settings)
    assert ensure_development_organization(settings) == "dev-organization"
    events = ingest_rows(central_district_rows())
    accepted, duplicates = persist_events(events, "dev-organization", "job-1", settings=settings)
    accepted_again, duplicates_again = persist_events(events, "dev-organization", "job-2", settings=settings)
    assert accepted == len(events)
    assert duplicates == 0
    assert accepted_again == 0
    assert duplicates_again == len(events)
