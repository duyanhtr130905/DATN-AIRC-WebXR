"""Reference consumer rule for tests/M1-C, no frontend integration in M1-B."""


def sequence_action(current: int, incoming: int) -> str:
    if incoming <= current:
        return "ignore"
    return "apply" if incoming == current + 1 else "resync"
