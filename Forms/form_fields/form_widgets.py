from kivy.properties import ObjectProperty
from kivy.metrics import dp
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.list import BaseListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDTimePicker, MDDatePicker

from Views.Popups.risk_popup.risk_popup import RiskPopup, RiskPopupContent
from Views.Popups.signature_popup.signature_popup import SignaturePopup, SignaturePopupContent
from Views.Popups.text_field_popup.text_field_popup import TextFieldPopup, TextFieldPopupContent
from Views.Popups.multi_select_popup.multi_select_popup import MultiSelectPopup, MultiSelectPopupContent

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Controller.form_view_controller import FormViewController
    from Views.Screens.form_view.form_view import FormView


class CheckBoxOption(GridLayout, BaseListItem):
    def __init__(self, ind, text, mandatory=True, divide=False, **kwargs):
        self.height = dp(64)
        super().__init__(**kwargs)
        self.id = ind
        self.ids.label.text = text
        self.option = False
        self.mandatory = mandatory
        self.bg_color = 'black'
        self.divide = divide
        self.filled = False


class SingleOption(BaseListItem):
    def __init__(self, model: 'MainModel', controller: 'FormViewController', ind: str, title: str, pre_select: Union[list, None],
                 selection=None, db=None, mandatory=True, divide=False, filled=False,
                 signatures=False, plan_field=False, **kwargs):
        self.height = dp(64)
        super().__init__(**kwargs)
        self.model = model
        self.controller = controller
        self.id = ind
        if plan_field:
            self.pre_select = ["Eliminate", "Substitute", "Engineered Controls", "Administrative Controls",
                               "Personal Protective Equipment"]

        else:
            self.pre_select = pre_select
        self.title = title
        self.text = title
        self.selection = selection
        self.mandatory = mandatory
        self.bg_color = 'black'
        self.divide = divide
        self.db = db
        self.filled = filled
        self.signatures = signatures
        self.plan_field = plan_field

    def select(self):
        self.bg_color = (0.404, 0.545, 0.376, 1)
        self.filled = True

    def un_select(self):
        self.bg_color = 'black'
        self.filled = False

    def add_button_text(self, selection):
        self.selection = selection
        self.secondary_text = selection

    def remove_button_text(self):
        self.selection = None
        self.secondary_text = ''

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


class SignatureOption(BaseListItem):
    def __init__(self, ind, model: 'MainModel', controller: 'FormViewController', person, sign_type, mandatory=True, **kwargs):
        self.height = dp(64)
        super().__init__(**kwargs)
        self.id = ind
        self.model = model
        self.controller = controller
        self.mandatory = mandatory
        self.bg_color = 'black'
        self.person = person.capitalize()
        self.sign_type = sign_type
        self.text = f"{self.sign_type} Here: {self.person}"
        self.divide = False
        self.filled = False

    def select(self):
        self.bg_color = (0.404, 0.545, 0.376, 1)
        self.filled = True

    def un_select(self):
        self.bg_color = 'black'
        self.filled = False

    def on_release(self):
        signature_popup = SignaturePopup(model=self.model, controller=self.controller, signature=self.person,
                                         sign_type=self.sign_type,
                                         content_cls=SignaturePopupContent(), type='custom')
        signature_popup.open()


class SingleOptionButton(BaseListItem):
    def __init__(self, ind, pre_select, controller: 'FormViewController', mandatory=True, divide=False, selected=None, **kwargs):
        self.height = dp(64)
        super().__init__(**kwargs)
        self.controller = controller
        self.id = ind
        self.text = 'Work to Be Done'
        self.pre_select = [{"text": f"{p}", "viewclass": "OneLineListItem", "height": dp(56),
                            "on_release": lambda x=f"{p}": self.call_back(x)} for p in pre_select]
        self.mandatory = mandatory
        self.bg_color = 'black'
        self.menu = MDDropdownMenu(items=self.pre_select, caller=self, width_mult=4)
        self.divide = divide
        self.selected = selected
        self.filled = False

    def on_release(self):
        self.menu.open()

    def call_back(self, *args):
        self.text = args[0]
        self.menu.dismiss()
        self.add_tasks()

    def add_tasks(self):
        self.controller.view.get_tree()
        button = next(m for m in self.controller.model.multi if m.id == 'tasks')
        button.selections = list(self.controller.model.forms['Field Level Hazard Assessment'][self.text])
        if len(button.db) > 1:
            button.db[1] = self.text
        else:
            button.db.append(self.text)
        self.controller.model.form_view_fields['work_to_be_done'] = self.text
        self.selected = self.text
        self.filled = True
        self.bg_color = (0.404, 0.545, 0.376, 1)


