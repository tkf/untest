import signal
from contextlib import contextmanager


@contextmanager
def ignoring(sig):
    """
    Context manager for ignoring signal `sig`.

    For example,::

        with ignoring(signal.SIGINT):
            do_something()

    would ignore user's ctrl-c during ``do_something()``.  This is
    useful when launching interactive program (in which ctrl-c is a
    valid keybinding) from Python.
    """
    s = signal.signal(sig, signal.SIG_IGN)
    try:
        yield
    finally:
        signal.signal(sig, s)
