from os.path import join, dirname

from kivy.lang import Builder
from kivy.metrics import dp

from Views.Popups.confirm_delete.confirm_delete import ConfirmDelete
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar

from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Controller.form_view_controller import FormViewController


class TextFieldPopup(MDDialog):
    def __init__(self, model: 'MainModel', controller: 'FormViewController', title: str, ind: str, db: list,
                 selected: str = None, plan_option: bool = False, **kwargs):
        self.buttons = [MDFlatButton(text='Cancel', on_press=self.dismiss),
                        MDRaisedButton(text='Select', on_press=self.submit)]
        super().__init__(**kwargs)
        self.content_cls.popup = self
        self.selected = selected
        if self.selected:
            self.content_cls.ids.dropdown.text = self.selected
        self.title = title
        self.id = ind
        self.model = model
        self.controller = controller
        self.db = db
        self.signatures = None
        self.plan_option = plan_option

    def set_item(self):
        self.selected = self.content_cls.ids.dropdown.text
        for s in self.model.single:
            if s.id == self.id:
                s.select()
                s.add_button_text(self.selected)
                break

    def delete_item(self, value):
        if not value:
            Snackbar(text='Entry cannot be empty').open()
            return
        self.content_cls.confirm_delete_field(value)

    def submit(self, obj):
        self.set_item()
        if not self.selected:
            Snackbar(text='Entry cannot be empty').open()
            return
        if self.content_cls.ids.save.active:
            self.add()
        if not self.plan_option:
            self.controller.view.get_tree()
            self.controller.save_fields(popup=self, number='single')
        else:
            self.model.form_view_fields['plan'].update({f"{self.id.split(' - ')[-1]}": self.selected})
            self.controller.view.get_tree()
            for r in self.model.single:
                if r.id.split(' - ')[-1] in self.model.form_view_fields['plan']:
                    r.select()
                    r.add_button_text(self.selected)
        self.dismiss()

    def add(self):
        if not self.db:
            Snackbar(text='Items cannot be added to this list from here').open()
            return
        self.content_cls.add_field()


class TextFieldPopupContent(MDBoxLayout):
    def __init__(self, model: 'MainModel', controller: 'FormViewController', pre_select: list,
                 popup: 'TextFieldPopup' = None, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.controller = controller
        self.popup = popup
        self.pre_select = [{"text": f"{p}", "viewclass": "ListItem", "height": dp(56), 'popup_content': self,
                            "on_release": lambda x=f"{p}": self.call_back(x)} for p in pre_select]
        self.menu = MDDropdownMenu(items=self.pre_select, caller=self.ids.dropdown.arrow, width_mult=6)
        self.ids.dropdown.menu = self.menu

    def call_back(self, *args):
        self.popup.selected = args[0]
        self.ids.dropdown.text = args[0]
        self.menu.dismiss()

    def add_list_item(self, list_item: str):
        self.pre_select.append({"text": f"{list_item}", "viewclass": "ListItem", "height": dp(56), 'popup_content': self,
                                "on_release": lambda x=f"{list_item}": self.call_back(x)})

    def add_field(self):
        if self.ids.dropdown.text and self.popup.db and not self.popup.plan_option:
            self.controller.view.get_tree()
            self.update_fields(self.model.add_form_option, [self.popup, self.ids.dropdown.text])
        if not self.popup.db and self.popup.plan_option:
            Snackbar(text='Items cannot be added to this list from here').open()

    def confirm_delete_field(self, value):
        popup = ConfirmDelete(item=value, feed=self.popup.title, button=None,
                              form_option=True, popup=self.popup, model=self.model)
        popup.open()

    def delete_field(self, value):
        if not self.popup.db:
            Snackbar(text='Items cannot be deleted from this list from here').open()
            return
        if self.popup.model.is_undeletable(self.popup.title, value):
            Snackbar(text='This item cannot be deleted').open()
            return
        self.update_fields(func=self.model.delete_form_option, param=[self.popup, value], delete=True)

    def update_fields(self, func: Callable, param: list, delete: bool = False):
        options, single_option_fields = func(param)
        widget = next((s for s in single_option_fields if self.popup.id == s.id), None)
        widget.pre_select = options
        if param[1] == self.popup.selected and delete:
            self.ids.dropdown.text = ''
            self.popup.selected = None
            self.model.form_view_fields[self.popup.id] = ''
            widget.un_select()
            widget.remove_button_text()
            for item in self.menu.items:
                if item['text'] == param[1]:
                    self.menu.items.remove(item)
                    self.menu.dismiss()
                    break


class RightIcon(IRightBodyTouch, MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_release(self, *args):
        popup = self.parent.parent.popup_content.popup
        popup.delete_item(self.parent.parent.text)


class ListItem(OneLineAvatarIconListItem):
    pass


Builder.load_file(join(dirname(__file__), "text_field_popup_content.kv"))
Builder.load_file(join(dirname(__file__), "right_icon.kv"))
