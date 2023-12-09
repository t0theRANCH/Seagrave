import json
from datetime import datetime
import time
from os import remove, environ, makedirs, listdir
from os.path import join, exists, dirname, getsize
import shutil

from kivy.event import EventDispatcher
from kivy.utils import platform
from kivy.properties import ObjectProperty, StringProperty, DictProperty, BooleanProperty
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar

from api_requests import secure_request, open_request
from Model.forms_model import FormsModel
from Model.images_model import ImagesModel
from Model.sites_model import SitesModel
from Model.equipment_model import EquipmentModel
from Model.login_model import LoginModel

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from Mobile_OS.android_os import Android
    from Mobile_OS.ios import IOS
    from Mobile_OS.pc import PC
    from Views.Buttons.rv_button.rv_button import RVButton
    from kivy.storage.jsonstore import JsonStore
    from Views.Popups.text_field_popup.text_field_popup import TextFieldPopup
    from Views.Popups.multi_select_popup.multi_select_popup import MultiSelectPopup


class MainModel(EventDispatcher):
    phone: Union['Android', 'IOS', 'PC'] = ObjectProperty()
    form_view_fields: dict = DictProperty({})
    time_card: dict = DictProperty({})
    current_site_id: str = StringProperty()
    current_site: str = StringProperty()
    primary_color: tuple = ()
    demo_mode = BooleanProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.writeable_folder = ''
        self.demo_mode = self.settings['Demo Mode']
        self.database_folder = 'demo_database' if self.demo_mode else 'database'
        self.get_ios_writeable_folder()
        self.forms_model = FormsModel(main_model=self)
        self.images_model = ImagesModel(main_model=self)
        self.sites_model = SitesModel(main_model=self)
        self.equipment_model = EquipmentModel(main_model=self)
        self.login_model = LoginModel(main_model=self)
        self.single, self.multi, self.checkbox, self.risk, self.signature, self.labels, self.pops = [], [], [], [], [], [], []

    def on_demo_mode(self, instance, value):
        self.database_folder = 'demo_database' if value else join(self.writeable_folder, 'database')

    def get_ios_writeable_folder(self):
        if platform != 'ios':
            return
        self.writeable_folder = join(environ['HOME'], 'Documents')
        self.database_folder = 'demo_database' if self.demo_mode else join(self.writeable_folder, self.database_folder)
        self.check_writeable_folder()
        self.check_writeable_folder(folder='demo_database')

    def check_writeable_folder(self, folder='database'):
        makedirs(join(self.writeable_folder, folder), exist_ok=True)
        MAX_RETRIES = 5  # Define a maximum number of retries.
        RETRY_WAIT_TIME = 0.5  # Time in seconds to wait between retries.
        for file in listdir(folder):
            if file.endswith('.json'):
                source_path = join(folder, file)
                target_path = join(self.writeable_folder, folder, file)
                self.copy_file(file, source_path, target_path, MAX_RETRIES, RETRY_WAIT_TIME)
            else:
                makedirs(join(self.writeable_folder, folder, file), exist_ok=True)
                for sub_file in listdir(join(folder, file)):
                    source_sub_path = join(folder, file, sub_file)
                    target_sub_path = join(self.writeable_folder, folder, file, sub_file)
                    self.copy_file(sub_file, source_sub_path, target_sub_path, MAX_RETRIES, RETRY_WAIT_TIME)

    @staticmethod
    def copy_file(file, source_path, target_path, max_retries=5, retry_wait_time=0.5):
        if file.endswith('.json') and not exists(target_path):
            retry_count = 0
            while retry_count < max_retries:
                shutil.copy(source_path, target_path)
                if getsize(source_path) == getsize(target_path):
                    break  # Break the loop when file sizes match.
                time.sleep(retry_wait_time)  # Wait for a specified time before retrying.
                retry_count += 1

    def get_directory(self, directory: str):
        return join(self.writeable_folder, directory)

    @staticmethod
    def display_error_snackbar(message_text: str):
        MDSnackbar(
            MDLabel(
                text=message_text
            )
        ).open()

    def update_file_cache(self, db, new_entry):
        rest = self.file_cache[db]
        rest.update(new_entry)
        self.file_cache[db] = rest

    def update_settings(self, db_id: str, new_entry):
        rest = self.settings[db_id]
        rest.update(new_entry)
        self.settings[db_id] = rest

    def update_tutorial_settings(self, key, value):
        tutorial_settings = self.settings['Tutorial']
        tutorial_settings[key] = value
        self.update_settings('Tutorial', tutorial_settings)

    def is_undeletable(self, title: str, text: str):
        if title in self.undeletable:
            return text in self.undeletable[title]

    def iterate_register(self, response: dict):
        self.db_handler()
        register_file_path = self.get_directory('database/register.json')
        with open(register_file_path, 'r') as f:
            data = json.load(f)
            data['iteration'] = response['iteration']
        remove(register_file_path)
        self.save_db_file('register', data)

    def save_db_file(self, database: str, data_dict: dict):
        with open(self.get_directory(f"database/{database}.json"), 'w') as fp:
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

    def delete_item(self, database: 'JsonStore', button: 'RVButton', id_token: str):
        database.delete(button.id)
        data = {'AccessToken': self.access_token, 'Id': button.id, 'action': 'delete',
                'function_name': 'sql_delete', 'database': button.feed}
        return secure_request(data=data, id_token=id_token, url=self.secure_api_url)

    def remove_site_from_equipment_db(self, index: str):
        for e in self.equipment:
            if index == self.equipment[e]['site']:
                db = self.equipment[e]
                db['site'] = ''
                self.update_equipment(db_id=e, new_entry=db)

    def remove_pictures_from_site_db(self, index: str):
        for p in self.pictures:
            if index == self.pictures[p]['site_id']:
                db = self.pictures[p]
                db['site_id'] = ''
                self.update_pictures(db_id=p, new_entry=db, column='site_id')

    def remove_blueprints_from_site_db(self, index: str):
        for b in self.blueprints:
            if index == self.blueprints[b]['site_id']:
                db = self.blueprints[b]
                db['site_id'] = ''
                self.update_blueprints(db_id=b, new_entry=db, column='site_id')

    def remove_equipment_from_site_db(self, index: str):
        for s in self.sites:
            if index in self.sites[s]['equipment']:
                db = self.sites[s]
                db['equipment'].remove(index)
                self.update_sites(db_id=s, new_entry=db)

    def remove_form_from_site_db(self, index: str):
        for s in self.sites:
            if index in self.sites[s]['forms']:
                db = self.sites[s]
                db['forms'].remove(index)
                self.update_sites(db_id=s, new_entry=db)

    # Login

    def check_for_user_info(self):
        return self.login_model.check_for_user_info()

    def save_password(self, user: str, password: str):
        self.save_password_settings(True)
        self.login_model.save_password(user, password)

    def dont_save_password(self, user: str):
        self.save_password_settings(False)
        self.login_model.dont_save_password(user)

    def save_password_settings(self, value):
        settings = dict(self.settings)
        settings["Save Password"] = value
        self.save_db_file('settings', settings)

    def db_handler(self):
        self.login_model.db_handler()

    # Sites

    def update_sites(self, db_id: str, new_entry: dict, column: str = None):
        self.sites_model.update_sites(db_id, new_entry, column)

    def update_time_clock(self, new_entry: dict):
        self.sites_model.update_time_clock(new_entry)

    def delete_site(self, action):
        self.sites_model.delete_site(action)

    def punch_clock(self, current_datetime, current_day, action, user=None, sql_id=None):
        self.sites_model.punch_clock(current_datetime, current_day, action, user, sql_id)

    def get_hours(self, users=None):
        if not users:
            users = [self.user['given_name']]
        return self.sites_model.get_hours(users)

    # Equipment

    def update_equipment(self, db_id: str, new_entry: dict):
        self.equipment_model.update_equipment(db_id, new_entry)

    def get_equipment_data(self):
        return {e: self.equipment[e] for e in self.equipment if self.equipment[e]['site'] != self.current_site}

    def get_single_equipment_data(self, equipment_id):
        return self.equipment_model.get_single_equipment_data(equipment_id)

    def edit_equipment_data(self, equipment_id, site_name, new_data):
        self.equipment_model.edit_equipment_data(equipment_id, site_name, new_data)

    # Forms

    def download_form(self, button_id):
        self.forms_model.download_form(button_id)
        if button_id not in self.file_cache['forms']:
            form_entry = self.file_cache['forms']
            form_entry[str(button_id)] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.update_file_cache('forms', form_entry)

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

    def add_hazard(self, hazard_type, hazard):
        self.forms_model.add_hazard(hazard_type, hazard)

    def delete_hazard(self, hazard):
        self.forms_model.delete_hazard(hazard)

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

    def clear_pictures(self):
        self.images_model.clear_pictures()

    def clear_blueprints(self):
        self.images_model.clear_blueprints()

    def clear_forms(self):
        self.images_model.clear_forms()

    def download_pictures(self):
        self.images_model.download_pictures()
        for picture in self.sites[self.current_site]['pictures']:
            if picture not in self.file_cache['pictures']:
                pic_entry = self.file_cache['pictures']
                pic_entry[str(picture)] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.update_file_cache('pictures', pic_entry)

    def download_blueprints(self, file_name):
        self.images_model.download_blueprints(file_name)
        if file_name not in self.file_cache['blueprints']:
            bp_entry = self.file_cache['blueprints']
            bp_entry[str(file_name)] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.update_file_cache('blueprints', bp_entry)

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
    def api_key(self):
        return self.phone.get_encrypted_data('api_key')

    @api_key.setter
    def api_key(self, value):
        if value:
            self.phone.save_encrypted_data(value, 'api_key')
        else:
            self.phone.delete_data('api_key')

    @property
    def secure_api_url(self):
        return self.phone.get_encrypted_data('secure_api_url')

    @secure_api_url.setter
    def secure_api_url(self, value):
        if value:
            self.phone.save_encrypted_data(value, 'secure_api_url')
        else:
            self.phone.delete_data('secure_api_url')

    @property
    def access_token(self):
        return self.phone.get_encrypted_data('access_token')

    @access_token.setter
    def access_token(self, value):
        if value:
            self.phone.save_encrypted_data(value, 'access_token')
        else:
            self.phone.delete_data('access_token')

    @property
    def id_token(self):
        return self.phone.get_encrypted_data('id_token')

    @id_token.setter
    def id_token(self, value):
        if value:
            self.phone.save_encrypted_data(value, 'id_token')
        else:
            self.phone.delete_data('id_token')

    @property
    def refresh_token(self):
        return self.phone.get_encrypted_data('refresh_token')

    @refresh_token.setter
    def refresh_token(self, value):
        if value:
            self.phone.save_encrypted_data(value, 'refresh_token')
        else:
            self.phone.delete_data('refresh_token')

    @property
    def site_rows(self):
        return [{"text": f"{self.sites[s]['customer']}", "id": str(s),
                 "secondary_text": f"{self.sites[s]['address']}", "tertiary_text": f"{self.sites[s]['city']}",
                 "type": 'site'} for s in self.sites]

    @property
    def equipment_rows(self):
        return [{"text": str(self.equipment[e]['type']), "id": str(e), "type": 'equipment',
                 "secondary_text": f"{self.equipment[e]['unit_num']}",
                 "tertiary_text": f"{self.equipment[e]['mileage']} Hours"}
                for e in self.equipment]

    @property
    def form_rows(self):
        return [{"text": str(self.forms[f]['name']), "id": str(f).lower().replace(' ', '_'), "type": 'forms'}
                for f in self.forms if str(self.forms[f]['name']) not in ["Add Site", "Add Equipment", "Time Card"]]

    @property
    def today_rows(self):
        return [{"text": self.today['forms'][f]['name'], "id": str(f), "type": 'forms',
                 "secondary_text": f"{self.today['forms'][f]['date']} {self.today['forms'][f]['location']}",
                 "tertiary_text": f"{self.today['forms'][f]['separation']}"}
                for f in self.today['forms']]

    @property
    def blueprints(self):
        return JsonStore(self.get_directory(f'{self.database_folder}/blueprints/blueprints.json'))

    @property
    def completed_forms(self):
        return JsonStore(self.get_directory(f'{self.database_folder}/forms/completed_forms.json'))

    @property
    def equipment(self):
        return JsonStore(self.get_directory(f'{self.database_folder}/equipment.json'))

    @property
    def forms(self):
        return JsonStore(self.get_directory(f'{self.database_folder}/forms/forms.json'))

    @property
    def pictures(self):
        return JsonStore(self.get_directory(f'{self.database_folder}/pictures/pictures.json'))

    @property
    def register(self):
        return JsonStore(self.get_directory(f'{self.database_folder}/register.json'))

    @property
    def settings(self):
        return JsonStore(self.get_directory('database/settings.json'))

    @property
    def sites(self):
        return JsonStore(self.get_directory(f'{self.database_folder}/sites.json'))

    @property
    def today(self):
        return JsonStore(self.get_directory(f'{self.database_folder}/today.json'))

    @property
    def undeletable(self):
        return JsonStore(self.get_directory(f'{self.database_folder}/undeletable.json'))

    @property
    def user(self):
        return JsonStore(self.get_directory(f'{self.database_folder}/user.json'))

    @property
    def time_clock(self):
        return JsonStore(self.get_directory(f'{self.database_folder}/time_clock.json'))

    @property
    def file_cache(self):
        return JsonStore(self.get_directory('database/file_cache.json'))

    @property
    def management(self):
        return ['Justin', 'Max']

    @property
    def admin(self):
        return ['Tyson']
