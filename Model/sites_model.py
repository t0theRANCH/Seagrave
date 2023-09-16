from os import remove

from api_requests import secure_request

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Model.main_model import MainModel


class SitesModel:
    def __init__(self, main_model: 'MainModel'):
        self.main_model = main_model

    def update_sites(self, db_id: str, new_entry: dict, column: str = None):
        rest = self.main_model.sites[db_id]
        rest.update(new_entry)
        self.main_model.sites[db_id] = rest
        if column:
            data = {'AccessToken': self.main_model.access_token, 'database': 'sites', 'column': column,
                    'function_name': 'sql_update', 'cols': new_entry}
            secure_request(id_token=self.main_model.id_token, data=data)

    def delete_site(self, action):
        data = {'AccessToken': self.main_model.access_token, 'Id': self.main_model.current_site, 'action': action,
                'function_name': 'sql_delete', 'database': 'sites'}
        r = secure_request(data=data, id_token=self.main_model.id_token, url=self.main_model.secure_api_url)
        site_db = self.main_model.sites
        site_db.delete(self.main_model.current_site)
        self.delete_cached_files()
        self.main_model.iterate_register(r)

    def delete_cached_files(self):
        site = self.main_model.sites[self.main_model.current_site]
        for blueprint in site['blueprints']:
            remove(f'blueprints/{self.main_model.blueprints[blueprint]["file_name"]}')
        for picture in site['pictures']:
            remove(f'pictures/{self.main_model.pictures[picture]["file_name"]}')
        for form in site['forms']:
            remove(f'forms/{self.main_model.forms[form]["file_name"]}')

    def update_time_clock(self, new_entry: dict):
        self.main_model.time_clock.clear()
        for key, value in new_entry.items():
            self.main_model.time_clock[key] = value

    def punch_clock(self, current_datetime, current_day, action):
        data = self.format_request(action, current_datetime, current_day)
        response = secure_request(id_token=self.main_model.id_token, data=data, url=self.main_model.secure_api_url)
        self.get_hours()

    def format_request(self, action, current_datetime, current_day):
        if action == 'in':
            d = {'function_name': 'sql_create',
                 'cols': {'employee': self.main_model.user['given_name'],
                          'clock_in': current_datetime,
                          'status': 'in'}
                 }
        else:
            d = {'function_name': 'sql_update',
                 'cols': {'clock_out': current_datetime,
                          'status': 'out',
                          'employee': self.main_model.user['given_name'],
                          'id': self.main_model.time_clock[current_day]['id']}
                 }
        return {
                   'AccessToken': self.main_model.access_token,
                   'database': 'time_clock',
               } | d

    def get_hours(self):
        data = {'function_name': 'get_hours', 'AccessToken': self.main_model.access_token}
        time_card = secure_request(id_token=self.main_model.id_token, data=data, url=self.main_model.secure_api_url)
        self.update_time_clock(new_entry=time_card)
