from os.path import join, dirname

from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.modalview import ModalView


class Scrim(ModalView):
    is_visible = BooleanProperty(False)
    message = StringProperty("Please wait...")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.pos_hint = {'center_x': .5, 'center_y': .5}
        self.background_color = (0, 0, 0, 0.7)
        self.auto_dismiss = False

    def on_touch_down(self, touch):
        # Block touch events when scrim is visible
        return True if self.is_visible else super().on_touch_down(touch)

    def on_is_visible(self, instance, value):
        self.ids.spinner.active = value  # Activate the spinner if visible
        if value:
            self.open()
        else:
            self.dismiss()


Builder.load_file(join(dirname(__file__), 'scrim.kv'))
