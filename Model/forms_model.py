import contextlib
from os import remove, listdir

from kivy.storage.jsonstore import JsonStore
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar

from Forms.safety_talk import SafetyTalk
from Forms.equipment_checklist import EquipmentChecklist
from Forms.flha import FLHA
from api_requests import secure_request, download, upload

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

    def upload_file(self, file_name):
        upload(path=self.main_model.get_directory(file_name),
               local_path=self.main_model.get_directory(file_name),
               id_token=self.main_model.id_token,
               url=self.main_model.secure_api_url, access_token=self.main_model.access_token)
        return secure_request(id_token=self.main_model.id_token, url=self.main_model.secure_api_url,
                              data={'upload': 'today.json', 'database': 'none', 'function_name': 'sql_create',
                                    'AccessToken': self.main_model.access_token})

    def get_location(self, form_type):
        if form_type == 'forms' and 'location' in self.main_model.form_view_fields and self.main_model.form_view_fields[
            'location']:
            return self.main_model.form_view_fields['location']
        elif form_type == 'equipment':
            return self.main_model.form_view_fields['site']
        elif form_type == 'site':
            return f"{self.main_model.form_view_fields['customer']} - {self.main_model.form_view_fields['city']}"
        else:
            return None

    def download_form(self, file_name):
        if file_name in listdir(self.main_model.get_directory('database/forms')):
            return
        dl_list = {f'database/{self.main_model.current_site}/forms/{file_name}': f'database/forms/{file_name}'}
        download(id_token=self.main_model.id_token, access_token=self.main_model.access_token,
                 url=self.main_model.secure_api_url, dl_list=dl_list)

    def update_completed_forms(self, db_id: str, new_entry: dict, column: str = None):
        rest = self.main_model.completed_forms[db_id]
        rest.update(new_entry)
        self.main_model.completed_forms[db_id] = rest
        if column:
            data = {'database': 'completed_forms', 'AccessToken': self.main_model.access_token,
                    'cols': new_entry}
            secure_request(id_token=self.main_model.id_token, data=data)

    def update_forms(self, db_id: str, new_entry: dict):
        rest = self.main_model.forms[db_id]
        rest.update(new_entry)
        self.main_model.forms[db_id] = rest

    def update_todays_forms(self, db_id: str, new_entry: dict, column: str = None):
        rest = self.main_model.today['forms']
        rest.update(new_entry)
        self.main_model.today['forms'] = rest
        if column:
            data = {'database': 'today', 'cols': new_entry, 'AccessToken': self.main_model.access_token}
            secure_request(id_token=self.main_model.id_token, data=data)

    def delete_todays_form(self, database: 'JsonStore', button: 'RVButton', id_token: str, demo_mode: bool = False):
        entry = button if isinstance(button, str) else button.id
        total = database['forms']
        if entry in total:
            total.pop(entry)
            database['forms'] = total
        if demo_mode:
            return
        return self.upload_file(file_name="database/today.json")

    def delete_signatures(self, signature_type: str, selections: list):
        if signature_type in self.main_model.form_view_fields:
            for s in list(self.main_model.form_view_fields[signature_type]):
                if s not in selections:
                    remove(self.main_model.get_directory(
                        f"database/{self.main_model.form_view_fields[signature_type][s]}"))
                    self.main_model.form_view_fields[signature_type].pop(s)

    def add_form_option(self, popup: Union['TextFieldPopup', 'MultiSelectPopup']):
        text_field, widgets = self.get_entry_text_and_widgets(popup)
        options, params = self.compile_entry_to_change(popup, text_field)
        self.update_forms(db_id=popup.db[0], new_entry=params)
        popup.content_cls.add_list_item(text_field)
        response = self.upload_file(file_name="database/forms.json")
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
            fields, widgets = self.get_single_widgets(popup, selection)
        response = self.upload_file(file_name='database/forms.json')
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
        if selection in fields:
            fields.remove(selection)
        if selection in popup.selections:
            popup.selections.remove(selection)
        widgets = self.main_model.multi
        return fields, widgets

    def get_single_widgets(self, popup, selection):
        widgets = self.main_model.single
        fields = [x['text'] for x in popup.content_cls.pre_select]
        with contextlib.suppress(ValueError):
            # This won't work with the delete icons
            fields.remove(selection)
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
                self.main_model.form_view_fields['separation'] = self.main_model.form_view_fields[minimum]
                return True, None
        return True, None

    def check_for_duplicates(self, form_type, separator):
        if form_type != 'forms':
            return False
        entries_to_check = {'name': 'name', 'site_id': 'site_id', 'date': 'date',
                            'separation': separator}
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
        response = self.upload_file(file_name="database/today.json")
        self.main_model.iterate_register(response)

    def get_index(self):
        if 'index' in self.main_model.form_view_fields:
            return self.main_model.form_view_fields['index']
        elif list(self.main_model.today['forms']):
            return str(max(int(x) for x in self.main_model.today['forms']) + 1)
        else:
            return str(0)

    def update_equipment_entry(self):
        machine = self.main_model.form_view_fields['type']
        unit_num = self.main_model.form_view_fields['unit_num']
        mileage = self.main_model.form_view_fields['mileage']
        for e in self.main_model.equipment:
            if unit_num == self.main_model.equipment[e]['unit_num'] \
                    and machine == self.main_model.equipment[e]['type']:
                equipment_info = self.main_model.equipment[e]
                equipment_info['mileage'] = mileage

                self.main_model.update_equipment(new_entry=equipment_info, db_id=e)

    def process_form(self, signature, form, separator):
        form_class = self.forms[form]
        form_instance = form_class()
        form_instance.separator = self.main_model.form_view_fields[separator]
        form_instance.fields = self.main_model.form_view_fields
        form_instance.forms_path = self.main_model.get_directory("database/forms")
        form_instance.signature_path = self.main_model.get_directory(f"database/forms/{signature}")
        form_instance.make_file()
        form_instance.print()
        try:
            if not self.main_model.demo_mode:
                upload(path=f"database/{self.main_model.current_site_id}/forms/{form_instance.file_name}.pdf",
                       local_path=self.main_model.get_directory(f"database/forms/{form_instance.file_name}.pdf"),
                       id_token=self.main_model.id_token,
                       url=self.main_model.secure_api_url, access_token=self.main_model.access_token)
                self.remove_form_from_db(file_name=form_instance.file_name, form=form, separator=separator)
            else:
                file_name = self.main_model.get_directory(f"database/forms/{form_instance.file_name}.pdf")
                self.main_model.phone.open_pdf(file_name)
        except Exception as e:
            self.save_incomplete_form(separator, 'this input is not used')
            MDSnackbar(
                MDLabel(
                    text='There was a problem uploading the form'
                )
            ).open()
        finally:
            if not self.main_model.demo_mode:
                form_instance.remove_file()
            else:
                self.remove_files(form_instance)
                self.remove_from_device(demo_mode=self.main_model.demo_mode)

    def remove_files(self, form_instance):
        to_be_deleted = [
            self.main_model.get_directory(f"database/forms/{form_instance.file_name}.pdf"),
            form_instance.signature_path,
        ]
        to_be_deleted.extend(
            self.main_model.get_directory(f"database/forms/{form_instance.fields['signatures'].get(signature, '')}")
            for signature in form_instance.fields.get('signatures', '')
        )
        settings = dict(self.main_model.settings)
        settings['To Be Deleted'] = to_be_deleted
        self.main_model.save_db_file('settings', settings)

    def get_equipment_id(self):
        if 'unit_num' not in self.main_model.form_view_fields:
            return '0'
        for e in self.main_model.equipment:
            if (
                    self.main_model.equipment[e]['unit_num']
                    == self.main_model.form_view_fields['unit_num']
                    and self.main_model.equipment[e]['type']
                    == self.main_model.form_view_fields['type']
            ):
                return e

    def remove_from_device(self, demo_mode=False):
        for x in [x for x in ['signatures', 'initials'] if x in self.main_model.form_view_fields]:
            self.main_model.form_view_fields.pop(x)
        if 'index' in self.main_model.form_view_fields:
            self.delete_todays_form(self.main_model.today, self.main_model.form_view_fields['index'],
                                    self.main_model.id_token, demo_mode=demo_mode)
        self.main_model.current_site_id = ''

    def remove_form_from_db(self, file_name, form, separator):
        fields = {"name": form, "site_id": self.main_model.current_site_id,
                  'location': self.main_model.form_view_fields['location'],
                  'date': self.main_model.form_view_fields['date'],
                  'separation': self.main_model.form_view_fields[separator],
                  'file_name': f"{file_name}.pdf",
                  'equipment': self.get_equipment_id()}
        data = {"database": "forms",
                "cols": fields,
                'function_name': 'sql_create', 'AccessToken': self.main_model.access_token
                }
        response = secure_request(data=data, id_token=self.main_model.id_token, url=self.main_model.secure_api_url)
        self.record_completed_form(response=response, fields=fields)

    def record_completed_form(self, response, fields):
        self.main_model.iterate_register(response)
        new_id = response['body']
        sites = self.main_model.sites
        site_id = self.main_model.current_site_id
        site = sites[site_id]
        site['forms'].append(str(new_id))
        self.main_model.completed_forms[new_id] = fields
        self.main_model.update_sites(new_entry=site, db_id=site_id)
        self.remove_from_device()

    def process_db_request(self, form_type):
        if 'equipment' in form_type:
            updated_db, data = self.add_equipment()
        else:
            updated_db, data = self.add_site()
        self.add_to_db(updated_db, data)

    def add_equipment(self):
        self.get_site_id(self.main_model.form_view_fields['site'])
        self.main_model.form_view_fields['site'] = self.main_model.current_site_id
        data = {'cols': {"type": self.main_model.form_view_fields['type'], "site_id": self.main_model.current_site_id,
                         "unit_num": self.main_model.form_view_fields['unit_num'],
                         "mileage": self.main_model.form_view_fields['mileage'],
                         "last_service": self.main_model.form_view_fields['last_service'],
                         "last_inspection": self.main_model.form_view_fields['last_inspection'],
                         "owned": self.main_model.form_view_fields['owned']},
                "database": 'equipment'}
        updated_db = self.main_model.equipment
        site_entry = self.main_model.sites[self.main_model.current_site_id]
        site_entry['equipment'].append(self.main_model.current_site_id)
        self.main_model.update_sites(new_entry=site_entry, db_id=self.main_model.current_site_id)
        return updated_db, data

    def add_site(self):
        data = {'cols': {"customer": self.main_model.form_view_fields['customer'],
                         "address": self.main_model.form_view_fields['address'],
                         "city": self.main_model.form_view_fields['city'],
                         "complete": False,
                         "banner_image": '',
                         "start_date": self.main_model.form_view_fields['start_date']},
                "database": 'sites'}
        updated_db = self.main_model.sites
        self.main_model.form_view_fields.pop('name', 'default')
        return updated_db, data

    def add_to_db(self, updated_db, data):
        data.update({'function_name': 'sql_create', 'AccessToken': self.main_model.access_token})
        response = secure_request(id_token=self.main_model.id_token, data=data, url=self.main_model.secure_api_url)
        if isinstance(response['body'], str):
            return
        new_id = response['body']
        updated_db[str(new_id)] = self.main_model.form_view_fields
        self.main_model.iterate_register(response)

    def add_hazard(self, hazard_type, hazard):
        form_entry = self.main_model.forms[self.main_model.form_view_fields['name']]
        if hazard_type == 'Task-Specific':
            work_to_be_done = self.main_model.form_view_fields['work_to_be_done']
            task = self.main_model.form_view_fields['task']
            form_entry[work_to_be_done][task].append(hazard)
        else:
            form_entry['hazards'].append(hazard)
        self.update_forms(db_id=self.main_model.form_view_fields['name'], new_entry=form_entry)

    def delete_hazard(self, hazard):
        form_entry = self.main_model.forms[self.main_model.form_view_fields['name']]
        if hazard in form_entry['hazards']:
            form_entry['hazards'].remove(hazard)
        else:
            work_to_be_done = self.main_model.form_view_fields['work_to_be_done']
            task = self.main_model.form_view_fields['task']
            if hazard in form_entry[work_to_be_done][task]:
                form_entry[work_to_be_done][task].remove(hazard)
        self.update_forms(db_id=self.main_model.form_view_fields['name'], new_entry=form_entry)
