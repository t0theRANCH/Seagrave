from os.path import join, dirname

from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, ListProperty, DictProperty
from kivy.metrics import dp
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.list import BaseListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDTimePicker, MDDatePicker

from Views.Popups.risk_popup.risk_popup import RiskPopup, RiskPopupContent
from Views.Popups.signature_popup.signature_popup import SignaturePopup, SignaturePopupContent
from Views.Popups.text_field_popup.text_field_popup import TextFieldPopup, TextFieldPopupContent
from Views.Popups.multi_select_popup.multi_select_popup import MultiSelectPopup, MultiSelectPopupContent

from Forms.form_fields.base_form_widgets import BaseFormWidget, FormWidget

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Views.Screens.form_view.form_view import FormView


class SingleOption(FormWidget):
    plan_field = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.plan_field:
            self.pre_select = ["Eliminate", "Substitute", "Engineered Controls", "Administrative Controls",
                               "Personal Protective Equipment"]

    def on_release(self):
        if self.plan_field:
            selected = self.model.form_view_fields['plan'][self.id.split(" - ")[-1]] or None
        else:
            selected = self.model.form_view_fields[self.id] if self.id in self.model.form_view_fields else None
        pops = TextFieldPopup(model=self.model, controller=self.controller, title=self.title, db=self.db, ind=self.id,
                              selected=selected, plan_option=self.plan_field, type='custom',
                              content_cls=TextFieldPopupContent(pre_select=self.pre_select, model=self.model,
                                                                controller=self.controller))
        pops.open()


class SignatureOption(BaseFormWidget):
    person = StringProperty()
    sign_type = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.person = self.person.capitalize()
        self.text = f"{self.sign_type} Here: {self.person}"

    def on_release(self):
        signature_popup = SignaturePopup(model=self.model, controller=self.controller, signature=self.person,
                                         sign_type=self.sign_type,
                                         content_cls=SignaturePopupContent(), type='custom')
        signature_popup.open()


class SingleOptionDatePicker(FormWidget):
    time = BooleanProperty(True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_save(self, instance, value, date_range):
        self.selection = value.strftime("%d/%m/%Y")
        if self.time:
            self.show_time_picker()
            return
        self.fill_in_response(self.selection)

    def on_release(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def show_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.get_time)
        time_dialog.open()

    def get_time(self, instance, time):
        t = time.strftime("%H:%M")
        dt = f"{self.selection} {t}"
        self.fill_in_response(dt, time)

    def fill_in_response(self, dt, time=None):
        self.model.form_view_fields[self.id] = dt
        self.select()
        self.add_button_text(dt)
        if not time:
            time = self.selection
        return time


class MultiOptionButton(FormWidget):
    selection_db = DictProperty(allownone=True)
    selections = ListProperty(allownone=True)
    field_ids = ListProperty(allownone=True)
    equipment = BooleanProperty(False)
    signature = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.equipment:
            self.field_ids = [self.selection_db[x] for x in self.selection_db]
            self.selections = {x: '' for x in self.selection_db}
        else:
            self.field_ids = None
            self.selections = self.selections

    def on_release(self):
        selected = self.model.form_view_fields[self.id] or None
        pops = MultiSelectPopup(title=self.title, ind=self.id, db=self.db,
                                selections=self.selections, type='custom', selected=selected,
                                content_cls=MultiSelectPopupContent(field_ids=self.field_ids, equipment=self.equipment),
                                model=self.model, controller=self.controller)

        pops.open()


class RiskButton(FormWidget):
    view: 'FormView' = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_release(self):
        pops = RiskPopup(type='custom',
                         content_cls=RiskPopupContent(ind=self.id, view=self.view, model=self.model, title=self.title))
        pops.open()


class SingleOptionButton(FormWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = 'Work to Be Done'
        self.pre_select = [{"text": f"{p}", "viewclass": "OneLineListItem", "height": dp(56),
                            "on_release": lambda x=f"{p}": self.call_back(x)} for p in self.pre_select]
        self.menu = MDDropdownMenu(items=self.pre_select, caller=self, width_mult=4)

    def on_release(self):
        self.menu.open()

    def call_back(self, *args):
        self.select()
        self.add_button_text(args[0])
        self.menu.dismiss()
        self.add_tasks()

    def add_tasks(self):
        self.controller.view.get_tree()
        button = next(m for m in self.controller.model.single if m.id == 'task')
        button.pre_select = list(self.controller.model.forms['Field Level Hazard Assessment'][self.secondary_text])
        if len(button.db) > 1:
            button.db[1] = self.secondary_text
        else:
            button.db.append(self.secondary_text)
        self.controller.model.form_view_fields['work_to_be_done'] = self.secondary_text


class CheckBoxOption(GridLayout, BaseListItem):
    option = BooleanProperty(False)

    def __init__(self, ind, text, mandatory=True, divide=False, *args, **kwargs):
        self.height = dp(64)
        super().__init__(*args, **kwargs)
        self.id = ind
        self.ids.label.text = text
        self.mandatory = mandatory
        self.bg_color = 'black'
        self.divide = divide
        self.filled = False

    def on_option(self, instance, value):
        if value:
            self.ids.cb.active = True


Builder.load_file(join(dirname(__file__), "checkbox.kv"))
