from os.path import join, dirname

from kivy.lang import Builder

from kivymd.uix.boxlayout import MDBoxLayout

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Controller.site_view_controller import SiteViewController


class PictureContent(MDBoxLayout):
    def __init__(self, controller: 'SiteViewController', picture_data, **kwargs):
        super().__init__(**kwargs)
        self.picture_data = picture_data
        self.controller = controller
        self.phone = self.controller.model.phone

    def add_picture(self):
        if self.phone:
            self.phone.open_file_picker(instance_item=None)

    def view_pictures(self):
        self.controller.main_controller.picture_list_view_controller.populate_grid(self.picture_data)
        self.controller.main_controller.change_screen('picture_list_view')


Builder.load_file(join(dirname(__file__), "picture_content.kv"))
