__all__ = ('operations', )
from kivy.core.window import Window
from kivy.graphics import Line, Color, InstructionGroup
from kivypaint.async_event import async_event
from . import Operation, BoundingBox


async def polyline(widget, touch, ctx, *, precision=20):
    if touch.button != 'left':
        return (None, None)
    to_widget = widget.to_widget
    inst_group = InstructionGroup()
    inst_group.add(Color(*ctx.line_color))
    line = Line(
        width=ctx.line_width,
        points=[*to_widget(*touch.opos), *to_widget(*touch.pos)]
    )
    inst_group.add(line)
    widget.canvas.add(inst_group)

    def on_touch_down(w, t):
        if t.button == 'left':
            p = line.points
            p.extend(p[-2:])
            # line.points = p
            return True
    def on_mouse_pos(window, mouse_pos):
        x, y = to_widget(*mouse_pos)
        points = line.points
        points[-1] = y
        points[-2] = x
        line.points = points
    Window.bind(mouse_pos=on_mouse_pos)
    widget.bind(on_touch_down=on_touch_down)
    await async_event(
        widget, 'on_touch_down',
        filter=lambda w, t: t.button == 'right',
        return_value=True)
    widget.unbind(on_touch_down=on_touch_down)
    Window.unbind(mouse_pos=on_mouse_pos)
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
        name='polyline',
        func=polyline,
        icon='vector-polyline',
        helper_text="'left-click' to plot. 'right-click' to finish."
    ),
)
