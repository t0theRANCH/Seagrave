from os.path import join, dirname

from kivy.lang import Builder
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.card import MDCard


class MD3Card(MDCard, RoundedRectangularElevationBehavior):
    pass
