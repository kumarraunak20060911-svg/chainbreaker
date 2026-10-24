def source_citations(events, event_ids):
    by_id = {event.event_id: event for event in events}
    return [event.row_id or event.event_id for event_id in event_ids if (event := by_id.get(event_id))]
