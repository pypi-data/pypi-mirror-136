import inspect
from typing import Callable
import asyncio

class Event:
    def __init__(self, name: str, func: Callable):
        self.name = name
        self.func = func

class Command:
    def __init__(self, name: str, func: Callable, _type: int):
        self.name = name
        self.func = func
        self.type = _type

class Component:
    def __init__(self, custom_id, future, func: Callable, timeout: float = 0.0, is_single_use: bool = False):
        self.custom_id = custom_id
        self.func = func
        self.future = future
        self.timeout = timeout
        self.is_single_use = is_single_use


def event(name):
    def wrapper(func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError('Event decorator can only be applied to coroutine functions')
        return Event(name, func)
    return wrapper

def command(name, _type):
    def wrapper(func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError('Command decorator can only be applied to coroutine functions')
        print(type(func))
        print(func)
        print(func.__get__)
        return Command(name, func, _type)
    return wrapper
