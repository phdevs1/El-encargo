DEFAULT_WAIT_MINUTES = 10
SAMPLE_SIZE = 20


def estimate_wait_minutes(
    recent_completed_wait_minutes: list[int], default_minutes: int = DEFAULT_WAIT_MINUTES
) -> int:
    if not recent_completed_wait_minutes:
        return default_minutes
    return round(sum(recent_completed_wait_minutes) / len(recent_completed_wait_minutes))
