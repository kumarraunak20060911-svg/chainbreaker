from chainbreaker.ingest.service import ingest_rows_diagnostics
from chainbreaker.scenarios.generator import central_district_rows


def test_end_to_end_ingest_pipeline():
    raw_rows = central_district_rows()
    events, diagnostics = ingest_rows_diagnostics(raw_rows)

    assert len(events) == len(raw_rows)
    assert diagnostics.accepted_rows == len(raw_rows)
    assert len(diagnostics.rejected_rows) == 0

    # Test HMAC pseudonymization consistency
    account_events = [e for e in events if e.account]
    assert len(account_events) > 0
    # Every account should be a 16-hex char pseudonymized HMAC string
    for event in account_events:
        assert len(event.account) == 16
        assert event.account != "ops_k"  # Raw identity is never stored in cleartext
