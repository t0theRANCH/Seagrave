from os.path import join, dirname

from kivy.lang import Builder

from Views.Containers.md3_card.md3_card import MD3Card

from typing import TYPE_CHECKING

from kivymd.toast import toast

if TYPE_CHECKING:
    from Controller.login_screen_controller import LoginScreenController


class ResetPasswordCard(MD3Card):
    def __init__(self, controller: 'LoginScreenController', **kwargs):
        super(ResetPasswordCard, self).__init__(**kwargs)
        self.controller = controller

    def send_code(self):
        if self.controller.email_field_check():
            self.ids.email.error = False
            self.controller.reset_password()

    def enter_confirmation_code(self):
        if not self.controller.email_field_check():
            self.ids.email.error = True
            self.ids.email.helper_text = 'Please enter a valid email'
            return
        self.ids.email.error = False
        self.controller.view.confirm_password_code_card.ids.instructions.text = f"Enter the code sent to {self.ids.email.text}"
        self.controller.view.switch_cards(self.controller.view.confirm_password_code_card)

    def back(self):
        self.ids.email.error = False
        self.controller.view.switch_cards(self.controller.view.login_card)


Builder.load_file(join(dirname(__file__), "reset_password_card.kv"))
