from os.path import join, dirname

from kivy.lang import Builder

from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog


class ErrorPopup(MDDialog):
    def __init__(self, empty_fields, **kwargs):
        self.empty_fields = "\n".join(empty_fields)
        self.buttons = [MDFlatButton(text='Go Back', on_press=self.dismiss)]
        super(ErrorPopup, self).__init__(**kwargs)
        self.text = f"Please Fill in Fields: \n{self.empty_fields}"


Builder.load_file(join(dirname(__file__), "error_popup.kv"))
