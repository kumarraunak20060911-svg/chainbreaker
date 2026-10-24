from chainbreaker.web.app import demo_run


def benchmark() -> dict[str, float]:
    run = demo_run()
    return {"events": float(len(run["events"])), "findings": float(len(run["findings"])), "links": float(len(run["links"])), "chains": float(len(run["chains"]))}


if __name__ == "__main__":
    print(benchmark())
