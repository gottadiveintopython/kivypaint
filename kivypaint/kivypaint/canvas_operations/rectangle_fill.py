__all__ = ('operations', )

from functools import partial
from kivy.graphics import (Rectangle, Ellipse, Color, InstructionGroup, )
from kivypaint.async_event import async_event
from . import Operation, BoundingBox, touch_context

shape_classes = {
    'Rectangle': Rectangle,
    'Ellipse': Ellipse,
}

async def _rectangle_based(widget, touch, ctx, *, shape_name):
    def update_shape(shape, touch):
        x = min(touch.x, touch.ox)
        y = min(touch.y, touch.oy)
        width = abs(touch.x - touch.ox)
        height = abs(touch.y - touch.oy)
        shape.pos = (x, y)
        shape.size = (width, height)
    inst_group = InstructionGroup()
    inst_group.add(Color(*ctx.fill_color))
    shape = shape_classes[shape_name]()
    inst_group.add(shape)
    with touch_context(touch):
        touch.apply_transform_2d(widget.to_widget)
        update_shape(shape, touch)
    widget.canvas.add(inst_group)

    def on_touch_move(w, t):
        if t is touch and t.grab_current is w:
            with touch_context(t):
                touch.apply_transform_2d(w.to_local)
                update_shape(shape, touch)
            return True
    try:
        touch.grab(widget)
        widget.bind(on_touch_move=on_touch_move)
        await async_event(
            widget, 'on_touch_up',
            filter=lambda w, t: t is touch and t.grab_current is w,
            return_value=True)
    except:
        widget.canvas.remove(inst_group)
        raise
    finally:
        widget.unbind(on_touch_move=on_touch_move)
        touch.ungrab(widget)
    pos, size = shape.pos, shape.size
    return (
        inst_group,
        BoundingBox(
            x=pos[0], right=pos[0] + size[0],
            y=pos[1], top=pos[1] + size[1],
        )
    )


operations = (
    Operation(
        name='rectangle(fill)',
        func=partial(_rectangle_based, shape_name='Rectangle'),
        icon='rectangle',
    ),
    Operation(
        name='ellipse(fill)',
        func=partial(_rectangle_based, shape_name='Ellipse'),
        icon='ellipse',
    ),
)
