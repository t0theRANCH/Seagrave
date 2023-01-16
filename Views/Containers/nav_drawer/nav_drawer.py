from os.path import join, dirname

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.navigationdrawer import MDNavigationDrawer

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from Controller.main_controller import MainController
    from Views.Screens.root_screen.root_screen import RootScreen


class NavDrawer(MDNavigationDrawer):
    root_screen: Union[None, 'RootScreen'] = ObjectProperty()
    controller: Union[None, 'MainController'] = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_screen = None
        self.controller = None

    def on_enter(self):
        self.root_screen = self.parent.parent
        self.controller = self.root_screen.controller

    def get_current_screen(self):
        return self.controller.screen_manager.get_screen(f"{self.controller.screen_manager.current}")

    def open_close(self):
        if self.state == 'open':
            self.set_state('close')
        else:
            self.set_state('open')

    def input_employee_name(self, name):
        self.ids.employee_name.text = name

    def input_employee_email(self, email):
        self.ids.employee_email.text = email

    def change_feed(self, feed, deletable=False):
        screen = self.get_current_screen()
        screen.controller.change_feed(feed, deletable)
        self.open_close()

    def danger_zone(self):
        screen = self.get_current_screen()
        screen.controller.danger_zone()
        self.open_close()


Builder.load_file(join(dirname(__file__), "nav_drawer.kv"))
