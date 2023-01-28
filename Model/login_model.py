from api_requests import secure_request, download

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
        return secure_request(data=data, id_token=self.main_model.id_token)

    def populate_db(self, response: dict):
        dbs = list(response)
        non_file_params = [x for x in response if x in ['status', 'download_list', 'credentials']]
        for x in dbs:
            if x not in non_file_params:
                self.main_model.save_db_file(x, response[x])
        credentials = response['credentials']
        download(credentials=credentials, folder=None, title=None, dl_list=response['download_list'])
