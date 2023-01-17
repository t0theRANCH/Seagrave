import shutil
from os import listdir
from os.path import join, dirname

import kivy
from kivy import Config, platform
from kivymd.app import MDApp
from kivy.core.window import Window

from Model.main_model import MainModel
from Controller.main_controller import MainController
from Controller.login_screen_controller import LoginScreenController
from Controller.main_screen_controller import MainScreenController
from Controller.site_view_controller import SiteViewController
from Controller.form_view_controller import FormViewController
from Controller.picture_list_view_controller import PictureListViewController
from Controller.picture_view_controller import PictureViewController


class Hnnnng(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = MainModel()
        self.main_controller = MainController(self.model)
        self.load_controllers()
        self.colors = None

    def load_controllers(self):
        self.main_controller.login_controller = LoginScreenController(self.model)
        self.main_controller.main_screen_controller = MainScreenController(self.model)
        self.main_controller.site_view_controller = SiteViewController(self.model)
        self.main_controller.form_view_controller = FormViewController(self.model)
        self.main_controller.picture_list_view_controller = PictureListViewController(self.model)
        self.main_controller.picture_view_controller = PictureViewController(self.model)

    def build(self):
        if platform == 'linux':
            Window.size = (400, 600)
        self.set_keyboard_height()
        self.set_theme()
        return self.main_controller.start_up()

    def set_theme(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = "Gray"
        self.theme_cls.material_style = 'M3'

    @staticmethod
    def set_keyboard_height():
        Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
        Window.softinput_mode = 'below_target'

    def on_pause(self):
        return True


if __name__ == '__main__':
    Hnnnng().run()
