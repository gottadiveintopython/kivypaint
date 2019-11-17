__all__ = ('Paint', )

import trio
from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty
from kivy.event import EventDispatcher
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.clock import Clock
from .async_animation import async_animation

from . import theme
from .canvas_operations import operations


def random_boolean():
    from random import choice
    return choice((True, False))


Builder.load_string('''
#:import theme kivypaint.theme
#:import md_icons kivypaint.md_icons.md_icons

<Paint>:
    orientation: 'vertical'
    spacing: 2
    padding: 2, 6, 6, 2
    canvas.before:
        Color:
            rgba: theme.background_color
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        id: main
        spacing: 2
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: None
            width: toolbox.width
            PaintToolbox:
                id: toolbox
                ctx: root.ctx
            BoxLayout:
                orientation: 'vertical'
                Button:
                    font_name: 'Icon'
                    text: md_icons['delete-outline']
                    font_size: theme.icon_size
                    size_hint: None, None
                    size: self.texture_size
                    on_press: root.reset()
        PaintCanvas:
            id: canvas
            ctx: root.ctx
    PaintLabel:
        id: helper_text
        size_hint_y: None
        height: theme.font_size
        text: '' if root.ctx.operation is None else root.ctx.operation.helper_text
<PaintLabel@Label>:
    color: theme.foreground_color
    font_size: theme.font_size
<PaintToolbox>:
    cols: 2
    spacing: 2
    size_hint: None, None
    size: self.minimum_size
    pos_hint: {'top': 1, 'x': 0, }
<PaintToolboxItem>:
    color: theme.foreground_color
    font_name: 'Icon'
    font_size: theme.icon_size
    size_hint: None, None
    size: (theme.icon_size, ) * 2
    text: md_icons[root.operation.icon]
    canvas.before:
        Color:
            rgba: (1, 1, 1, 0 if self.state == 'normal' else .1)
        Rectangle:
            pos: self.pos
            size: self.size
<PaintCanvas>:
    canvas.before:
        Color:
            rgba: theme.canvas_color
        Rectangle:
            pos: self.to_local(*self.pos)
            size: self.size
''')

class Context(EventDispatcher):
    nursery = ObjectProperty()
    operation = ObjectProperty(None, allownone=True, rebind=True)
    line_width = NumericProperty(2)
    freehand_precision = NumericProperty(20)

    @property
    def line_color(self):
        from kivy.utils import get_random_color
        return get_random_color(alpha=.8)

    @property
    def fill_color(self):
        from kivy.utils import get_random_color
        return get_random_color(alpha=.5)

    @property
    def do_anim_scale(self):
        return random_boolean()

    @property
    def do_anim_rotate(self):
        return random_boolean()

    @property
    def do_anim_translate(self):
        return random_boolean()


class Paint(Factory.BoxLayout):
    ctx = ObjectProperty()

    def __init__(self, *, nursery, **kwargs):
        if 'ctx' not in kwargs:
            kwargs['ctx'] = Context()
        super().__init__(**kwargs)
        self._parent_nursery = nursery
        Clock.schedule_once(self.reset)
        # Clock.schedule_interval(self.reset, 2)

    def reset(self, *args):
        self._reset_nursery()
        self.ids.canvas.canvas.clear()

    def _reset_nursery(self):
        nursery = self.ctx.nursery
        if nursery is not None:
            nursery.cancel_scope.cancel()
        async def root_task(ctx):
            async with trio.open_nursery() as nursery:
                ctx.nursery = nursery
                nursery.start_soon(trio.sleep_forever)
        self._parent_nursery.start_soon(root_task, self.ctx)


class PaintToolbox(Factory.GridLayout):
    ctx = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        def on_press(button):
            self.ctx.operation = None if button.state == 'normal' else button.operation
        for op in operations:
            self.add_widget(
                PaintToolboxItem(
                    operation=op, group='canvas_op', on_press=on_press
                )
            )


class PaintToolboxItem(Factory.ToggleButtonBehavior, Factory.Label):
    operation = ObjectProperty()


# class PaintCanvas(Factory.RelativeLayout):
class PaintCanvas(Factory.StencilView, Factory.Widget):
    ctx = ObjectProperty()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.opos):
            ctx = self.ctx
            if ctx.operation is not None:
                ctx.nursery.start_soon(self.canvas_operation, touch)

    async def canvas_operation(self, touch):
        from kivy.graphics import(
            PushMatrix, PopMatrix, Translate, Rotate, Scale,
            InstructionGroup,
        )
        from . import random_animation
        ctx = self.ctx
        inst_group, bbox = await ctx.operation.func(self, touch, ctx)
        if inst_group is None:
            return
        # print(bbox)
        center = ((bbox.x + bbox.right) / 2, (bbox.y + bbox.top) / 2, )
        sub_group = InstructionGroup()
        sub_group.add(PushMatrix())
        start_soon = ctx.nursery.start_soon
        if ctx.do_anim_translate:
            translate = Translate()
            start_soon(RandomAnimation.translate, translate)
            sub_group.add(translate)
        if ctx.do_anim_rotate:
            rotate = Rotate(origin=center, axis=(0, 0, 1))
            if random_boolean():
                start_soon(RandomAnimation.rotate, rotate)
            else:
                start_soon(RandomAnimation.rotate2, rotate)
            sub_group.add(rotate)
        if ctx.do_anim_scale:
            scale = Scale(origin=center)
            start_soon(RandomAnimation.scale, scale)
            sub_group.add(scale)
        inst_group.insert(0, sub_group)
        inst_group.add(PopMatrix())


class RandomAnimation:
    @staticmethod
    async def scale(target):
        from random import uniform
        d = uniform(.2, 1)
        while True:
            await async_animation(
                target,
                x=uniform(.8, .9),
                y=uniform(.8, .9),
                t='in_quart',
                d=d,
            )
            await async_animation(
                target,
                x=uniform(1.1, 1.2),
                y=uniform(1.1, 1.2),
                t='out_quart',
                d=d,
            )

    @staticmethod
    async def rotate(target):
        from random import uniform
        d = uniform(1, 3)
        while True:
            await async_animation(
                target,
                angle=uniform(-240, -10),
                t='in_out_quint',
                d=d,
            )
            await async_animation(
                target,
                angle=uniform(10, 240),
                t='in_out_quint',
                d=d,
            )

    @staticmethod
    async def rotate2(target):
        start = trio.current_time()
        while True:
            await trio.sleep(0)
            diff = trio.current_time() - start
            target.angle = diff * 30

    @staticmethod
    async def translate(target):
        from random import uniform
        while True:
            await async_animation(
                target,
                x=uniform(-100, 100),
                y=uniform(-100, 100),
                t='in_out_sine',
                d=uniform(1, 4),
            )
            await async_animation(
                target,
                x=uniform(-100, 100),
                y=uniform(-100, 100),
                t='in_out_sine',
                d=uniform(1, 4),
            )
