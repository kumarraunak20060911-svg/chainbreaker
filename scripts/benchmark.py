from chainbreaker.web.app import demo_run


if __name__ == "__main__":
    run = demo_run()
    print({"events": len(run["events"]), "findings": len(run["findings"]), "links": len(run["links"]), "chains": len(run["chains"])})
