from os.path import join, dirname

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty

from kivymd.uix.screen import MDScreen

from Views.Buttons.rv_button.rv_button import RVButton

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Controller.main_screen_controller import MainScreenController


class MainScreen(MDScreen):
    controller: 'MainScreenController' = ObjectProperty()
    model: 'MainModel' = ObjectProperty()
    previous_screen = StringProperty(allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_leave(self, *args):
        screen_manager = self.controller.main_controller.screen_manager
        next_screen = screen_manager.get_screen(screen_manager.current)
        next_screen.previous_screen = self.name

    def on_pre_enter(self):
        Clock.schedule_once(self.update_fab_pos, 0.3)

    def update_fab_pos(self, *args):
        self.ids.speed_dial._update_pos_buttons(Window, Window.width, Window.height)

    def add_widgets_to_feed(self, new_feed: dict, title: str, deletable: bool):
        for n in new_feed:
            widget = RVButton(id=n['id'], deletable=True, controller=self.controller, model=self.controller.model) \
                if deletable else RVButton(id=n['id'], controller=self.controller, model=self.controller.model)
            if 'equipment' in title:
                widget.equipment = True
            widget.text = n['text']
            if 'forms' not in title:
                widget.secondary_text = n['secondary_text']
                widget.tertiary_text = n['tertiary_text']
            widget.feed = self.controller.feed
            widget.screen_manager = self.manager
            self.ids.main_feed.add_widget(widget)


Builder.load_file(join(dirname(__file__), "main_screen.kv"))
