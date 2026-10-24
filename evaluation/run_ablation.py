from chainbreaker.scenarios.benign_cases import benign_case_names


def ablation() -> dict[str, object]:
    return {"baseline": "weighted-evidence-linking", "comparison": "shared-field-linking", "near_misses": benign_case_names()}


if __name__ == "__main__":
    print(ablation())
