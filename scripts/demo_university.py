from chainbreaker.scenarios.generator import university_security_rows
from chainbreaker.web.app import process_rows


if __name__ == "__main__":
    rows = university_security_rows()
    run = process_rows(rows, persist=False)
    print({"synthetic": True, "events": len(run["events"]), "findings": len(run["findings"]), "links": len(run["links"]), "chains": len(run["chains"]), "rejected_rows": len(run["diagnostics"].rejected_rows), "duplicate_candidates": 1})
