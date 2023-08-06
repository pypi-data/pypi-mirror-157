import resource


def _cpu_time() -> float:
    """Generates the cpu time to report. Adds the user and system time, following the implementation from timing-asgi"""
    resources = resource.getrusage(resource.RUSAGE_SELF)
    return resources[0] + resources[1]
