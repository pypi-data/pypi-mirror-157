from .kv import KV
import time

TIME_SLEEP = 0.7


class Backspace:
    def __init__(self):
        self.val = '\b'


backspace = Backspace()


def greeting():
    print("hello" + backspace.val + "world")


def n(num: int):
    if num < 0:
        raise ValueError("illegal input")
    return backspace.val * num


def printl(print_list, time_sleep=TIME_SLEEP, last: bool = True, end: str = ""):
    len_l = len(print_list)
    for i in range(len_l):
        len_i = len(print_list[i])
        print(print_list[i], end="")
        time.sleep(time_sleep)
        if last is True and i == len_l - 1:
            print("")
        else:
            print(len_i * backspace.val, end="")
        print(end, end="")


def loading():
    for i in range(10):
        print("-", end="")
        time.sleep(0.1)
    print("100%")
