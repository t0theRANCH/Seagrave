from os.path import join, dirname

from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivy.uix.modalview import ModalView


class Scrim(ModalView):
    is_visible = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.pos_hint = {'center_x': .5, 'center_y': .5}
        self.background_color = (0, 0, 0, 0.7)
        self.auto_dismiss = False
        self.opacity = 1 if self.is_visible else 0

    def on_touch_down(self, touch):
        return True if self.collide_point(*touch.pos) else super().on_touch_down(touch)

    def on_is_visible(self, instance, value):
        if value:
            self.open()
            self.opacity = 1
        else:
            self.opacity = 0
            self.dismiss()

Builder.load_file(join(dirname(__file__), 'scrim.kv'))
