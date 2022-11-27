from api_requests import Requests

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Model.main_model import MainModel


class LoginModel:
    def __init__(self, main_model: 'MainModel'):
        self.main_model = main_model

    def check_for_user_info(self):
        u = self.main_model.phone.get_prefs_entry('user')
        if s := self.main_model.phone.get_prefs_entry('password'):
            p = self.main_model.phone.decrypt_key()
        else:
            p = ''
        user = str(u) if u else ''
        return user, p

    def save_password(self, user: str, password: str):
        cipher, iv = self.main_model.phone.encrypt_key(password)
        self.main_model.phone.add_password_shared_prefs(cipher, iv)
        self.main_model.phone.add_shared_prefs('user', user)

    def dont_save_password(self, user: str):
        self.main_model.phone.add_shared_prefs('user', user)
        self.main_model.phone.add_shared_prefs('password', '')

    def db_handler(self):
        response = self.post_auth_db_check()
        if 'none' not in response['status']:
            self.populate_db(response=response)

    def post_auth_db_check(self):
        bp = self.main_model.blueprints
        pic = self.main_model.pictures
        reg = self.main_model.register
        data = {'blueprints': [bp[x]['path'].split('/')[-1] for x in bp],
                'pictures': [pic[x]['path'].split('/')[-1] for x in pic],
                'AccessToken': self.main_model.access_token, 'iteration': reg['iteration']}
        return Requests.secure_request(name='populate', data=data, id_token=self.main_model.id_token)

    def populate_db(self, response: dict):
        dbs = list(response)
        non_file_params = [x for x in response if x in ['status', 'download_list', 'credentials']]
        for x in dbs:
            if x not in non_file_params:
                self.main_model.save_db_file(x, response[x])
        credentials = response['credentials']
        Requests.download(credentials=credentials, folder=None, title=None, dl_list=response['download_list'])
