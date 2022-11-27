from os.path import join, dirname

from kivy.lang import Builder
from kivy.properties import ObjectProperty

from Views.Popups.equipment_service.equipment_service import EquipmentServicePopupContent, EquipmentService
from kivymd.uix.screen import MDScreen

from Views.Buttons.rv_button.rv_button import RVButton

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Controller.main_screen_controller import MainScreenController


class MainScreen(MDScreen):
    controller: 'MainScreenController' = ObjectProperty()
    model: 'MainModel' = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_widgets_to_feed(self, new_feed: dict, title: str, deletable: bool):
        for n in new_feed:
            widget = RVButton(id=n['id'], deletable=True, controller=self.controller, model=self.controller.model) \
                if deletable else RVButton(id=n['id'], controller=self.controller, model=self.controller.model)
            if 'equipment' in title:
                widget.equipment = True
            widget.text = n['text']
            widget.feed = self.controller.feed
            widget.screen_manager = self.manager
            self.ids.main_feed.add_widget(widget)


Builder.load_file(join(dirname(__file__), "main_screen.kv"))
