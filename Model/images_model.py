from shutil import copy
from os import remove

from api_requests import Requests

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
            data = {'database': 'pictures', 'column': column}
            Requests.secure_request('sqlUpdate', id_token=self.main_model.id_token, data=data)

    def update_blueprints(self, db_id: str, new_entry: dict, column: str = None):
        rest = self.main_model.blueprints[db_id]
        rest.update(new_entry)
        self.main_model.blueprints[db_id] = rest
        if column:
            data = {'database': 'blueprints', 'column': column}
            Requests.secure_request('sqlUpdate', id_token=self.main_model.id_token, data=data)

    def add_note_to_picture(self, picture_id, note):
        pic_db_entry = self.main_model.pictures[picture_id]
        pic_db_entry['note'] = note
        self.update_pictures(new_entry=pic_db_entry, db_id=picture_id, column='note')

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
                      'pictures': {'possible_file_extensions': ['jpg', 'png']}}
        if not all((self.check_extension(x, file_type, extension, y['possible_file_extensions'])
                    for x, y in file_types.items())):
            return False
        data = {"database": file_type, "name": path, "site": self.main_model.current_site}
        if blueprint_type:
            data['type'] = blueprint_type
        response = Requests.secure_request(data=data, name='sqlCreate', id_token=self.main_model.id_token)
        self.add_new_image_to_database(response, file_type, path)
        return True

    def add_new_image_to_database(self, response, file_type, path):
        f_types = ['blueprints', 'pictures']
        db_f_types = [self.main_model.blueprints, self.main_model.pictures]
        db_part = db_f_types[f_types.index(file_type)]
        new_id = str(response['body'])
        save_path = f"database/{file_type}"
        db_part.put(new_id, path=f"{save_path}/{path.split('/')[-1]}", site=self.main_model.current_site)
        if file_type == 'pictures':
            copy(path, f"{save_path}")
        response = Requests.upload(path, self.main_model.id_token)
        self.main_model.iterate_register(response)
