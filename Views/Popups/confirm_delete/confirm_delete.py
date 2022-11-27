from os.path import join, dirname

from kivy.lang import Builder

from kivymd.uix.button import MDFlatButton
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
                        MDFlatButton(text="Delete", on_release=self.delete_item)]
        super().__init__(**kwargs)

    def delete_item(self, obj):
        if not self.form_option:
            self.model.select_delete_item(self.button)
        else:
            self.delete_field()
        self.dismiss()

    def delete_field(self):
        if self.item_list:
            widget_list = {x.instance_item.text: x for x in self.popup.content_cls.ids.selection_list.children}
            for list_item in self.item_list:
                self.update_fields(func=self.model.delete_form_option,
                                   param=[self.popup, list_item])
                if list_item in widget_list:
                    self.popup.content_cls.ids.selection_list.remove_widget(widget_list[list_item])
        else:
            self.update_fields(func=self.model.delete_form_option, param=[self.popup, self.item])
        self.popup.dismiss()

    def update_fields(self, func: Callable, param: list):
        options, option_fields = func(param)
        widget = next((o for o in option_fields if self.popup.id == o.id), None)
        if self.item_list:
            widget.selections = options
        else:
            widget.pre_select = options
            if self.item == self.popup.selected:
                self.popup.content_cls.ids.text_field.text = ''
                self.popup.selected = None
                self.model.form_view_fields[self.popup.id] = ''
                widget.un_select()
                widget.remove_button_text()


Builder.load_file(join(dirname(__file__), "confirm_delete.kv"))
