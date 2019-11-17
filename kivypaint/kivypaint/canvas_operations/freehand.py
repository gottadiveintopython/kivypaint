__all__ = ('operations', )

from kivy.graphics import Line, Color, InstructionGroup
from kivypaint.async_event import async_event
from . import Operation, BoundingBox, touch_context


async def freehand(widget, touch, ctx):
    last_x, last_y = widget.to_widget(*touch.opos)
    inst_group = InstructionGroup()
    inst_group.add(Color(*ctx.line_color))
    line = Line(width=ctx.line_width, points=[last_x, last_y])
    inst_group.add(line)
    widget.canvas.add(inst_group)
    precision = ctx.freehand_precision

    touch.grab(widget)
    def on_touch_move(w, t):
        nonlocal last_x, last_y
        if t is touch and t.grab_current is w:
            with touch_context(t):
                t.apply_transform_2d(w.to_local)
                if abs(last_x - t.x) + abs(last_y - t.y) > precision:
                    points = line.points
                    points.extend(t.pos)
                    line.points = points
                    last_x, last_y = t.pos
            return True
    widget.bind(on_touch_move=on_touch_move)
    await async_event(
        widget, 'on_touch_up',
        filter=lambda w, t: t is touch and t.grab_current is w,
        return_value=True)
    widget.unbind(on_touch_move=on_touch_move)
    touch.ungrab(widget)
    x_list = line.points[::2]
    y_list = line.points[1::2]
    return (
        inst_group,
        BoundingBox(
            x=min(x_list), right=max(x_list),
            y=min(y_list), top=max(y_list),
        )
    )


operations = (
    Operation(
        name='freehand',
        func=freehand,
        icon='signature-freehand',
    ),
)
