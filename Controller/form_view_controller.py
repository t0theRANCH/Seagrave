from datetime import datetime
import contextlib

from kivy._event import EventDispatcher
from kivy.core.window import Window
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.widget import WidgetException

from Forms.form_compiler import CreateForm
from Views.Screens.form_view.form_view import FormView

from typing import TYPE_CHECKING, Union

from kivymd.toast import toast

if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Views.Popups.text_field_popup.text_field_popup import TextFieldPopup
    from Forms.form_fields.form_widgets import SingleOption
    from Controller.main_controller import MainController


class FormViewController(EventDispatcher):
    main_controller: 'MainController' = ObjectProperty()
    demo_mode: bool = BooleanProperty()

    def __init__(self, model: 'MainModel', **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.view = FormView(name='form_view', controller=self, model=self.model)
        self.separator = ''
        self.form = ''
        self.pops = []

    def close_speed_dial(self):
        if self.view.ids.speed_dial.state == "open":
            self.view.ids.speed_dial.close_stack()

    def switch_to_form_view(self, form_id: str):
        form = CreateForm(form_id=form_id, model=self.model, controller=self)
        func = form.populate_form_view()
        widgets = func()
        self.add_widgets_to_form_view(widgets, form.form_title)
        if form.today_form:
            self.add_saved_responses(form.form_title, form.today_form)
            self.check_signature('signatures', form.today_form)
            self.check_signature('initials', form.today_form)
        if 'Field Level' in form.form_title:
            self.add_saved_hazards()
            self.add_hazards_as_selections()
        self.view.get_tree()
        self.main_controller.site_view_controller.remove_widgets()
        if self.main_controller.nav_drawer.state == 'open':
            self.main_controller.nav_drawer.open_close()
        self.main_controller.change_screen('form_view')
        self.view.ids.speed_dial._update_pos_buttons(Window, Window.width, Window.height)

    def add_widgets_to_form_view(self, widgets: list, title: str):
        for widget in widgets:
            if widget.id not in self.model.form_view_fields:
                self.model.form_view_fields[widget.id] = ''
            self.view.ids.formview.add_widget(widget)
            if widget.divide:
                self.separator = str(widget.id)
        self.form = title
        self.model.form_view_fields['date'] = str(datetime.now().strftime("%d/%m/%Y"))
        self.model.form_view_fields['name'] = title

    def add_saved_responses(self, form_title: str, form_entry: str):
        self.model.form_view_fields = self.model.today['forms'][form_entry]
        self.view.get_tree()
        for s in self.model.single:
            s.selection = self.model.form_view_fields[s.id]
            if s.selection:
                s.select()
                s.add_button_text(s.selection)
        for m in self.model.multi:
            if self.model.form_view_fields[m.id]:
                if 'Equipment' in form_title:
                    for k in self.model.form_view_fields[m.id]:
                        self.check_equipment_for_failure(title=m.title, grade=self.model.form_view_fields[m.id][k],
                                                         component=k)
                    if not [self.model.form_view_fields[m.id][x] for x in self.model.form_view_fields[m.id]
                            if self.model.form_view_fields[m.id][x]]:
                        continue
                else:
                    m.add_button_text(self.model.form_view_fields[m.id])
                m.select()

        for c in self.model.checkbox:
            c.option = self.model.form_view_fields[c.id]
        self.view.get_tree()

    def check_equipment_for_failure(self, title: str, grade: str, component: str):
        if grade == 'R':
            self.view.get_tree()
            for key, value in self.model.forms['Equipment and Vehicle Pre-Start Checklist'][title].items():
                if key == component:
                    self.add_repairs(key, value)

    def add_repairs(self, key: str, value: str):
        with contextlib.suppress(WidgetException):
            for f in self.model.signature:
                self.view.ids.formview.remove_widget(f)
        self.view.delete_old_repair_widgets(key, value)
        self.view.add_repair_widgets(key, value)
        self.view.add_repairman_signature()

    def add_saved_hazards(self):
        if 'risk' not in self.model.form_view_fields:
            self.model.form_view_fields['risk'] = {x: '' for x in self.model.form_view_fields.get('hazards', '')}
        if 'plan' not in self.model.form_view_fields:
            self.model.form_view_fields['plan'] = {x: '' for x in self.model.form_view_fields.get('hazards', '')}
        if 'hazards' in self.model.form_view_fields:
            for m in self.model.multi:
                if m.id in 'hazards':
                    m.selections = self.model.form_view_fields['hazards']
                    self.add_risk_plan(selections=self.model.form_view_fields['hazards'])
        if 'signatures' not in self.model.form_view_fields:
            self.model.form_view_fields['signatures'] = {}
            self.model.form_view_fields['initials'] = {}

    def add_risk_plan(self, selections: list):
        for num, s in enumerate(selections):
            name = s
            button_text = f"Risk/Priority - {name}"
            self.model.form_view_fields['risk'].update({name: {"risk": '', "priority": ''}})
            self.model.form_view_fields['plan'].update({name: ''})
            self.view.add_risk_plan_widgets(name, num, button_text)
            for x in self.model.form_view_fields['risk']:
                if x not in selections:
                    self.model.form_view_fields['risk'].pop(x)
                    self.model.form_view_fields['plan'].pop(x)

    def check_signature(self, signature: str, form_entry: str):
        if signature not in self.model.today['forms'][form_entry]:
            return
        if 'workers' in self.model.today['forms'][form_entry]:
            t = signature.rstrip('atures') if 'signature' in signature else signature.rstrip('s')

            self.view.add_worker_signatures(form_entry, signature, t)

    def add_signature(self, selections: list):
        self.view.remove_signature_widgets()
        for s in selections:
            self.view.add_signature_widgets(s)
        for x in ['signatures', 'initials']:
            self.model.delete_signatures(x, selections)

    def add_hazards_as_selections(self):
        hazards = list(
            self.model.forms['Field Level Hazard Assessment'][self.model.form_view_fields['work_to_be_done']][
                self.model.form_view_fields.get('task', '')])
        hazards = list(dict.fromkeys(hazards))
        hazards.extend(self.model.forms['Field Level Hazard Assessment']['hazards'])
        for m in self.model.multi:
            if m.id == 'hazards':
                m.selections = hazards
                break

    def save_fields(self, popup: 'TextFieldPopup', number: str = 'multi', equipment: bool = False):
        self.model.form_view_fields[popup.id] = popup.selected
        if popup.signatures:
            self.add_signature(popup.selections)
        self.fill_in_machine_details(popup)
        if 'hazards' in popup.id:
            for r in self.model.risk:
                self.view.ids.formview.remove_widget(r)
            for s in self.model.single:
                if "Plans to Eliminate/Control - " in s.text:
                    self.view.ids.formview.remove_widget(s)
            self.add_risk_plan(selections=popup.selections)
        if number == 'single':
            self.colour_completed_list_items(widgets=self.model.single, popup_id=popup.id,
                                             selections=popup.selected, number='single')
        elif not equipment:
            self.colour_completed_list_items(widgets=self.model.multi, popup_id=popup.id,
                                             selections=popup.selected)
        else:
            self.colour_completed_list_items(widgets=self.model.multi, popup_id=popup.id,
                                             selections=[popup.selected[x] for x in popup.selected
                                                         if popup.selected[x]])
        if popup.title == 'Task':
            self.add_hazards_as_selections()
        if equipment:
            for x, y in popup.selections.items():
                self.check_equipment_for_failure(title=popup.title, grade=y, component=x)

        if self.model.settings['Tutorials'] and self.model.settings['Tutorial']['form_view_complete']:
            widgets = self.model.single + self.model.multi + self.model.checkbox + self.model.signature + self.model.risk
            for w in widgets:
                if not w.filled:
                    return
            self.view.tap_target()

    def colour_completed_list_items(self, widgets: list, popup_id: str, selections: Union[list, str],
                                    number: str = 'multi'):
        for w in widgets:
            if w.id == popup_id and selections:
                if number == 'single':
                    w.selected = self.model.form_view_fields[w.id]
                w.select()

    def fill_in_machine_details(self, popup: 'TextFieldPopup'):
        self.machine(popup)
        self.unit_num(popup)

    def machine(self, popup: 'TextFieldPopup'):
        equipment = {e: self.model.equipment[e] for e in self.model.equipment
                     if self.model.equipment[e]['type'] == popup.selected}
        if len(equipment) > 1:
            unit_nums = [v['unit_num'] for k, v in equipment.items()]
            sites = [f"{self.model.sites[v['site']]['customer']} - {self.model.sites[v['site']]['city']}"
                     for k, v in equipment.items()]
            for s in self.model.single:
                if s.id == 'location':
                    s.pre_select = sites
                    s.content_cls.pre_select = sites
                elif s.id == 'unit_num':
                    s.pre_select = unit_nums
                    s.content_cls.pre_select = unit_nums
        else:
            self.check_if_filled(popup=popup, third_field='unit_num', popup_field='type')

    def unit_num(self, popup: 'TextFieldPopup'):
        if 'unit_num' not in popup.id:
            return
        self.check_if_filled(popup=popup, third_field='type', popup_field='unit_num')

    def check_if_filled(self, popup: 'TextFieldPopup', third_field: str, popup_field: str):
        equipment = {e: self.model.equipment[e] for e in self.model.equipment
                     if self.model.equipment[e][popup_field] == popup.selected}

        mileage = [v['mileage'] for k, v in equipment.items()]
        site = [v['site'] for k, v in equipment.items()]
        third_item = [v[third_field] for k, v in equipment.items()]
        third_item = third_item[0] if third_item else None
        mileage = mileage[0] if mileage else None
        if third_field == 'type':
            third_field = 'machine'
        for s in self.model.single:
            self.fill_in_details(s, third_field, third_item)
            self.fill_in_details(s, 'mileage', mileage)
            if site and site[0]:
                site_entry = self.model.sites[site[0]]
                self.fill_in_details(s, 'location', f"{site_entry.get('customer', '')} - {site_entry.get('city', '')}")

    def fill_in_details(self, widget: 'SingleOption', field_name: str, value: str):
        if widget.id == field_name and not widget.filled and value:
            self.model.form_view_fields[field_name] = value
            widget.add_button_text(value)
            widget.select()

    def check_for_minimum_required_fields(self, submit):
        self.view.get_tree()
        self.model.update_field(fields=self.model.form_view_fields,
                                field_dict={c.id: c.option for c in self.model.checkbox})
        done, minimum = self.model.save_form_fields(submit=submit, separator=self.separator, form_type=self.view.type)
        return done, minimum, list(self.model.forms)

    def parse_field_check_response(self, submit):
        done, minimum, forms = self.check_for_minimum_required_fields(submit)
        if minimum == 'Duplicate Form':
            toast(text='This form has already been completed today')
            return False
        if not done:
            self.pops = minimum if isinstance(minimum, list) else [minimum]
            self.view.open_error_popup()
            return False
        return True

    def save_form(self, *args):
        self.close_speed_dial()
        if self.demo_mode:
            self.main_controller.demo_mode_prompt()
            return
        if done := self.parse_field_check_response(submit=False):
            self.remove_widgets()

    def submit_form(self, *args):
        self.main_controller.view.scrim_on()
        self.close_speed_dial()
        done = self.parse_field_check_response(submit=True)
        if not done:
            self.main_controller.view.scrim_off()
            return

        self.pops.extend(
            self.check_for_empty_fields(fields={s.id: s.text for s in self.model.single},
                                        widget_list=self.model.single))
        self.pops.extend(self.check_for_empty_fields(fields={m.id: m.text for m in self.model.multi},
                                                     widget_list=self.model.multi))
        self.pops.extend(self.check_for_empty_fields(fields={r.id: f"Risk: {r.id}"
                                                             for r in self.model.risk},
                                                     widget_list=self.model.risk))

        if self.model.signature:
            for s in self.model.signature:
                if not s.filled:
                    self.pops.append(s.text)
        if self.pops:
            self.main_controller.view.scrim_off()
            self.view.open_error_popup()
            return
        if all(x not in self.form for x in ['Add Site', 'Add Equipment']):
            self.main_controller.view.scrim_off()
            self.view.open_final_signature_popup()
            return
        self.fill_form(signature=None)

    @staticmethod
    def check_for_empty_fields(fields, widget_list):
        empty_fields = [s.id for s in widget_list if s.mandatory and not s.filled]
        return [v for k, v in fields.items() if k in empty_fields]

    def fill_signatures(self, signature, name=None, signature_field=False):
        if not signature_field or not name:
            return
        self.view.get_tree()
        sign_type = 'Sign' if 'Sign' in signature else 'Initial'
        sign_key = 'signatures' if sign_type == 'Sign' else 'initials'
        if sign_key in self.model.form_view_fields:
            self.model.form_view_fields[sign_key].update({f"{name}": f"{signature}"})
        else:
            self.model.form_view_fields[sign_key] = {f"{name}": f"{signature}"}
        for s in self.model.signature:
            if s.person in name and sign_type in s.sign_type:
                s.select()

    def fill_form(self, signature):
        self.main_controller.view.scrim_on()
        if self.view.type == 'forms':
            self.model.process_form(signature, separator=self.separator, form=self.form, demo_mode=self.demo_mode)
        else:
            if self.demo_mode:
                self.main_controller.demo_mode_prompt()
                self.main_controller.view.scrim_off()
                return
            self.model.process_db_request(form_type=self.view.type)
        self.main_controller.view.scrim_off()
        self.remove_widgets()

    def remove_widgets(self, *args):
        self.close_speed_dial()
        self.view.get_tree()
        fields = self.model.single + self.model.multi + self.model.checkbox + self.model.signature + \
                 self.model.labels + self.model.risk
        for f in fields:
            self.view.ids.formview.remove_widget(f)
        with contextlib.suppress(WidgetException):
            self.view.add_save_button()
        self.view.get_tree()
        if self.model.current_site:
            self.switch_to_site_view(self.model.current_site)
        else:
            self.main_controller.main_screen_controller.change_feed('today', deletable=True)
            self.main_controller.change_screen('main_screen')

    def switch_to_site_view(self, site_id):
        self.main_controller.site_view_controller.switch_to_site_view(site_id)
