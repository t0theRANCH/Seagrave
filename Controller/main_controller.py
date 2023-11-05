from kivy._event import EventDispatcher
from kivy.properties import ObjectProperty, BooleanProperty
from kivymd.uix.transition import MDSwapTransition, MDSlideTransition

from Views.Screens.root_screen.root_screen import RootScreen

from typing import TYPE_CHECKING

from api_requests import upload

if TYPE_CHECKING:
    from kivymd.uix.screenmanager import MDScreenManager
    from kivymd.uix.navigationdrawer import MDNavigationDrawer
    from Controller.login_screen_controller import LoginScreenController
    from Controller.main_screen_controller import MainScreenController
    from Controller.site_view_controller import SiteViewController
    from Controller.form_view_controller import FormViewController
    from Controller.picture_list_view_controller import PictureListViewController
    from Controller.picture_view_controller import PictureViewController
    from Model.main_model import MainModel


class MainController(EventDispatcher):
    login_controller: 'LoginScreenController' = ObjectProperty()
    main_screen_controller: 'MainScreenController' = ObjectProperty()
    site_view_controller: 'SiteViewController' = ObjectProperty()
    form_view_controller: 'FormViewController' = ObjectProperty()
    picture_list_view_controller: 'PictureListViewController' = ObjectProperty()
    picture_view_controller: 'PictureViewController' = ObjectProperty()
    demo_mode = BooleanProperty()

    def __init__(self, model: 'MainModel', **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.view = RootScreen(controller=self, model=self.model)
        self.screen_manager = self.view.ids.screen_manager
        self.nav_drawer = self.view.ids.nav
        self.demo_mode = model.settings['Demo Mode']
        self.slide_transition = MDSlideTransition()
        self.swap_transition = MDSwapTransition()

    def on_demo_mode(self, instance, value):
        if not value and self.login_controller:
            self.login_controller.refresh_auth()
        self.model.demo_mode = value

    def start_up(self):
        self.load_controllers()
        if self.model.settings['Keep Me Logged In'] and not self.demo_mode:
            self.login_controller.set_phone()
            self.login_controller.refresh_auth()
            if self.model.id_token:
                self.login_controller.populate_main_screen()
                self.login_controller.switch_to_main()
            else:
                self.change_screen('login')
        else:
            self.change_screen('login')
        return self.view

    def load_controllers(self):
        screens = [self.login_controller, self.main_screen_controller, self.site_view_controller,
                   self.form_view_controller, self.picture_list_view_controller, self.picture_view_controller]
        for s in screens:
            s.main_controller = self
            s.demo_mode = self.demo_mode
            self.screen_manager.add_widget(s.view)

    def change_screen(self, screen_name: str, slide: bool = False):
        if slide:
            self.screen_manager.transition = self.slide_transition
        else:
            self.screen_manager.transition = self.swap_transition
        self.screen_manager.current = screen_name

    def input_data_into_nav_drawer(self):
        user = self.model.user
        self.nav_drawer.input_employee_name(f"{user['given_name']} {user['family_name']}")
        self.nav_drawer.input_employee_email(user['email'])

    def equipment_service_popup(self, equipment_id):
        return self.model.get_single_equipment_data(equipment_id)

    def demo_mode_prompt(self):
        self.view.demo_mode_prompt()