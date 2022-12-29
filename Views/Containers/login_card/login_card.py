from os.path import join, dirname

from kivy.lang import Builder

from Views.Containers.md3_card.md3_card import MD3Card

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from Controller.login_screen_controller import LoginScreenController


class LoginCard(MD3Card):
    def __init__(self, controller: 'LoginScreenController', **kwargs):
        self.controller = controller
        super(LoginCard, self).__init__(**kwargs)

    def log_in(self):
        self.controller.log_in()

    def register(self):
        self.controller.register()

    def forgot_password(self):
        self.controller.forgot_password()


Builder.load_file(join(dirname(__file__), "login_card.kv"))
