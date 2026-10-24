def shared_field_pairs(events):
    pairs = []
    for index, left in enumerate(events):
        for right in events[index + 1:]:
            fields = ("account", "ip", "host", "device_id", "session_id", "domain")
            if any(getattr(left, field) and getattr(left, field) == getattr(right, field) for field in fields):
                pairs.append((left.event_id, right.event_id))
    return pairs


def shared_field_pairs_with_metadata(events):
    pairs = []
    for left, right in ((events[i], events[j]) for i in range(len(events)) for j in range(i + 1, len(events))):
        fields = ("account", "ip", "host", "device_id", "session_id", "domain")
        shared = [field for field in fields if getattr(left, field) and getattr(left, field) == getattr(right, field)]
        if shared:
            pairs.append({"left": left.event_id, "right": right.event_id, "fields": tuple(shared), "public_wifi_nat": bool(left.metadata.get("public_wifi_nat"))})
    return pairs
