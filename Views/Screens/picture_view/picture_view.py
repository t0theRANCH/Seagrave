from os.path import join, dirname

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty, OptionProperty, StringProperty

from Views.Containers.add_note_to_picture.add_note_to_picture import AddNote
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen


from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Controller.picture_view_controller import PictureViewController


class PictureView(MDScreen):
    controller: 'PictureViewController' = ObjectProperty()
    model: 'MainModel' = ObjectProperty()
    previous_screen = StringProperty(allownone=True)
    orientation = OptionProperty("portrait", options=['portrait', 'landscape'])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popup: Union[None, MDDialog] = None

    def on_pre_enter(self):
        Clock.schedule_once(self.update_fab_pos, 0.3)

    def update_fab_pos(self, *args):
        self.ids.speed_dial._update_pos_buttons(Window, Window.width, Window.height)

    def on_leave(self, *args):
        screen_manager = self.controller.main_controller.screen_manager
        next_screen = screen_manager.get_screen(screen_manager.current)
        next_screen.previous_screen = self.name

    def on_portrait(self):
        self.ids.scatter.pos_hint = {'center_x': 0.5, 'top': 1}

    def on_landscape(self):
        self.ids.hero_to.size_hint_x = 1
        self.ids.scatter.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

    def dismiss_popup(self):
        self.popup.dismiss()
        self.popup = None

    def open_add_note_popup(self):
        self.popup = MDDialog(title='Annotate Picture', type="custom", content_cls=AddNote(),
                              buttons=[MDFlatButton(text='Cancel', on_release=self.dismiss_popup),
                                       MDFlatButton(text='Add Note', on_release=self.controller.confirm_add_note)])
        self.popup.open()

    def open_set_as_banner_image_popup(self):
        self.popup = MDDialog(text='Use this photo as the banner image for this site?', type='confirmation',
                              buttons=[MDFlatButton(text='Cancel', on_release=self.dismiss_popup),
                                       MDFlatButton(text='OK', on_release=self.controller.confirm_add_image)]
                              )
        self.popup.open()


Builder.load_file(join(dirname(__file__), "picture_view.kv"))
