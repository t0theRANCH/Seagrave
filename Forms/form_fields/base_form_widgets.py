from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty, ObjectProperty, BooleanProperty
from kivymd.uix.list import BaseListItem

from Model.main_model import MainModel

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Controller.form_view_controller import FormViewController


class BaseFormWidget(BaseListItem):
    controller: 'FormViewController' = ObjectProperty()
    model: 'MainModel' = ObjectProperty()
    ind: str = StringProperty()
    title: str = StringProperty()
    mandatory: bool = BooleanProperty(True)
    divide: bool = BooleanProperty(False)
    filled: bool = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = self.ind
        self.height = dp(64)
        self.bg_color = 'black'

    def on_title(self, instance, value):
        self.text = value

    def select(self):
        self.bg_color = self.model.primary_color  # (0.404, 0.545, 0.376, 1)
        self.filled = True

    def un_select(self):
        self.bg_color = 'black'
        self.filled = False


class FormWidget(BaseFormWidget):
    pre_select = ListProperty()
    selection = StringProperty(allownone=True)
    db = ListProperty(allownone=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_button_text(self, selection):
        if isinstance(selection, list):
            self.selection = ', '.join(selection)
        else:
            self.selection = selection
        self.secondary_text = self.selection

    def remove_button_text(self):
        self.selection = None
        self.secondary_text = ''
