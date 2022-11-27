from kivy.storage.jsonstore import JsonStore
from api_requests import Requests

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Model.main_model import MainModel


class EquipmentModel:
    def __init__(self, main_model: 'MainModel'):
        self.main_model = main_model

    def update_equipment(self, db_id: str, new_entry: dict, column: str = None):
        rest = self.main_model.equipment[db_id]
        rest.update(new_entry)
        self.main_model.equipment[db_id] = rest
        if column:
            data = {'database': 'equipment', 'column': column}
            Requests.secure_request('sqlUpdate', id_token=self.main_model.id_token, data=data)

    def get_single_equipment_data(self, equipment_id):
        equipment_info = self.main_model.equipment[equipment_id]
        site = f"{self.main_model.sites[equipment_info['site']]['customer']} - " \
               f"{self.main_model.sites[equipment_info['site']]['city']}"
        return equipment_info, site

    def move_equipment(self, equipment_id, site_name):
        site_id = next(x for x in self.main_model.sites if f"{self.main_model.sites[x]['customer']} - "
                                                           f"{self.main_model.sites[x]['city']}" == site_name)
        site_info = self.get_current_site_info(site_id, equipment_id)
        old_site_id, old_site_info = self.get_old_site_info(equipment_id)
        equipment_info = self.get_equipment_info(equipment_id, site_id)
        self.main_model.update_sites(new_entry=site_info, db_id=site_id, column='equipment')
        self.main_model.update_sites(new_entry=old_site_info, db_id=old_site_id, column='equipment')
        self.update_equipment(new_entry=equipment_info, db_id=equipment_id, column='site')

    def get_old_site_info(self, equipment_id):
        old_site_id = self.main_model.equipment[equipment_id]['site']
        old_site_info = self.main_model.sites[old_site_id]
        old_site_info['equipment'].remove(equipment_id)
        return old_site_id, old_site_info

    def get_current_site_info(self, site_id, equipment_id):
        site_info = self.main_model.sites[site_id]
        site_info['equipment'].append(equipment_id)
        return site_info

    def get_equipment_info(self, equipment_id, site_id):
        equipment_info = self.main_model.equipment[equipment_id]
        equipment_info['site'] = site_id
        equipment_info['site_id'] = site_id
        return equipment_info
