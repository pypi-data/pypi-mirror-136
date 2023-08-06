import threading


def threaded(fn):
    def wrapper(*k, **kw):
        t = threading.Thread(target=fn, args=k, daemon=True, kwargs=kw)
        t.start()
        return t
    return wrapper

# test
