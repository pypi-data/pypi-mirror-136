from functools import wraps
from threading import Thread


MAIN_THREADING = {}
MAIN_FUNCTIONS = {}


def thread(func: object) -> object:
    """
    这是thread修饰符，您可以使用它来修饰一个函数，之后每次调用这个函数时都会自动创建线程。

    name：线程的名称；
    """
    @wraps(func)
    def wrapper(name: str=f'Thread{len(MAIN_THREADING)}', *args, **kwargs) -> None:
        MAIN_THREADING[name] = Thread(target=func, args=args, kwargs=kwargs)
        MAIN_THREADING[name].start()
        MAIN_FUNCTIONS[func] = MAIN_THREADING[name]
    return wrapper