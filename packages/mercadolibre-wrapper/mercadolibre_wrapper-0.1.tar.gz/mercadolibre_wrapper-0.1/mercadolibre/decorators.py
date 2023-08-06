import time
from functools import wraps


def valid_token(func):
    @wraps(func)
    def helper(*args, **kwargs):
        client = args[0]
        if client.expires_at and not client.expires_at > time.time():
            client.refresh_token()
        return func(*args, **kwargs)

    return helper
