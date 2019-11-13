__all__ = ('async_event', )

import trio
from collections import namedtuple
Parameter = namedtuple('Parameter', ('args', 'kwargs'))


async def async_event(ed, name, *, filter=None, return_value=None):
    def _callback(*args, **kwargs):
        nonlocal parameter
        nonlocal bind_id
        if (filter is not None) and not filter(*args, **kwargs):
            return
        parameter = Parameter(args, kwargs, )
        ed.unbind_uid(name, bind_id)
        event.set()
        return return_value

    parameter = None
    bind_id = ed.fbind(name, _callback)
    assert bind_id > 0  # check if binding succeeded
    event = trio.Event()
    await event.wait()
    return parameter
