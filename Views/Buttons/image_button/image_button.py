from os.path import join, dirname

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.hero import MDHeroFrom

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from Controller.picture_view_controller import PictureViewController
    from kivy.uix.image import Image


class PictureButtonContainer(ButtonBehavior, MDBoxLayout):
    def __init__(self, source, tag, controller: 'PictureViewController', picture_id, **kwargs):
        super().__init__(**kwargs)
        self.ids.picture_tile.source = source
        self.ids.hero_from.picture_tile: Image = self.ids.picture_tile
        self.ids.hero_from.tag = tag
        self.controller = controller
        self.ids.hero_from.controller = self.controller
        self.ids.hero_from.picture_id = picture_id


class PictureButton(MDHeroFrom):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller: Union[None, 'PictureViewController'] = None
        self.tag = None
        self.picture_tile: Union[None, Image] = None
        self.picture_id = None

    def on_release(self):
        def switch_screen(*args):
            self.controller.main_controller.screen_manager.current_heroes = [self.tag]
            self.controller.switch_screen(self.tag, self.picture_id)
        if self.controller.main_controller.screen_manager.current == 'picture_list_view':
            Clock.schedule_once(switch_screen, 0.2)


Builder.load_file(join(dirname(__file__), "image_button.kv"))
