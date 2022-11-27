from os.path import join, dirname

from kivy.lang import Builder
from kivy.metrics import dp

from Views.Popups.confirm_delete.confirm_delete import ConfirmDelete
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar

from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Controller.form_view_controller import FormViewController


class TextFieldPopup(MDDialog):
    def __init__(self, model: 'MainModel', controller: 'FormViewController', title: str, ind: str, db: list,
                 selected: str = None, plan_option: bool = False, **kwargs):
        self.buttons = [MDRaisedButton(text='Delete', on_press=self.delete_item,
                                       md_bg_color=(0.545, 0.431, 0.376, 1)),
                        MDFlatButton(text='Cancel', on_press=self.dismiss),
                        MDFlatButton(text='Select', on_press=self.submit)]
        super().__init__(**kwargs)
        self.content_cls.popup = self
        self.selected = selected
        if self.selected:
            self.content_cls.ids.text_field.text = self.selected
        self.title = title
        self.id = ind
        self.model = model
        self.controller = controller
        self.db = db
        self.signatures = None
        self.plan_option = plan_option

    def set_item(self):
        self.selected = self.content_cls.ids.text_field.text
        for s in self.model.single:
            if s.id == self.id:
                s.add_button_text(self.content_cls.ids.text_field.text)

    def delete_item(self, obj):
        self.set_item()
        if not self.selected:
            Snackbar(text='Entry cannot be empty').open()
            return
        self.content_cls.delete_field()

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
        self.pre_select = [{"text": f"{p}", "viewclass": "OneLineListItem", "height": dp(56),
                            "on_release": lambda x=f"{p}": self.call_back(x)} for p in pre_select]
        self.menu = MDDropdownMenu(items=self.pre_select, caller=self.ids.open_menu, width_mult=4)

    def call_back(self, *args):
        self.popup.selected = args[0]
        self.ids.text_field.text = args[0]
        self.menu.dismiss()

    def add_list_item(self, list_item: str):
        self.pre_select.append({"text": f"{list_item}", "viewclass": "OneLineListItem", "height": dp(56),
                                "on_release": lambda x=f"{list_item}": self.call_back(x)})

    def add_field(self):
        if self.ids.text_field.text and self.popup.db and not self.popup.plan_option:
            self.controller.view.get_tree()
            self.update_fields(self.model.add_form_option, self.popup)
        if not self.popup.db and self.popup.plan_option:
            Snackbar(text='Items cannot be added to this list from here').open()

    def delete_field(self):
        popup = ConfirmDelete(item=self.ids.text_field.text, feed=self.popup.title, button=None,
                              form_option=True, popup=self.popup, model=self.model)
        popup.open()

    def update_fields(self, func: Callable, param: 'TextFieldPopup'):
        options, single_option_fields = func(param)
        widget = next((s for s in single_option_fields if self.popup.id == s.id), None)
        widget.pre_select = options


Builder.load_file(join(dirname(__file__), "text_field_popup_content.kv"))
