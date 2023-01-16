from os import remove

from kivy.storage.jsonstore import JsonStore

from Forms.safety_talk import SafetyTalk
from Forms.equipment_checklist import EquipmentChecklist
from Forms.flha import FLHA
from api_requests import Requests

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Views.Buttons.rv_button.rv_button import RVButton
    from Views.Popups.text_field_popup.text_field_popup import TextFieldPopup
    from Views.Popups.multi_select_popup.multi_select_popup import MultiSelectPopup


class FormsModel:
    def __init__(self, main_model: 'MainModel'):
        self.main_model = main_model
        forms = [x for x in self.main_model.forms if x not in ['Add Site', 'Add Equipment']]
        form_classes = [SafetyTalk, EquipmentChecklist, FLHA]
        self.forms = {x[0]: x[1] for x in zip(forms, form_classes)}

    def get_site_id(self, location):
        entry = location.split(' - ')
        customer = entry[0]
        city = entry[1]
        site_id = next((site_id for site_id in self.main_model.sites if
                        customer in self.main_model.sites[site_id]['customer']
                        and city in self.main_model.sites[site_id]['city']), None)
        self.main_model.current_site_id = site_id

    def get_location(self, form_type):
        if form_type == 'forms' and 'location' in self.main_model.form_view_fields and self.main_model.form_view_fields['location']:
            return self.main_model.form_view_fields['location']
        elif form_type == 'equipment':
            return self.main_model.form_view_fields['site']
        elif form_type == 'site':
            return f"{self.main_model.form_view_fields['customer']} - {self.main_model.form_view_fields['city']}"
        else:
            return None

    def download_form(self, button_id):
        r = Requests.secure_request(name='getCredentials', data={"AccessToken": self.main_model.access_token},
                                    id_token=self.main_model.id_token)
        Requests.download(credentials=r, folder='database/forms', title=button_id)
        if self.main_model.phone:
            self.main_model.phone.open_pdf(database='forms', file_name=button_id)

    def update_completed_forms(self, db_id: str, new_entry: dict, column: str = None):
        rest = self.main_model.completed_forms[db_id]
        rest.update(new_entry)
        self.main_model.completed_forms[db_id] = rest
        if column:
            data = {'database': 'completed_forms', 'column': column}
            Requests.secure_request('sqlUpdate', id_token=self.main_model.id_token, data=data)

    def update_forms(self, db_id: str, new_entry: dict):
        rest = self.main_model.forms[db_id]
        rest.update(new_entry)
        self.main_model.forms[db_id] = rest

    def update_todays_forms(self, db_id: str, new_entry: dict, column: str = None):
        rest = self.main_model.today['forms']
        rest.update(new_entry)
        self.main_model.today['forms'] = rest
        if column:
            data = {'database': 'today', 'column': column}
            Requests.secure_request('sqlUpdate', id_token=self.main_model.id_token, data=data)

    def delete_todays_form(self, database: 'JsonStore', button: 'RVButton', id_token: str):
        entry = button if isinstance(button, str) else button.id
        total = database['forms']
        if entry in total:
            total.pop(entry)
            database['forms'] = total
        return Requests.upload(path="database/today.json", id_token=id_token)

    def delete_signatures(self, signature_type: str, selections: list):
        if signature_type in self.main_model.form_view_fields:
            for s in list(self.main_model.form_view_fields[signature_type]):
                if s not in selections:
                    remove(f"database/{self.main_model.form_view_fields[signature_type][s]}")
                    self.main_model.form_view_fields[signature_type].pop(s)

    def add_form_option(self, popup: Union['TextFieldPopup', 'MultiSelectPopup']):
        text_field, widgets = self.get_entry_text_and_widgets(popup)
        options, params = self.compile_entry_to_change(popup, text_field)
        self.update_forms(db_id=popup.db[0], new_entry=params)
        popup.content_cls.add_list_item(text_field)
        response = Requests.upload(path='database/forms/forms.json', id_token=self.main_model.id_token)
        self.main_model.iterate_register(response)
        return options, widgets

    def get_entry_text_and_widgets(self, popup):
        if 'Multi' in str(type(popup)):
            text_field = popup.content_cls.ids.add_new.text
            widgets = self.main_model.multi
        else:
            text_field = popup.content_cls.ids.dropdown.text
            widgets = self.main_model.single
        return text_field, widgets

    def compile_entry_to_change(self, popup, text_field):
        if 'task' in popup.id:
            work, options = self.add_task(popup=popup)
            return options, {work: options}
        else:
            options = self.main_model.forms[popup.db[0]][popup.db[1]]
            options.append(text_field)
            return options, {popup.db[1]: options}

    def add_task(self, popup):
        options = {}
        w2b_done = next((s for s in self.main_model.single if 'work_to_be_done' in s.id and s.ids.pre_select.text),
                        None)
        work = w2b_done.ids.pre_select.text
        options |= self.main_model.forms[popup.db[0]][work]
        options[popup.ids.add_new.text] = []
        return work, options

    def delete_form_option(self, params: list):
        popup = params[0]
        selection = params[1]
        form = self.main_model.forms[popup.db[0]]
        self.remove_selection_from_db(form, popup, selection)
        self.main_model.forms[popup.db[0]] = form
        fields = None
        widgets = None
        if 'Multi' in str(type(popup)):
            fields, widgets = self.get_multi_widgets(popup, selection)
        if 'TextField' in str(type(popup)):
            fields, widgets = self.get_single_widgets(popup)
        response = Requests.upload(path='database/forms/forms.json', id_token=self.main_model.id_token)
        self.main_model.iterate_register(response)
        return fields, widgets

    @staticmethod
    def remove_selection_from_db(form, popup, selection):
        sub_db = form[popup.db[1]]
        if isinstance(sub_db, list):
            sub_db.remove(selection)
        else:
            sub_db.pop(selection, None)

    def get_multi_widgets(self, popup, selection):
        widget_to_delete = next(
            (x for x in popup.content_cls.ids.selection_list.children if x.instance_item.text == selection), None)
        widget_to_delete.do_unselected_item()
        fields = popup.content_cls.fields
        fields.remove(selection)
        if selection in popup.selections:
            popup.selections.remove(selection)
        widgets = self.main_model.multi
        return fields, widgets

    def get_single_widgets(self, popup):
        widgets = self.main_model.single
        fields = [x['text'] for x in popup.content_cls.pre_select]
        fields.remove(popup.content_cls.ids.dropdown.text)
        return fields, widgets

    @staticmethod
    def update_field(fields: dict, field_dict: dict):
        for key, value in field_dict.items():
            fields[key] = value

    def save_form_fields(self, submit, separator, form_type):
        done, minimum = self.check_for_minimum_required_fields(form_type)
        if minimum:
            return done, minimum
        if self.check_for_duplicates(form_type, separator):
            return False, 'Duplicate Form'
        if 'mileage' in self.main_model.form_view_fields:
            self.update_equipment_entry()
        if not submit:
            self.save_incomplete_form(separator, form_type)
        return True, None

    def check_for_minimum_required_fields(self, form_type):
        location = self.get_location(form_type)
        if location and form_type != 'site':
            self.get_site_id(location)
            self.main_model.form_view_fields['site_id'] = self.main_model.current_site_id
        done, minimum = self.check_for_required_distinguishing_field()
        if not done:
            return done, minimum
        return (True, None) if location else (False, 'location')

    def check_for_required_distinguishing_field(self):
        widgets = self.main_model.single + self.main_model.multi
        for w in widgets:
            if w.divide:
                minimum = w.id
                if not self.main_model.form_view_fields[minimum]:
                    return False, minimum
                self.main_model.form_view_fields['separator'] = self.main_model.form_view_fields[minimum]
                return True, None

    def check_for_duplicates(self, form_type, separator):
        if form_type != 'forms':
            return False
        entries_to_check = {'name': 'name', 'site': 'site_id', 'date': 'date',
                            'separator': separator}
        for x in self.main_model.completed_forms:
            check = [True for y, z in entries_to_check.items()
                     if self.main_model.completed_forms[x][y] == self.main_model.form_view_fields[z]]
            if len(check) == 4:
                return True
        return False

    def save_incomplete_form(self, separator, form_type):
        self.main_model.form_view_fields['row_text'] = f"{self.main_model.form_view_fields['name']} " \
                                                       f"{self.main_model.form_view_fields['date']}  " \
                                                       f"{self.main_model.form_view_fields['location']} : " \
                                                       f"{self.main_model.form_view_fields[separator]} "
        index = self.get_index()
        self.main_model.form_view_fields['index'] = index
        new_pair = {index: self.main_model.form_view_fields}
        self.update_todays_forms(new_entry=new_pair, db_id=form_type)
        response = Requests.upload(path="database/today.json", id_token=self.main_model.id_token)
        self.main_model.iterate_register(response)

    def get_index(self):
        if 'index' in self.main_model.form_view_fields:
            return self.main_model.form_view_fields['index']
        elif list(self.main_model.today['forms']):
            return str(max(int(x) for x in self.main_model.today['forms']) + 1)
        else:
            return str(0)

    def update_equipment_entry(self):
        machine = self.main_model.form_view_fields['machine']
        unit_num = self.main_model.form_view_fields['unit_num']
        mileage = self.main_model.form_view_fields['mileage']
        for e in self.main_model.equipment:
            if unit_num == self.main_model.equipment[e]['unit_num'] \
                    and machine == self.main_model.equipment[e]['type']:
                equipment_info = self.main_model.equipment[e]
                equipment_info['mileage'] = mileage
                self.main_model.update_equipment(new_entry=equipment_info, db_id=e, column='equipment')

    def process_form(self, signature, form, separator):
        form_class = self.forms[form]
        form_instance = form_class()
        form_instance.separator = self.main_model.form_view_fields[separator]
        form_instance.fields = self.main_model.form_view_fields
        form_instance.signature_path = f"database/{signature}"
        form_instance.make_file()
        form_instance.print()
        self.remove_form_from_db(file_name=form_instance.file_name, form=form, separator=separator)
        Requests.upload(path=f"{form_instance.file_name}.pdf", id_token=self.main_model.id_token)
        form_instance.remove_file()

    def remove_form_from_db(self, file_name, form, separator):
        for x in [x for x in ['signatures', 'initials'] if x in self.main_model.form_view_fields]:
            self.main_model.form_view_fields.pop(x)
        fields = {"name": form, "site": self.main_model.current_site_id,
                  'location': self.main_model.form_view_fields['location'],
                  'date': self.main_model.form_view_fields['date'],
                  'separator': self.main_model.form_view_fields[separator],
                  'file_name': f"{file_name}.pdf"}
        data = {"database": "completed_forms"}
        response = Requests.secure_request(name='sqlCreate', data=data | fields, id_token=self.main_model.id_token)
        self.record_completed_form(response=response, fields=fields)
        if 'index' in self.main_model.form_view_fields:
            self.delete_todays_form(self.main_model.today, self.main_model.form_view_fields['index'],
                                    self.main_model.id_token)

    def record_completed_form(self, response, fields):
        self.main_model.iterate_register(response)
        new_id = response['body']
        sites = self.main_model.sites
        site_id = self.main_model.current_site_id
        site = sites[site_id]
        site['forms'].append(str(new_id))
        self.main_model.completed_forms[new_id] = fields
        self.main_model.update_sites(new_entry=site, db_id=site_id, column='forms')
        self.main_model.current_site_id = ''

    def process_db_request(self, form_type):
        if 'equipment' in form_type:
            updated_db, data = self.add_equipment()
        else:
            updated_db, data = self.add_site()
        self.add_to_db(updated_db, data)

    def add_equipment(self):
        self.get_site_id(self.main_model.form_view_fields['site'])
        self.main_model.form_view_fields['site'] = self.main_model.current_site_id
        data = {"name": self.main_model.form_view_fields['name'], "site": self.main_model.current_site_id,
                "database": 'equipment'}
        updated_db = self.main_model.equipment
        site_entry = self.main_model.sites[self.main_model.current_site_id]
        site_entry['equipment'].append(self.main_model.current_site_id)
        self.main_model.update_sites(new_entry=site_entry, db_id=self.main_model.current_site_id, column='equipment')
        return updated_db, data

    def add_site(self):
        data = {"customer": self.main_model.form_view_fields['customer'],
                "address": self.main_model.form_view_fields['address'],
                "city": self.main_model.form_view_fields['city'], "database": 'sites'}
        updated_db = self.main_model.sites
        self.main_model.form_view_fields.pop('name', 'default')
        return updated_db, data

    def add_to_db(self, updated_db, data):
        response = Requests.secure_request(name='sqlCreate', id_token=self.main_model.id_token, data=data)
        new_id = response['body']
        updated_db[str(new_id)] = self.main_model.form_view_fields
        self.main_model.iterate_register(response)
