import time


MAX_LOGIN_ATTEMPTS = 5
RATE_LIMIT_WINDOW_SECONDS = 60


login_attempts: dict[str, list[float]] = {}


def is_rate_limited(identifier: str) -> bool:
    current_time = time.time()

    attempt_times = login_attempts.get(identifier, [])

    recent_attempts = [
        attempt_time
        for attempt_time in attempt_times
        if current_time - attempt_time < RATE_LIMIT_WINDOW_SECONDS
    ]

    login_attempts[identifier] = recent_attempts

    return len(recent_attempts) >= MAX_LOGIN_ATTEMPTS


def record_failed_login(identifier: str) -> None:
    current_time = time.time()

    attempt_times = login_attempts.get(identifier, [])

    recent_attempts = [
        attempt_time
        for attempt_time in attempt_times
        if current_time - attempt_time < RATE_LIMIT_WINDOW_SECONDS
    ]

    recent_attempts.append(current_time)

    login_attempts[identifier] = recent_attempts


def reset_login_attempts(identifier: str) -> None:
    login_attempts.pop(identifier, None)