from os.path import join, dirname

from kivy.lang import Builder

from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Controller.login_screen_controller import LoginScreenController


class SavePassword(MDDialog):
    def __init__(self, controller: 'LoginScreenController', **kwargs):
        self.controller = controller
        self.buttons = [MDFlatButton(text='Don\'t Save', on_press=self.no),
                        MDFlatButton(text='Save Password', on_press=self.yes)]
        super().__init__(**kwargs)

    def yes(self, obj):
        self.controller.save_password()
        self.dismiss()

    def no(self, obj):
        self.controller.dont_save_password()
        self.dismiss()


Builder.load_file(join(dirname(__file__), "save_password.kv"))
