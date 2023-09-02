from os.path import join, dirname

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.navigationdrawer import MDNavigationDrawer

from Views.Popups.settings.settings import Settings, SettingsContent
from Views.Popups.debug.debug import Debug, DebugContent

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

    def settings(self):
        settings_content = SettingsContent(model=self.root_screen.model)
        settings = Settings(title='Settings', type='custom', content_cls=settings_content)
        settings.open()

    def debug(self):
        debug_content = DebugContent(model=self.root_screen.model)
        debug = Debug(title='Debug', type='custom', content_cls=debug_content)
        debug.open()

    def danger_zone(self):
        screen = self.get_current_screen()
        screen.controller.danger_zone()
        self.open_close()


Builder.load_file(join(dirname(__file__), "nav_drawer.kv"))
