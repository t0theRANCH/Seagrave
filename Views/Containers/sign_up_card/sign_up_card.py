from os.path import join, dirname

from kivy.lang import Builder

from Views.Containers.md3_card.md3_card import MD3Card

from typing import TYPE_CHECKING

from kivymd.toast import toast

if TYPE_CHECKING:
    from Controller.login_screen_controller import LoginScreenController


class SignUpCard(MD3Card):
    def __init__(self, controller: 'LoginScreenController', **kwargs):
        super(SignUpCard, self).__init__(**kwargs)
        self.controller = controller

    def back(self):
        self.ids.email.error = False
        self.controller.view.switch_cards(self.controller.view.login_card)

    def enter_confirmation_code(self):
        if self.controller.demo_mode:
            self.controller.main_controller.demo_mode_prompt()
            return
        if not self.controller.email_field_check():
            self.ids.email.error = True
            self.ids.email.helper_text = 'Please enter a valid email'
            return
        self.controller.view.confirm_code_card.ids.instructions.text = f"Enter the code sent to {self.ids.email.text}"
        self.controller.view.switch_cards(self.controller.view.confirm_code_card)

    def register(self):
        if self.controller.demo_mode:
            self.controller.main_controller.demo_mode_prompt()
            return
        if not self.controller.email_field_check():
            self.ids.email.error = True
            self.ids.email.helper_text = 'Please enter a valid email'
        if not self.controller.password_field_check():
            self.ids.email.error = True
            self.ids.email.helper_text = 'Please enter a valid password'
        if self.ids.password.text != self.ids.confirm_password.text:
            self.ids.email.error = True
            self.ids.email.helper_text = 'Passwords do not match'
        self.ids.email.error = False
        self.controller.send_sign_up_email()



Builder.load_file(join(dirname(__file__), "sign_up_card.kv"))