class SingleOptionDatePicker(GridLayout, BaseListItem):
    add_new = ObjectProperty(None)
    pre_select = ObjectProperty(None)

    def __init__(self, ind, model: 'MainModel', mandatory=True, divide=False, filled=False, time=True, **kwargs):
        self.height = dp(64)
        super().__init__(**kwargs)
        self.id = ind
        self.model = model
        self.time = ''
        self.mandatory = mandatory
        self.bg_color = 'black'
        self.divide = divide
        self.filled = filled
        self.time = time

    def select(self):
        self.bg_color = (0.404, 0.545, 0.376, 1)
        self.filled = True

    def un_select(self):
        self.bg_color = 'black'
        self.filled = False

    def add_button_text(self, selection):
        self.time = selection
        self.secondary_text = selection

    def remove_button_text(self):
        self.time = ''
        self.secondary_text = ''

    def on_save(self, instance, value, date_range):
        self.time = value.strftime("%d/%m/%Y")
        if self.time:
            self.show_time_picker()
            return
        self.fill_in_response(self.time)

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def show_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_time)
        time_dialog.open()

    def get_time(self, instance, time):
        t = time.strftime("%H:%M")
        dt = f"{self.time} {t}"
        self.fill_in_response(dt, time)

    def fill_in_response(self, dt, time=None):
        self.model.form_view_fields[self.id] = dt
        self.ids.add_new.text = dt
        self.filled = True
        if not time:
            time = self.time
        return time


class MultiOptionButton(BaseListItem):
    def __init__(self, model: 'MainModel', controller: 'FormViewController', ind, selections, title,
                 mandatory=True, divide=False, db=None, signature=False, equipment=False, **kwargs):
        self.height = dp(64)
        super().__init__(**kwargs)
        self.model = model
        self.controller = controller
        self.id = ind
        self.equipment = equipment
        if self.equipment:
            self.field_ids = [selections[x] for x in selections]
            self.selections = {x: '' for x in selections}
        else:
            self.field_ids = None
            self.selections = selections
        self.title = title
        self.mandatory = mandatory
        self.bg_color = 'black'
        self.divide = divide
        self.db = db
        self.signature = signature
        self.filled = False

    def select(self):
        self.bg_color = (0.404, 0.545, 0.376, 1)
        self.filled = True

    def un_select(self):
        self.bg_color = 'black'
        self.filled = False

    def add_button_text(self, selections):
        self.secondary_text = ", ".join(selections)

    def remove_button_text(self):
        self.secondary_text = ''

    def on_release(self):
        selected = self.model.form_view_fields[self.id] or None
        pops = MultiSelectPopup(title=self.title, screen_manager=self.got_root, ind=self.id, db=self.db,
                                selections=self.selections, type='custom', selected=selected, signatures=self.signature,
                                content_cls=MultiSelectPopupContent(field_ids=self.field_ids, equipment=self.equipment),
                                model=self.model, controller=self.controller)

        pops.open()


class RiskButton(BaseListItem):
    def __init__(self, model: 'MainModel', view: 'FormView', ind, title, mandatory=True, selected=None, **kwargs):
        self.height = dp(64)
        super().__init__(**kwargs)
        self.id = ind
        self.model = model
        self.view = view
        self.title = title
        self.mandatory = mandatory
        self.bg_color = 'black'
        self.text = self.title
        self.filled = False
        self.selected = [] if selected is None else selected

    def select(self):
        self.bg_color = (0.404, 0.545, 0.376, 1)
        self.filled = True

    def un_select(self):
        self.bg_color = 'black'
        self.filled = False

    def add_button_text(self, selection):
        self.secondary_text = selection

    def remove_button_text(self):
        self.secondary_text = ''

    def on_release(self):
        pops = RiskPopup(type='custom',
                         content_cls=RiskPopupContent(ind=self.id, view=self.view, model=self.model, title=self.title))
        pops.open()

