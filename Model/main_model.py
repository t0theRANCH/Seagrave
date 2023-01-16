import json
from os import remove

from kivy._event import EventDispatcher
from kivy.properties import ObjectProperty, StringProperty, DictProperty
from kivy.storage.jsonstore import JsonStore

from api_requests import Requests
from Model.forms_model import FormsModel
from Model.images_model import ImagesModel
from Model.sites_model import SitesModel
from Model.equipment_model import EquipmentModel
from Model.login_model import LoginModel

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from Mobile_OS.android_os import Android
    from Views.Buttons.rv_button.rv_button import RVButton
    from kivy.storage.jsonstore import JsonStore
    from Views.Popups.text_field_popup.text_field_popup import TextFieldPopup
    from Views.Popups.multi_select_popup.multi_select_popup import MultiSelectPopup


class MainModel(EventDispatcher):
    phone: 'Android' = ObjectProperty()
    access_token: str = StringProperty()
    id_token: str = StringProperty()
    refresh_token: str = StringProperty()
    device_key: str = StringProperty()
    form_view_fields: dict = DictProperty({})
    current_site_id: str = StringProperty()
    current_site: str = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.forms_model = FormsModel(main_model=self)
        self.images_model = ImagesModel(main_model=self)
        self.sites_model = SitesModel(main_model=self)
        self.equipment_model = EquipmentModel(main_model=self)
        self.login_model = LoginModel(main_model=self)
        self.single, self.multi, self.checkbox, self.risk, self.signature, self.labels, self.pops = [], [], [], [], [], [], []

    def is_undeletable(self, title: str, text: str):
        if title in self.undeletable:
            return text in self.undeletable[title]

    def iterate_register(self, response: dict):
        with open('database/register.json', 'r') as f:
            data = json.load(f)
            data['iteration'] = response['iteration']
        remove('database/register.json')
        self.save_db_file('register', data)

    @staticmethod
    def save_db_file(database: str, data_dict: dict):
        with open(f"database/{database}.json", 'w') as fp:
            json.dump(data_dict, fp)

    def select_delete_item(self, button: 'RVButton'):
        dbs = ['sites', 'equipment', 'forms', 'today']
        db_files = [self.sites, self.equipment, self.forms, self.today]
        funcs = [self.delete_item, self.delete_item, self.delete_item, self.delete_todays_form]
        corr_db_funcs = [self.remove_site_from_equipment_db, self.remove_equipment_from_site_db,
                         self.remove_form_from_site_db, None]
        if corr_edit := corr_db_funcs[dbs.index(button.feed)]:
            corr_edit(index=button.id)
        func = funcs[dbs.index(button.feed)]
        response = func(database=db_files[dbs.index(button.feed)], button=button, id_token=self.id_token)
        self.iterate_register(response)
        button.parent.remove_widget(button)

    @staticmethod
    def delete_item(database: 'JsonStore', button: 'RVButton', id_token: str):
        data = {"database": button.feed, "id": button.id}
        database.delete(button.id)
        return Requests.secure_request(name='sqlDelete', data=data, id_token=id_token)

    def remove_site_from_equipment_db(self, index: str):
        for e in self.equipment:
            if index == self.equipment[e]['site']:
                db = self.equipment[e]
                db['site'] = ''
                self.update_equipment(db_id=e, new_entry=db, column='site')

    def remove_equipment_from_site_db(self, index: str):
        for s in self.sites:
            if index in self.sites[s]['equipment']:
                db = self.sites[s]
                db['equipment'].remove(index)
                self.update_sites(db_id=s, new_entry=db, column='equipment')

    def remove_form_from_site_db(self, index: str):
        for s in self.sites:
            if index in self.sites[s]['forms']:
                db = self.sites[s]
                db['forms'].remove(index)
                self.update_sites(db_id=s, new_entry=db, column='forms')

    # Login

    def check_for_user_info(self):
        return self.login_model.check_for_user_info()

    def save_password(self, user: str, password: str):
        self.login_model.save_password(user, password)

    def dont_save_password(self, user: str):
        self.login_model.dont_save_password(user)

    def db_handler(self):
        self.login_model.db_handler()

    # Sites
    
    def update_sites(self, db_id: str, new_entry: dict, column: str = None):
        self.sites_model.update_sites(db_id, new_entry, column)
        
    def update_time_clock(self, db_id: str, new_entry: dict, column: str = None):
        self.sites_model.update_time_clock(db_id, new_entry)
        
    def delete_site(self, action):
        self.sites_model.delete_site(action)

    def punch_clock(self, current_datetime, current_day, action):
        self.sites_model.punch_clock(current_datetime, current_day, action)

    # Equipment

    def update_equipment(self, db_id: str, new_entry: dict, column: str = None):
        self.equipment_model.update_equipment(db_id, new_entry, column)

    def get_equipment_data(self):
        return {e: self.equipment[e] for e in self.equipment if self.equipment[e]['site'] != self.current_site}

    def get_single_equipment_data(self, equipment_id):
        return self.equipment_model.get_single_equipment_data(equipment_id)

    def edit_equipment_data(self, equipment_id, site_name, new_data):
        self.equipment_model.edit_equipment_data(equipment_id, site_name, new_data)

    # Forms

    def download_form(self, button_id):
        self.forms_model.download_form(button_id)

    def update_completed_forms(self, db_id: str, new_entry: dict, column: str = None):
        self.forms_model.update_completed_forms(db_id, new_entry, column)

    def update_forms(self, db_id: str, new_entry: dict):
        self.forms_model.update_forms(db_id, new_entry)

    def update_todays_forms(self, db_id: str, new_entry: dict, column: str = None):
        self.forms_model.update_todays_forms(db_id, new_entry, column)

    def delete_todays_form(self, database: 'JsonStore', button: 'RVButton', id_token: str):
        return self.forms_model.delete_todays_form(database, button, id_token)

    def update_field(self, fields: dict, field_dict: dict):
        self.forms_model.update_field(fields, field_dict)

    def delete_signatures(self, signature_type: str, selections: list):
        self.forms_model.delete_signatures(signature_type, selections)

    def add_form_option(self, param: list):
        return self.forms_model.add_form_option(param[0])

    def delete_form_option(self, params: list):
        return self.forms_model.delete_form_option(params)

    def save_form_fields(self, submit, separator, form_type):
        return self.forms_model.save_form_fields(submit, separator, form_type)

    def process_form(self, signature, form, separator):
        self.forms_model.process_form(signature, form, separator)

    def process_db_request(self, form_type):
        self.forms_model.process_db_request(form_type)

    # Images

    def update_pictures(self, db_id: str, new_entry: dict, column: str = None):
        self.images_model.update_pictures(db_id, new_entry, column)
        
    def update_blueprints(self, db_id: str, new_entry: dict, column: str = None):
        self.images_model.update_blueprints(db_id, new_entry, column)

    def add_note_to_picture(self, picture_id, note):
        self.images_model.add_note_to_picture(picture_id, note)

    def get_banner_image(self):
        return self.images_model.get_banner_image()

    def set_banner_image(self, value):
        self.images_model.set_banner_image(value)
    
    def select_image_to_upload(self, path, file_type, blueprint_type=None):
        return self.images_model.select_image_to_upload(path, file_type, blueprint_type)

    # Properties

    @property
    def site_rows(self):
        return [{"text": f"{self.sites[s]['customer']} - {self.sites[s]['city']}", "id": str(s),
                       "type": 'site'} for s in self.sites]

    @property
    def equipment_rows(self):
        return [{"text": str(self.equipment[e]['type']), "id": str(e), "type": 'equipment'}
                           for e in self.equipment]

    @property
    def form_rows(self):
        return [{"text": str(self.forms[f]['name']), "id": str(f).lower().replace(' ', '_'), "type": 'forms'}
                      for f in self.forms if str(self.forms[f]['name']) not in ["Add Site", "Add Equipment"]]

    @property
    def today_rows(self):
        return [{"text": self.today['forms'][f]['row_text'], "id": str(f), "type": 'forms'}
                       for f in self.today['forms']]

    @property
    def blueprints(self):
        return JsonStore('database/blueprints/blueprints.json')

    @property
    def completed_forms(self):
        return JsonStore('database/forms/completed_forms.json')

    @property
    def equipment(self):
        return JsonStore('database/equipment.json')

    @property
    def forms(self):
        return JsonStore('database/forms/forms.json')

    @property
    def pictures(self):
        return JsonStore('database/pictures/pictures.json')
    
    @property
    def register(self):
        return JsonStore('database/register.json')

    @property
    def sites(self):
        return JsonStore('database/sites.json')

    @property
    def today(self):
        return JsonStore('database/today.json')

    @property
    def undeletable(self):
        return JsonStore('database/undeletable.json')

    @property
    def user(self):
        return JsonStore('database/user.json')

    @property
    def time_clock(self):
        return JsonStore('database/time_clock.json')
    