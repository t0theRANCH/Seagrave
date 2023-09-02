from os.path import join, dirname

from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout


class LabelSwitch(MDBoxLayout):
    label_text = StringProperty("")
    switch_active = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_switch_active(self, obj, value):
        self.switch_active = value


Builder.load_file(join(dirname(__file__), "label_switch.kv"))
