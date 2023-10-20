from kivy._event import EventDispatcher

from Views.Screens.picture_view.picture_view import PictureView

from kivy.properties import ObjectProperty, BooleanProperty

from typing import TYPE_CHECKING, Union


if TYPE_CHECKING:
    from Controller.main_controller import MainController
    from Model.main_model import MainModel
    from kivymd.uix.dialog import MDDialog


class PictureViewController(EventDispatcher):
    main_controller: 'MainController' = ObjectProperty()
    demo_mode: bool = BooleanProperty()

    def __init__(self, model: 'MainModel', **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.view = PictureView(name='picture_view', controller=self, model=self.model)
        self.speed_dial_data = {"Set as Banner Image": ["image-edit", "on_release", self.set_as_banner_image],
                                "Add a note": ["note-plus", "on_release", self.add_note],
                                "Back": ["arrow-left-circle", "on_release", self.go_back]
                                }
        self.picture_id = None
        self.popup: Union[None, MDDialog] = None
        self.view.bind(orientation=self.on_orientation)
        self.set_speed_dial_data()

    def switch_screen(self, tag, picture_id):
        self.view.ids.hero_to.tag = tag
        self.view.picture_id = picture_id
        self.main_controller.change_screen("picture_view", slide=True)

    def on_orientation(self):
        if self.view.orientation == 'portrait':
            self.view.on_portrait()
        else:
            self.view.on_landscape()

    def set_speed_dial_data(self):
        self.view.ids.speed_dial.data = self.speed_dial_data

    def close_speed_dial(self):
        if self.view.ids.speed_dial.state == "open":
            self.view.ids.speed_dial.close_stack()

    def add_note(self, obj):
        self.view.open_add_note_popup()

    def dismiss(self, obj):
        self.view.dismiss_popup()

    def confirm_add_note(self, obj):
        text_field = self.popup.content_cls.text_to_add
        if not text_field.text:
            text_field.error = True
            text_field.helper_text = "Field cannot be empty"
            return
        text_field.error = False
        self.model.add_note_to_picture(picture_id=self.picture_id, note=text_field.text)

    def confirm_add_image(self, obj):
        self.model.set_banner_image(self.picture_id)

    def set_as_banner_image(self, obj):
        self.view.open_set_as_banner_image_popup()

    def go_back(self, obj):
        self.main_controller.screen_manager.current_heroes = []
        self.main_controller.change_screen('picture_list_view', slide=True, direction='right')
