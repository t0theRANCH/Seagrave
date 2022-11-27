from os.path import join, dirname

from kivy.lang import Builder

from Views.Containers.confirm_code_input.confirm_code_input import NumberInput, NumberLabel
from Views.Containers.md3_card.md3_card import MD3Card

from typing import TYPE_CHECKING

from kivymd.toast import toast

if TYPE_CHECKING:
    from Controller.login_screen_controller import LoginScreenController


class ConfirmCodeCard(MD3Card):
    def __init__(self, controller: 'LoginScreenController', **kwargs):
        super(ConfirmCodeCard, self).__init__(**kwargs)
        self.controller = controller

    def resend_code(self):
        self.controller.send_code()

    def confirm(self):
        code = [x.text for x in self.ids.number_container.input_boxes]
        code = "".join(code)
        if '*' not in code:
            self.controller.send_confirmation_code(code)
            return
        toast('Fill in all digits')

    def back(self):
        self.controller.view.switch_cards(self.controller.view.sign_up_card)


Builder.load_file(join(dirname(__file__), "confirm_code.kv"))
