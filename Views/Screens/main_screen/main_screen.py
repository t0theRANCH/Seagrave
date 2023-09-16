import time
from os.path import join, dirname

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.button.button import MDFloatingBottomButton, MDFloatingRootButton

from kivymd.uix.screen import MDScreen
from kivymd.uix.taptargetview import MDTapTargetView

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
        self.tap_target_view = None

    def set_button_position(self, *args):
        self.controller.main_controller.view.update_fab_pos(self.ids.speed_dial)

    def on_leave(self, *args):
        screen_manager = self.controller.main_controller.screen_manager
        next_screen = screen_manager.get_screen(screen_manager.current)
        next_screen.previous_screen = self.name

    def on_pre_enter(self):
        Clock.schedule_once(self.set_button_position, 0.3)
        Clock.schedule_once(self.add_tap_target, 3)
        Clock.schedule_once(self.check_tutorial, 4)

    def check_tutorial(self, *args):
        if self.model.settings['Tutorials'] and self.model.settings['Tutorial']['main_screen']:
            self.tap_target_view.start()
            self.model.update_tutorial_settings('main_screen', False)

    def add_tap_target(self, *args):
        speed_dial = None
        for child in self.ids.speed_dial.children:
            if isinstance(child, MDFloatingRootButton):
                speed_dial = child
        self.tap_target_view = MDTapTargetView(
            widget=speed_dial,
            title_text="Add New Item",
            description_text="Add a new site, equipment, or form",
            widget_position="right_bottom",
            cancelable=True
        )


    def tap_target(self):
        if self.tap_target_view.state == "close":
            self.tap_target_view.start()
        else:
            self.tap_target_view.stop()

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
