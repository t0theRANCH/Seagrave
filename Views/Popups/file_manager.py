from kivy.core.window import Window

from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.snackbar import Snackbar

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Controller.site_view_controller import SiteViewController


class FileManager(MDFileManager):
    def __init__(self, controller: 'SiteViewController', **kwargs):
        super().__init__(preview=True, **kwargs)
        Window.bind(on_keyboard=self.events)
        self.controller = controller
        self.path = '~'
        self.exit_manager = self.close_manager
        self.select_path = self.select_file
        self.manager_open = False

    def close_manager(self, *args):
        self.close()
        self.manager_open = False

    def select_file(self, path):
        if file_to_upload := self.controller.model.select_image_to_upload(path=path, file_type='pictures'):
            self.close_manager()
        else:
            Snackbar(text='Picture must be a JPG or PNG')
            return
        self.close_manager()
        self.controller.remove_widgets()
        self.controller.switch_to_site_view(site_id=self.controller.model.current_site)
        self.controller.view.on_pre_enter()

    def events(self, instance, keyboard, keycode, text, modifiers):
        if keyboard in (1001, 27) and self.manager_open:
            self.file_manager.back()
        return True