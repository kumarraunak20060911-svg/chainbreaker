from chainbreaker.web.app import process_rows
from chainbreaker.scenarios.generator import central_district_rows


def test_demo_pipeline_produces_investigable_result():
    run = process_rows(central_district_rows())
    assert len(run["events"]) == 9
    assert run["findings"]
    assert run["links"]
    assert run["chains"]
