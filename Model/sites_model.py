from api_requests import Requests
from datetime import datetime, timedelta

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
            data = {'database': 'sites', 'column': column}
            Requests.secure_request('sqlUpdate', id_token=self.main_model.id_token, data=data)

    def delete_site(self, action):
        data = {'AccessToken': self.main_model.access_token, 'SiteId': self.main_model.current_site, 'action': action}
        r = Requests.secure_request(name='delete', data=data, id_token=self.main_model.id_token)
        site_db = self.main_model.sites
        site_db.delete(self.main_model.current_site)
        self.main_model.iterate_register(r)

    def update_time_clock(self, db_id: str, new_entry: dict):
        rest = self.main_model.time_clock[db_id]
        rest.update(new_entry)
        self.main_model.time_clock[db_id] = rest
        data = {'database': 'time_clock'} | new_entry
        Requests.secure_request('sqlCreate', id_token=self.main_model.id_token, data=data)

    def punch_clock(self, current_datetime, current_day, action):
        time_clock = self.main_model.time_clock['week']
        if current_day not in time_clock:
            time_clock[current_day] = {'in': '', 'out': ''}
        if datetime.strptime(time_clock[current_day]['in'], '%m/%d/%y %H:%M') - \
                datetime.strptime(current_datetime, '%m/%d/%y %H:%M') > timedelta(days=1):
            time_clock = {current_day: {'in': '', 'out': ''}}

        time_clock[current_day][action] = current_datetime
        self.update_time_clock(new_entry=time_clock, db_id='week')

