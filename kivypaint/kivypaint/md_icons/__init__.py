__all__ = ('md_icons', )

try:
    from kivymd.icon_definitions import md_icons
except ImportError:
    from pathlib import Path
    from kivy.core.text import LabelBase
    from .icon_definitions import md_icons
    PARENT_DIR = Path(__file__).resolve().parent
    LabelBase.register(
        'Icon', str(PARENT_DIR.joinpath('materialdesignicons-webfont.ttf')))
