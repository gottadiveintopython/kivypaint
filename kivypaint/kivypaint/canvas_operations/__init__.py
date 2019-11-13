__all__ = ('operations', )

import importlib
import itertools
from contextlib import contextmanager
from typing import Callable

import attr


@contextmanager
def touch_context(touch):
    touch.push()
    try:
        yield touch
    finally:
        touch.pop()


@attr.s(slots=True, auto_attribs=True, kw_only=True)
class Operation:
    name:str = '<default>'
    func:Callable = None  # async def func(widget, touch, ctx) -> (inst_group, bounding_box)
    helper_text:str = ''
    icon:str = ''


@attr.s(slots=True, auto_attribs=True)
class BoundingBox:
    x:int = 0
    y:int = 0
    right:int = 0
    top:int = 0


operations = tuple(
    itertools.chain.from_iterable(
        importlib.import_module('.' + name, __name__).operations
        for name in (
            'rectangle_line', 'rectangle_fill', 'freehand', 'polyline',
        )
    )
)
