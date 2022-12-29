from os.path import join, dirname

from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty

from kivymd.uix.relativelayout import MDRelativeLayout


class EditableDropdownMenu(MDRelativeLayout):
    arrow = ObjectProperty()
    text = StringProperty('')
    hint_text = StringProperty('')
    menu = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DropdownMenu(EditableDropdownMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_text(self, instance, value):
        self.ids.text_field.text = value




Builder.load_file(join(dirname(__file__), "dropdown_menu.kv"))
