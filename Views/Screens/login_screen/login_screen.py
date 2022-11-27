from os.path import join, dirname

from kivy.animation import Animation
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen

from Views.Containers.login_card.login_card import LoginCard
from Views.Containers.sign_up_card.sign_up_card import SignUpCard
from Views.Containers.confirm_code_card.confirm_code import ConfirmCodeCard
from Views.Containers.confirm_password_code_card.confirm_password_code_card import ConfirmPasswordCodeCard
from Views.Containers.reset_password_card.reset_password_card import ResetPasswordCard
from Views.Containers.create_new_password_card.create_new_password_card import CreateNewPasswordCard

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Controller.login_screen_controller import LoginScreenController


class LoginScreen(MDScreen):
    controller: 'LoginScreenController' = ObjectProperty()
    model: 'MainModel' = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_card = None
        self.card_to = None
        self.login_card = LoginCard(self.controller)
        self.sign_up_card = SignUpCard(self.controller)
        self.confirm_code_card = ConfirmCodeCard(self.controller)
        self.confirm_password_code_card = ConfirmPasswordCodeCard(self.controller)
        self.reset_password_card = ResetPasswordCard(self.controller)
        self.create_new_password_card = CreateNewPasswordCard(self.controller)
        self.all_cards = [self.login_card, self.sign_up_card, self.confirm_code_card, self.reset_password_card,
                          self.confirm_password_code_card, self.create_new_password_card]

    def on_pre_enter(self, *args):
        self.add_cards()
        self.set_card_positions()

    def add_cards(self):
        for widget in self.all_cards:
            self.ids.card_container.add_widget(widget)

    def set_card_positions(self):
        for widget in self.all_cards:
            widget.pos_hint = {'top': 0}

    def enter_animation(self):
        self.card_to = self.login_card
        self.card_in_animation(enter=True)
        self.current_card = self.login_card

    def switch_cards(self, card_to):
        self.card_to = card_to
        self.card_out_animation()
        self.current_card = card_to

    def logo_fade_in_start(self, *args):
        logo_animation = Animation(opacity=0.1, duration=2)
        logo_animation.bind(on_complete=self.logo_fade_in_finish)
        logo_animation.start(self.ids.logo)

    def logo_fade_in_finish(self, *args):
        logo_animation = Animation(opacity=1, duration=1)
        logo_animation.start(self.ids.logo)

    def card_in_animation(self, animation=None, widget=None, enter=False):
        anim = Animation(pos_hint={'top': 1}, duration=1)
        if enter:
            anim.bind(on_complete=self.logo_fade_in_start)
        anim.start(self.card_to)

    def card_out_animation(self):
        anim = Animation(pos_hint={'top': 0}, duration=1)
        anim.bind(on_complete=self.card_in_animation)
        anim.start(self.current_card)

    def on_enter(self, *args):
        self.enter_animation()
        self.controller.on_enter(*args)

    def register(self):
        self.switch_cards(self.sign_up_card)


Builder.load_file(join(dirname(__file__), "login.kv"))
