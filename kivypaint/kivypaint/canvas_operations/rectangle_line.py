__all__ = ('operations', )

from functools import partial
from kivy.graphics import (Line, Color, InstructionGroup, )
from kivypaint.async_event import async_event
from . import Operation, BoundingBox, touch_context

async def _rectangle_based(widget, touch, ctx, *, shape_name):
    def update_line(line, touch):
        x = min(touch.x, touch.ox)
        y = min(touch.y, touch.oy)
        width = abs(touch.x - touch.ox)
        height = abs(touch.y - touch.oy)
        setattr(line, shape_name, (x, y, width, height, ))
    inst_group = InstructionGroup()
    inst_group.add(Color(*ctx.line_color))
    line = Line(width=ctx.line_width)
    inst_group.add(line)
    with touch_context(touch):
        touch.apply_transform_2d(widget.to_widget)
        update_line(line, touch)
    widget.canvas.add(inst_group)

    touch.grab(widget)
    def on_touch_move(w, t):
        if t is touch and t.grab_current is w:
            update_line(line, touch)
            return True
    widget.bind(on_touch_move=on_touch_move)
    await async_event(
        widget, 'on_touch_up',
        filter=lambda w, t: t is touch and t.grab_current is w,
        return_value=True)
    widget.unbind(on_touch_move=on_touch_move)
    touch.ungrab(widget)
    with touch_context(touch):
        t = touch
        t.apply_transform_2d(widget.to_widget)
        return (
            inst_group,
            BoundingBox(
                x=min(t.ox, t.x), right=max(t.ox, t.x),
                y=min(t.oy, t.y), top=max(t.oy, t.y),
            )
        )


operations = (
    Operation(
        name='rectangle(line)',
        func=partial(_rectangle_based, shape_name='rectangle'),
        icon='rectangle-outline',
    ),
    Operation(
        name='ellipse(line)',
        func=partial(_rectangle_based, shape_name='ellipse'),
        icon='ellipse-outline',
    ),
)
