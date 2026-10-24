def summarize(records):
    if not records:
        return {}
    return {key: sum(record[key] for record in records) / len(records) for key in records[0] if isinstance(records[0][key], (int, float))}
