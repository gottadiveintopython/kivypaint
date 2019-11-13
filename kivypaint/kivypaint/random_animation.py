from random import uniform, randrange
from kivy.animation import Animation


def translate():
    anim = Animation(
        x=uniform(-100, 100),
        y=uniform(-100, 100),
        t='in_out_sine',
        d=uniform(1, 4)) + Animation(
            x=uniform(-100, 100),
            y=uniform(-100, 100),
            t='in_out_sine',
            d=uniform(1, 4))
    anim.repeat = True
    return anim


def scale():
    d = uniform(.2, 1)
    anim = Animation(
        x=uniform(.8, .9),
        y=uniform(.8, .9),
        t='in_quart',
        d=d) + Animation(
            x=uniform(1.1, 1.2),
            y=uniform(1.1, 1.2),
            t='out_quart',
            d=d)
    anim.repeat = True
    return anim


def rotate():
    d = uniform(1, 3)
    anim = Animation(
        angle=uniform(-240, -10),
        t='in_out_quint',
        d=d) + Animation(
            angle=uniform(10, 240),
            t='in_out_quint',
            d=d)
    anim.repeat = True
    return anim
