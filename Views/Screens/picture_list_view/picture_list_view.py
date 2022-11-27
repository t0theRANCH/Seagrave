from os.path import join, dirname

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from Views.Buttons.image_button.image_button import PictureButtonContainer

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Controller.picture_list_view_controller import PictureListViewController


class PictureListView(MDScreen):
    controller: 'PictureListViewController' = ObjectProperty()
    model: 'MainModel' = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pictures = None
        self.tiles = []

    def populate_grid(self):
        picture_view_controller = self.controller.main_controller.picture_view_controller
        for k, v in self.pictures.items():
            tile = PictureButtonContainer(source=v['path'], tag=v['path'].split('/')[-1], picture_id=v,
                                          controller=picture_view_controller)
            self.view.ids.container.add_widget(tile)
            self.tiles.append(tile)

    def clear_grid(self):
        for t in self.tiles:
            self.ids.container.remove_widget(t)
        self.tiles = []
        self.pictures = None


Builder.load_file(join(dirname(__file__), "picture_list_view.kv"))
