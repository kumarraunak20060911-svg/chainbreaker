from chainbreaker.ingest.service import ingest_rows_diagnostics


def test_ingest_keeps_valid_rows_and_reports_invalid_rows_and_corrections():
    rows = [
        {"timestamp": "2026-10-24T02:10:00+00:00", "source": "auth", "event_type": "login_success", "ip": "10.0.0.8", "clock_offset_seconds": "2"},
        {"timestamp": "not-a-time", "source": "dns", "event_type": "dns_query"},
    ]
    events, diagnostics = ingest_rows_diagnostics(rows)
    assert len(events) == 1
    assert len(diagnostics.rejected_rows) == 1
    assert diagnostics.clock_offsets["auth"] == 2.0
    assert events[0].metadata["pseudonymized"] is True
    assert events[0].metadata.get("public_wifi_nat") is not True
