import traceback
from os import remove

import kivy
from kivy import platform
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
from api_requests import open_request, upload


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
        if platform in ['linux', 'windows', 'macosx', 'darwin']:
            Window.size = (400, 600)
        self.set_keyboard_height()
        self.set_theme()
        if not self.model.settings['cleanup']:
            self.on_stop()
        settings = dict(self.model.settings)
        settings['cleanup'] = False
        self.model.save_db_file('settings', settings)
        return self.main_controller.start_up()

    def set_theme(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = "Gray"
        self.theme_cls.material_style = 'M3'
        self.model.primary_color = self.theme_cls.primary_color

    @staticmethod
    def set_keyboard_height():
        Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
        Window.softinput_mode = 'below_target'

    def on_pause(self):
        return True

    @staticmethod
    def send_crash_report(crash_report):
        data = {'log_type': 'crash_report', 'data': str(crash_report)}
        open_request(name='log', data=data)

    def on_stop(self):
        settings = dict(self.model.settings)
        if not settings.get('Keep Me Logged In', False):
            self.model.refresh_token = ''
            self.model.access_token = ''
            self.model.id_token = ''
        if settings['Tutorials']:
            for item in settings['Tutorial']:
                settings['Tutorial'][item] = True
        self.model.update_settings('Tutorial', settings['Tutorial'])
        for file in self.model.settings['To Be Deleted']:
            remove(file)
        settings['To Be Deleted'] = []
        """for category in settings['To Be Uploaded']:
            for file in settings['To Be Uploaded'][category]:
                upload(path=file['upload_path'], local_path=file['device_path'], id_token=self.model.id_token,
                       url=self.model.secure_api_url,
                       access_token=self.model.access_token)
                settings['To Be Uploaded'][category].remove(
                    {'device_path': file['device_path'], 'upload_path': file['upload_path']})"""
        settings['cleanup'] = True

        self.model.save_db_file('settings', settings)


if __name__ == '__main__':
    try:
        app = Hnnnng()
        app.run()
    except Exception as e:
        crash_info = traceback.format_exc()
        if platform in ['linux', 'windows', 'macosx', 'darwin']:
            print(crash_info)
        else:
            Hnnnng.send_crash_report(crash_info)
