from chainbreaker.correlation.link_weights import EvidenceLinkEngine, LinkObservation


def test_nat_is_heavily_penalized_and_calibration_reports_brier():
    engine = EvidenceLinkEngine({"ip": {"nat": 1000, "rare": 1}})
    nat = engine.score(LinkObservation("a", "b", "ip", "nat", 1, public_wifi_nat=True))
    rare = engine.score(LinkObservation("a", "c", "ip", "rare", 1, rare_external_ip=True))
    assert rare.weight > nat.weight
    report = engine.fit_isotonic([LinkObservation("a", "b", "ip", "nat", 1, 0, True), LinkObservation("a", "c", "ip", "rare", 1, 1, False)])
    assert report.samples == 2
    assert 0 <= report.brier_score <= 1
