from os.path import join, dirname

from kivy.lang import Builder

from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog

from typing import TYPE_CHECKING, Union, Callable
if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Views.Buttons.rv_button.rv_button import RVButton
    from Views.Popups.text_field_popup.text_field_popup import TextFieldPopup
    from Views.Popups.multi_select_popup.multi_select_popup import MultiSelectPopup


class ConfirmDelete(MDDialog):
    def __init__(self, model: 'MainModel', item: Union[list, str], feed: str, button: Union['RVButton', None],
                 form_option: bool = False, popup: Union['TextFieldPopup', 'MultiSelectPopup'] = None, **kwargs):
        self.feed = 'Incomplete Forms' if feed == 'today' else feed
        if isinstance(item, list):
            self.item = ", ".join(item)
            self.item_list = item
        else:
            self.item_list = []
            self.item = item
        self.model = model
        self.text = f"Are you sure you want to delete {self.item} from {self.feed}?"
        self.button = button
        self.form_option = form_option
        self.popup = popup
        self.buttons = [MDFlatButton(text="Cancel", on_release=self.dismiss),
                        MDRaisedButton(text="Delete", on_release=self.delete_item)]
        super().__init__(**kwargs)

    def delete_item(self, obj):
        if not self.form_option:
            self.model.select_delete_item(self.button)
        else:
            self.popup.content_cls.delete_field(self.item)
        self.dismiss()


Builder.load_file(join(dirname(__file__), "confirm_delete.kv"))
