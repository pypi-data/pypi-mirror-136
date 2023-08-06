from functools import wraps
from threading import Thread


MAIN_THREADING = {}


def thread(func: object) -> object:
    @wraps(func)
    def wrapper(name: str=f'Thread{len(MAIN_THREADING)}', *args, **kwargs) -> None:
        MAIN_THREADING[name] = Thread(target=func, args=args, kwargs=kwargs)
        MAIN_THREADING[name].start()
    return wrapper