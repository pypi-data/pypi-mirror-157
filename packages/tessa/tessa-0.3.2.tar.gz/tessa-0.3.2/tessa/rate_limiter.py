"""Rate Limiter -- makes sure we don't hit the APIs too often by making sure a minimum
amount of time has elapsed between calls to an API.

The goal is to never run into errors in the first place, b/c at least investing.com
takes substantial time until it allow-lists a blocked IP address again. That is also why
we can't use a library such das Tenacity here.
"""

import time
import pendulum

guards = {}

original_guards = {
    # `reset_guards` will add `last_call` to each guard.
    "investing": {
        "wait_seconds": 1,
    },
    "crypto": {
        "wait_seconds": 1,
    },
}


def reset_guards() -> None:
    """Reset the guards."""
    global guards  # pylint: disable=invalid-name,global-statement
    guards = original_guards.copy()
    for guard in guards.values():
        guard["last_call"] = pendulum.parse("1900")


# FIXME Turn rate_limit into a decorator that takes the type as an argument? cf
# https://realpython.com/primer-on-python-decorators/#decorators-with-arguments (Only
# possible if we split the price_history function up into multiple functions at some
# point.)


def rate_limit(type_: str) -> None:
    """Do the actual rate limiting."""
    which_guard = "crypto" if type_ == "crypto" else "investing"
    guard = guards[which_guard]
    diff = (pendulum.now() - guard["last_call"]).total_seconds()
    if diff < guard["wait_seconds"]:
        time.sleep(guard["wait_seconds"] - diff)
    guard["last_call"] = pendulum.now()


reset_guards()
