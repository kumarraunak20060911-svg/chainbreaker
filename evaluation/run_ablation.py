from chainbreaker.correlation.service import build_links
from chainbreaker.ingest.service import ingest_rows
from chainbreaker.scenarios.benign_cases import benign_case_names
from chainbreaker.scenarios.generator import central_district_rows
try:
    from evaluation.baselines.naive_linker import shared_field_pairs
except ModuleNotFoundError:
    from baselines.naive_linker import shared_field_pairs


def ablation() -> dict[str, object]:
    rows = central_district_rows()
    events = ingest_rows(rows)
    weighted = build_links(events)
    naive = shared_field_pairs(events)
    dropped = {}
    for field in ("ip", "peer", "account"):
        modified = [{key: value for key, value in row.items() if key != field} for row in rows]
        dropped[field] = len(build_links(ingest_rows(modified)))
    nat_rows = [dict(row, network_zone="public-wifi", public_wifi_nat="true") for row in rows if row.get("ip")][:3]
    nat_events = ingest_rows(nat_rows)
    nat_naive = len(shared_field_pairs(nat_events))
    nat_weighted = len(build_links(nat_events))
    return {
        "baseline": {"name": "weighted-evidence-linking", "links": len(weighted)},
        "comparison": {"name": "shared-field-linking", "links": len(naive)},
        "public_wifi_nat": {"naive_links": nat_naive, "weighted_links": nat_weighted},
        "dropped_fields": dropped,
        "stage_prior": {"on": True, "off": "documented comparison toggle"},
        "clock_skew_correction": {"on": True, "off": "explicit offsets can be omitted"},
        "near_misses": benign_case_names(),
    }


if __name__ == "__main__":
    print(ablation())
