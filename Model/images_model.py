from datetime import datetime
from os import remove, listdir
from shutil import copy

from api_requests import secure_request, upload, download

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Model.main_model import MainModel


class ImagesModel:
    def __init__(self, main_model: 'MainModel'):
        self.main_model = main_model

    def update_pictures(self, db_id: str, new_entry: dict, column: str = None):
        rest = self.main_model.pictures[db_id]
        rest.update(new_entry)
        self.main_model.pictures[db_id] = rest
        if column:
            data = {'AccessToken': self.main_model.access_token, 'database': 'pictures', 'column': column,
                    'function_name': 'sql_update',
                    'cols': new_entry}
            secure_request(id_token=self.main_model.id_token, data=data)

    def update_blueprints(self, db_id: str, new_entry: dict, column: str = None):
        rest = self.main_model.blueprints[db_id]
        rest.update(new_entry)
        self.main_model.blueprints[db_id] = rest
        if column:
            data = {'AccessToken': self.main_model.access_token, 'database': 'blueprints', 'column': column,
                    'function_name': 'sql_update',
                    'cols': new_entry}
            secure_request(id_token=self.main_model.id_token, data=data)

    def download_pictures(self):
        site_id = self.main_model.current_site
        dl_list = {x['file_name']: self.main_model.get_directory(f"database/pictures/{x['file_name'].split('/')[-1]}")
                   for x in dict(self.main_model.pictures).values()
                   if x['site_id'] == site_id}
        download(url=self.main_model.secure_api_url, id_token=self.main_model.id_token,
                 access_token=self.main_model.access_token, dl_list=dl_list)

    def download_blueprints(self, file_name):
        if file_name in listdir(self.main_model.get_directory('database/blueprints')):
            return
        dl_list = {f'database/{self.main_model.current_site}/blueprints/{file_name}': self.main_model.get_directory(
            f'database/blueprints/{file_name}')}
        download(id_token=self.main_model.id_token, access_token=self.main_model.access_token,
                 url=self.main_model.secure_api_url, dl_list=dl_list)

    def clear_pictures(self):
        pictures = list(listdir(self.main_model.get_directory('database/pictures')))
        for picture in pictures:
            if picture != 'pictures.json':
                remove(self.main_model.get_directory(f'database/pictures/{picture}'))

    def clear_blueprints(self):
        blueprints = list(listdir(self.main_model.get_directory('database/blueprints')))
        for blueprint in blueprints:
            if blueprint != 'blueprints.json':
                remove(self.main_model.get_directory(f'database/blueprints/{blueprint}'))

    def clear_forms(self):
        forms = list(listdir(self.main_model.get_directory('database/forms')))
        for form in forms:
            if form not in ['forms.json', 'completed_forms.json']:
                remove(self.main_model.get_directory(f'database/forms/{form}'))

    def add_note_to_picture(self, picture_id, note):
        pic_db_entry = self.main_model.pictures[picture_id]
        pic_db_entry['note'] = note
        self.update_pictures(new_entry=pic_db_entry, db_id=picture_id)

    def get_banner_image(self):
        if 'banner_image' not in self.main_model.sites[self.main_model.current_site]:
            return None
        return self.main_model.sites[self.main_model.current_site]['banner_image'] or None

    def set_banner_image(self, value):
        if self.main_model.current_site:
            site_entry = self.main_model.sites[self.main_model.current_site]
            site_entry['banner_image'] = value
            self.main_model.update_sites(new_entry=site_entry, db_id=self.main_model.current_site,
                                         column='banner_image')

    @staticmethod
    def check_extension(required_ftype, file_type, extension, possible_file_extensions):
        return file_type is not required_ftype or extension in possible_file_extensions

    def select_image_to_upload(self, path, file_type, blueprint_type):
        extension = path.split('.')[-1]
        file_types = {'blueprints': {'possible_file_extensions': ['pdf']},
                      'pictures': {'possible_file_extensions': ['jpg', 'jpeg', 'png']}}
        if not all((self.check_extension(x, file_type, extension, y['possible_file_extensions'])
                    for x, y in file_types.items())):
            return False
        path_folders = path.split('/')
        file_name = f"database/{self.main_model.current_site}/{path_folders[-2]}/{path_folders[-1]}"
        local_path = self.main_model.get_directory(f"database/{path_folders[-2]}/{path_folders[-1]}")
        data = {"database": file_type,
                "function_name": 'sql_create',
                "AccessToken": self.main_model.access_token,
                "cols": {
                    "file_name": file_name,
                    "site_id": self.main_model.current_site
                }
                }
        if blueprint_type:
            data['cols']['type'] = blueprint_type
        response = secure_request(id_token=self.main_model.id_token, url=self.main_model.secure_api_url,
                                  data=data)
        to_be_uploaded = self.main_model.settings['To Be Uploaded']
        to_be_uploaded[file_type].append({'device_path': local_path, 'upload_path': file_name})
        self.main_model.update_settings('To Be Uploaded', to_be_uploaded)
        self.add_new_image_to_database(response, file_type, file_name, blueprint_type, local_path)
        return True

    def add_new_image_to_database(self, response, file_type, path, blueprint_type, local_path):
        f_types = ['blueprints', 'pictures']
        db_f_types = [self.main_model.blueprints, self.main_model.pictures]
        db_part = db_f_types[f_types.index(file_type)]
        new_id = str(response['body'])
        if blueprint_type:
            db_part.put(new_id, file_name=path, site_id=self.main_model.current_site, type=blueprint_type)
        else:
            db_part.put(new_id, file_name=path, site_id=self.main_model.current_site)
        upload(path=path, local_path=local_path, id_token=self.main_model.id_token,
               url=self.main_model.secure_api_url,
               access_token=self.main_model.access_token)
        self.main_model.file_cache[file_type][path] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.main_model.iterate_register(response)
        to_be_uploaded = self.main_model.settings['To Be Uploaded']
        to_be_uploaded[file_type].remove({'device_path': local_path, 'upload_path': path})
        self.main_model.update_settings('To Be Uploaded', to_be_uploaded)
