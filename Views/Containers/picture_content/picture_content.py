from os.path import join, dirname

from kivy.lang import Builder

from kivymd.uix.boxlayout import MDBoxLayout

from Views.Popups.file_manager import FileManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Controller.site_view_controller import SiteViewController


class PictureContent(MDBoxLayout):
    def __init__(self, controller: 'SiteViewController', picture_data, **kwargs):
        super().__init__(**kwargs)
        self.picture_data = picture_data
        self.controller = controller
        self.phone = self.controller.model.phone
        self.file_manager = FileManager(self.controller)
        self.set_file_path()

    def set_file_path(self):
        if self.phone:
            self.file_manager.path = self.phone.get_primary_storage_path()

    def add_picture(self):
        if self.phone:
            self.phone.get_storage_permissions()
        self.file_manager.show(self.file_manager.path)
        self.file_manager.manager_open = True

    def view_pictures(self):
        self.controller.main_controller.picture_list_view_controller.populate_grid(self.picture_data)
        self.controller.main_controller.change_screen('picture_list_view')


Builder.load_file(join(dirname(__file__), "picture_content.kv"))
