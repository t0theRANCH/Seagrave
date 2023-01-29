from os.path import join, dirname

from kivy.lang import Builder

from Views.Containers.md3_card.md3_card import MD3Card

from typing import TYPE_CHECKING

from kivymd.toast import toast

if TYPE_CHECKING:
    from Controller.login_screen_controller import LoginScreenController


class ConfirmPasswordCodeCard(MD3Card):
    def __init__(self, controller: 'LoginScreenController', **kwargs):
        super(ConfirmPasswordCodeCard, self).__init__(**kwargs)
        self.controller = controller
        self.code = ''

    def resend_code(self):
        self.controller.reset_password()

    def confirm(self):
        code = [x.text for x in self.ids.number_container.input_boxes]
        if '*' not in code:
            self.code = "".join(code)
            self.controller.view.switch_cards(self.controller.view.create_new_password_card)
            return
        toast('Fill in all digits')

    def back(self):
        self.controller.view.switch_cards(self.controller.view.sign_up_card)


Builder.load_file(join(dirname(__file__), "confirm_password_code_card.kv"))
