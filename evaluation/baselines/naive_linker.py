def shared_field_pairs(events):
    pairs = []
    for index, left in enumerate(events):
        for right in events[index + 1:]:
            fields = ("account", "ip", "host", "device_id", "session_id", "domain")
            if any(getattr(left, field) and getattr(left, field) == getattr(right, field) for field in fields):
                pairs.append((left.event_id, right.event_id))
    return pairs
