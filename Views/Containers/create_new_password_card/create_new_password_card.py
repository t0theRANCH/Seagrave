from os.path import join, dirname

from kivy.lang import Builder
from kivy.properties import ObjectProperty

from Views.Containers.md3_card.md3_card import MD3Card

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Controller.login_screen_controller import LoginScreenController


class CreateNewPasswordCard(MD3Card):
    password = ObjectProperty()
    confirm_password = ObjectProperty()

    def __init__(self, controller: 'LoginScreenController', **kwargs):
        super(CreateNewPasswordCard, self).__init__(**kwargs)
        self.controller = controller
        self.password.bind(text=self.new_password_error_check)
        self.confirm_password.bind(text=self.confirm_password_error_check)

    def new_password_error_check(self, instance, value):
        if not self.controller.password_field_check():
            self.password.error = True
            self.password.helper_text = 'Password must have at least 8 characters, a number, symbol, and capital letter'

    def confirm_password_error_check(self, instance, value):
        if self.password.text != self.confirm_password.text:
            self.confirm_password.error = True
            self.confirm_password.helper_text = 'Both passwords must match'

    def reset_password(self):
        self.controller.send_password_confirmation_code()

    def back(self):
        self.controller.view.switch_cards(self.controller.view.confirm_password_code_card)


Builder.load_file(join(dirname(__file__), "create_new_password_card.kv"))
