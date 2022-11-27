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

from colors import colors


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
        # Window.size = (400, 600)
        Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
        Window.softinput_mode = 'below_target'
        self.theme_cls.theme_style = "Dark"
        self.colors = colors[self.theme_cls.theme_style]
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = "Gray"
        self.theme_cls.material_style = 'M3'
        return self.main_controller.start_up()

    def on_pause(self):
        return True


if __name__ == '__main__':
    Hnnnng().run()
