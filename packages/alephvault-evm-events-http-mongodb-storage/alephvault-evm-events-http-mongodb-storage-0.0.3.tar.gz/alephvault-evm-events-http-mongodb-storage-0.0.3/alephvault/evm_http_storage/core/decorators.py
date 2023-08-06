import os
import functools
from ilock import ILock


def uses_lock(f):
    """
    Wraps the entire call in a global lock, whose name is taken
    from the ILOCK_NAME environment variable, or "default".
    :param f: The wrapped function.
    :return: A wrapping function.
    """

    lock_name = os.getenv("ILOCK_NAME", "default")

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        with ILock("alephvault.evm_http_storage.lock." + lock_name):
            return f(*args, **kwargs)

    return wrapper