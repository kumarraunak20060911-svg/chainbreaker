from dataclasses import asdict
from chainbreaker.ingest.merkle import MerkleTree
from chainbreaker.reporting.case_report import build_case_report
from chainbreaker.scenarios.generator import central_district_rows
from chainbreaker.ingest.service import ingest_rows
from chainbreaker.detection.service import detect_all
from chainbreaker.correlation.service import build_links
from chainbreaker.inference.service import infer_chains


def test_case_report_merkle_verification():
    events = ingest_rows(central_district_rows())
    findings = detect_all(events, {})
    links = build_links(events)
    chains = infer_chains(events, links)
    row_dicts = [asdict(event) for event in events]
    tree = MerkleTree(row_dicts)

    report = build_case_report("run-test-01", {"id": "inc-1"}, chains[0] if chains else {}, findings, links, tree.root)
    assert report["merkle_root"] == tree.root
    assert report["report_id"] == "report-run-test-01"
    proof = tree.proof(0)
    assert MerkleTree.verify(proof) is True
