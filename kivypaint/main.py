from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('kivy', 'log_level', 'debug')
import kivy
kivy.require('2.0.0')
# from kivy.utils import platform
# assert platform not in ('android', 'ios', )

import trio
from kivy.app import App


class PaintApp(App):
    nursery = None

    def build(self):
        from kivypaint import Paint
        return Paint(nursery=self.nursery)

    async def root_task(self):
        async with trio.open_nursery() as nursery:
            self.nursery = nursery

            async def app_task():
                await self.async_run(async_lib='trio')
                nursery.cancel_scope.cancel()

            nursery.start_soon(app_task)


if __name__ == "__main__":
    trio.run(PaintApp().root_task)
