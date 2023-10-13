from datetime import datetime, timedelta
from os import remove

from api_requests import secure_request, download, open_request

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Model.main_model import MainModel


class LoginModel:
    def __init__(self, main_model: 'MainModel'):
        self.main_model = main_model

    def check_for_user_info(self):
        u = self.main_model.phone.get_user()
        p = self.main_model.phone.get_password()
        user = str(u) if u else ''
        return user, p

    def save_password(self, user: str, password: str):
        self.main_model.phone.save_password(user, password)

    def dont_save_password(self, user: str):
        self.main_model.phone.dont_save_password(user)

    def db_handler(self):
        creds = open_request(name='get_credentials', data={'AccessToken': self.main_model.access_token},
                             auth=self.main_model.id_token)
        if 'statusCode' in creds and creds['statusCode'] == 400:
            return self.delete_tokens()
        if 'message' not in creds:
            self.save_credentials(creds)
        elif 'expired' in creds['message'] or 'unauthorized' in creds['message'] or 'Missing Authentication Token' in creds['message']:
            return self.delete_tokens()
        response = self.post_auth_db_check()
        if 'Not authorized' in response.get('body', ''):
            return self.delete_tokens()
        if 'status' in response and 'none' not in response['status']:
            self.populate_db(response=response)

    def delete_tokens(self):
        self.main_model.access_token = ''
        self.main_model.id_token = ''
        return

    def save_credentials(self, creds):
        self.main_model.api_key = creds['api_key']
        self.main_model.secure_api_url = creds['api_address']

    def post_auth_db_check(self):
        reg = self.main_model.register
        data = {'AccessToken': self.main_model.access_token, 'iteration': reg['iteration'],
                'api_key': self.main_model.api_key, 'function_name': 'populate'}
        return secure_request(data=data, id_token=self.main_model.id_token,
                              url=self.main_model.secure_api_url)

    def populate_db(self, response: dict):
        self.check_cache()
        dbs = list(response)
        non_file_params = [x for x in response if x in ['status', 'download_list', 'credentials']]
        for x in dbs:
            if x not in non_file_params:
                if x in ['pictures', 'blueprints', 'completed_forms']:
                    db_name = f"{x.split('_')[-1]}/{x}"
                else:
                    db_name = x
                self.main_model.save_db_file(db_name, response[x])
        download(url=self.main_model.secure_api_url,
                 id_token=self.main_model.id_token,
                 access_token=self.main_model.access_token,
                 dl_list=response['download_list'])

    def check_cache(self):
        settings = self.main_model.settings
        cache_date = settings['Cache Documents (Weeks)']
        today = datetime.now()
        if cache_date == 'Completion of Site':
            return
        difference = timedelta(weeks=cache_date)
        for cache in self.main_model.file_cache:
            for file, date in cache.items():
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                if today - date > difference:
                    self.main_model.file_cache[cache].remove(file)
                    remove(self.main_model.get_directory(f"database/{cache}/{file}"))
        self.main_model.save_db_file('file_cache', self.main_model.file_cache)

