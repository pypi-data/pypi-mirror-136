from ..EasyThreadings import MAIN_THREADING, MAIN_FUNCTIONS


def join(thread_name: str) -> None:
    """
    阻塞线程指导线程执行完毕。

    thread_name：使用EasyThreading创建线程时提供的name参数；
    """
    MAIN_THREADING[thread_name].join()


def join_func(func: object) -> None:
    """
    阻塞线程指导线程执行完毕。

    func：您希望阻塞的函数；
    """
    MAIN_FUNCTIONS[func].join()