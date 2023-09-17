import re

from kivy import platform
from kivy._event import EventDispatcher
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.clock import Clock

from kivymd.toast import toast
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar

if platform == 'android':
    from Mobile_OS.android_os import Android
elif platform == 'ios':
    from Mobile_OS.ios import IOS
else:
    from Mobile_OS.pc import PC
from Views.Popups.save_password.save_password import SavePassword
from Views.Screens.login_screen.login_screen import LoginScreen
from api_requests import open_request

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Controller.main_controller import MainController
    from Model.main_model import MainModel


class LoginScreenController(EventDispatcher):
    main_controller: 'MainController' = ObjectProperty()
    demo_mode: bool = BooleanProperty()

    def __init__(self, model: 'MainModel', **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.view = LoginScreen(name='login', controller=self, model=self.model)

    def on_enter(self, *args):
        self.set_phone()
        if not self.model.phone:
            return
        user, password = self.model.check_for_user_info()
        self.enter_user_data(user, password)

    def set_phone(self):
        if platform == 'android':
            self.model.phone = Android()
        elif platform == 'ios':
            self.model.phone = IOS()
        else:
            self.model.phone = PC()

        self.model.phone.main_controller = self.main_controller

    def scrim_on(self):
        self.main_controller.view.scrim_on()

    def scrim_off(self):
        self.main_controller.view.scrim_off()

    def enter_user_data(self, user: str, password: str):
        self.view.login_card.ids.email.text = user
        self.view.login_card.ids.password.text = password

    def password_field_check(self):
        special = [' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=',
                   '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~']

        p_rules = [lambda s: any(x.isupper() for x in s),  # must have at least one uppercase
                   lambda s: any(x.islower() for x in s),  # must have at least one lowercase
                   lambda s: any(x.isdigit() for x in s),  # must have at least one digit
                   lambda s: any(x in s for x in special),  # must contain special characters
                   lambda s: len(s) >= 7  # must be at least 7 characters
                   ]

        return all(rule(self.view.current_card.ids.password.text) for rule in p_rules)

    def email_field_check(self):
        regex = r'\b[A-Za-z0-9._%+-]+@seagravebuildings\.com\b'
        return bool(re.fullmatch(regex, self.view.current_card.ids.email.text))

    def register(self):
        self.view.register()

    def send_sign_up_email(self):
        self.scrim_on()
        r = open_request(name='sign_up', data={"email": self.view.current_card.ids.email.text.capitalize(),
                                               "password": self.view.current_card.ids.password.text})
        if 'error' in r:
            self.view.current_card.ids.email.helper_text = r['body']
            self.view.current_card.ids.email.error = True
            self.scrim_off()
            return
        self.scrim_off()
        self.clear_errors()
        self.view.switch_cards(self.view.confirm_code_card)

    def send_code(self):
        self.scrim_on()
        r = open_request(name='sign_up_resend', data={"email": self.view.sign_up_card.ids.email.text})
        if 'error' in r:
            self.display_error_snackbar(r['body'])
            self.scrim_off()
            return
        self.scrim_off()
        toast("Verification code sent!")

    def send_confirmation_code(self, code):
        self.scrim_on()
        r = open_request(name='sign_up_confirm', data={"code": code, "email": self.view.sign_up_card.ids.email.text})
        if 'error' in r:
            self.display_error_snackbar(r['body'])
            self.scrim_off()
            return
        self.scrim_off()
        toast('Your email has been verified, please log in')
        self.main_controller.change_screen('login')

    def send_password_confirmation_code(self):
        self.scrim_on()
        data = {"code": self.view.confirm_password_code_card.code,
                "email": self.view.reset_password_card.ids.email.text,
                "password": self.view.current_card.ids.password.text}
        r = open_request(name='forgot_password_confirm', data=data)
        self.main_controller.login_controller.display_error_snackbar(r['body'])
        self.scrim_off()
        self.main_controller.change_screen('login')

    def forgot_password(self):
        if self.demo_mode:
            self.main_controller.demo_mode_prompt()
            return
        self.view.switch_cards(self.view.reset_password_card)

    def log_in(self):
        if self.demo_mode:
            self.populate_main_screen()
            self.switch_to_main()
        self.scrim_on()
        if self.email_field_check() and self.password_field_check():
            self.clear_errors()
            u = self.view.current_card.ids.email.text
            s = self.view.current_card.ids.password.text
            r = open_request(name='authenticate', data={"email": u.capitalize(), "password": s})
            if 'AuthenticationResult' in r:
                self.authentication(r)
        else:
            self.view.current_card.ids.password.helper_text = 'Password must have at lease one uppercase, number, and symbol, ' \
                                                              'and be over 7 characters'
            self.view.current_card.ids.password.error = True
        self.scrim_off()

    def authentication(self, r):
        self.model.access_token = r['AuthenticationResult']['AccessToken']
        self.model.id_token = r['AuthenticationResult']['IdToken']
        self.model.refresh_token = r['AuthenticationResult']['RefreshToken']
        if not self.model.access_token:
            self.display_error_snackbar('Error logging in, please try again')
            return
        self.save_password_prompt()
        self.model.db_handler()
        if not self.model.access_token:
            self.display_error_snackbar('Error logging in, please try again')
            return
        self.model.get_hours()
        self.model.clear_pictures()
        self.model.clear_blueprints()
        self.model.clear_forms()
        self.populate_main_screen()
        self.switch_to_main()

    def clear_errors(self):
        self.view.login_card.ids.email.helper_text = ''
        self.view.login_card.ids.email.error = False
        self.view.login_card.ids.password.helper_text = ''
        self.view.login_card.ids.password.error = False

    def save_password_prompt(self):
        if self.model.phone and not self.model.phone.get_user():
            save_password = SavePassword(self)
            save_password.open()

    def save_password(self):
        user = self.view.login_card.ids.email.text
        pw = self.view.login_card.ids.password.text
        self.model.save_password(user, pw)

    def dont_save_password(self):
        user = self.view.login_card.ids.email.text
        self.model.dont_save_password(user)

    def reset_password(self):
        email = self.view.reset_password_card.ids.email.text
        self.clear_errors()
        r = open_request(name='forgot_password', data={"email": email})
        if r['success']:
            self.enter_confirmation_code()
        else:
            self.display_error_message(r['body'])

    def enter_confirmation_code(self):
        self.view.confirm_password_code_card.ids.instructions.text = f"Enter the code sent to " \
                                                                     f"{self.view.reset_password_card.ids.email.text}"
        self.view.switch_cards(self.view.confirm_password_code_card)

    def check_email_field(self, text: str):
        if not text:
            self.display_error_message('Please enter an email')
        return not self.view.login_card.ids.email.error

    def display_error_message(self, message_text: str):
        self.view.current_card.ids.email.helper_text = message_text
        self.view.current_card.ids.email.error = True

    @staticmethod
    def display_error_snackbar(message_text: str):
        MDSnackbar(
            MDLabel(
                text=message_text
            )
        ).open()

    def populate_main_screen(self):
        user = self.model.user
        if user['given_name'] not in ['max', 'Max', 'tyson', 'Tyson', 'justin', 'Justin']:
            self.main_controller.site_view_controller.remove_delete_button()
        self.main_controller.main_screen_controller.input_data_into_view()
        self.main_controller.input_data_into_nav_drawer()

    def switch_to_main(self):
        if not self.demo_mode:
            Clock.schedule_interval(self.refresh_auth, (30 * 60))
        self.main_controller.change_screen('main_screen')

    def refresh_auth(self, *args):
        if self.model.refresh_token:
            self.model.db_handler()
            if not self.model.id_token:
                response = open_request(name='authenticate_refresh',
                                        data={"refresh_token": self.model.refresh_token,
                                              "username": self.model.user['given_name']})
                if 'success' in response.get('message', ''):
                    self.model.access_token = response['data']['access_token']
                    self.model.id_token = response['data']['id_token']
                    self.model.db_handler()
        else:
            self.main_controller.change_screen('login')
            self.model.id_token = ''
            self.model.refresh_token = ''
            self.model.access_token = ''
