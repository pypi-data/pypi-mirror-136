from ..EasyThreading import MAIN_THREADING


def join(thread_name: str) -> None:
    MAIN_THREADING[thread_name].join()