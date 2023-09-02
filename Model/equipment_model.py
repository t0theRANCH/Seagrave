from kivy.storage.jsonstore import JsonStore
from api_requests import secure_request

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Model.main_model import MainModel


class EquipmentModel:
    def __init__(self, main_model: 'MainModel'):
        self.main_model = main_model

    def update_equipment(self, db_id: str, new_entry: dict):
        rest = self.main_model.equipment[db_id]
        for key, value in new_entry.items():
            rest[key] = value
        self.main_model.equipment[db_id] = rest
        data = {'database': 'equipment',
                'function_name': 'sql_update',
                'AccessToken': self.main_model.access_token,
                'cols': {'id': db_id,
                         'type': new_entry['type'],
                         'site_id': new_entry['site_id'],
                         'unit_num': new_entry['unit_num'],
                         'mileage': new_entry['mileage'],
                         'last_service': new_entry['last_service'],
                         'last_inspection': new_entry['last_inspection'],
                         'owned': new_entry['owned']
                         }
                }
        secure_request(id_token=self.main_model.id_token, data=data, url=self.main_model.secure_api_url)

    def get_single_equipment_data(self, equipment_id):
        equipment_info = self.main_model.equipment[equipment_id]
        site = f"{self.main_model.sites[equipment_info['site']]['customer']} - " \
               f"{self.main_model.sites[equipment_info['site']]['city']}"
        return equipment_info, site

    def edit_equipment_data(self, equipment_id, site_name, new_data):
        site_id = next(x for x in self.main_model.sites if f"{self.main_model.sites[x]['customer']} - "
                                                           f"{self.main_model.sites[x]['city']}" == site_name)
        site_info = self.get_current_site_info(site_id, equipment_id)

        old_site_id, old_site_info = self.get_old_site_info(equipment_id, site_id)
        if old_site_info:
            self.main_model.update_sites(new_entry=old_site_info, db_id=old_site_id)
        equipment_info = self.get_equipment_info(equipment_id, site_id, new_data)
        self.main_model.update_sites(new_entry=site_info, db_id=site_id)
        self.update_equipment(new_entry=equipment_info, db_id=equipment_id)

    def get_old_site_info(self, equipment_id, site_id):
        old_site_id = self.main_model.equipment[equipment_id]['site']
        if old_site_id == site_id:
            return False, False
        old_site_info = self.main_model.sites[old_site_id]
        old_site_info['equipment'].remove(equipment_id)
        return old_site_id, old_site_info

    def get_current_site_info(self, site_id, equipment_id):
        site_info = self.main_model.sites[site_id]
        site_info['equipment'].append(equipment_id)
        return site_info

    def get_equipment_info(self, equipment_id, site_id, new_data):
        equipment_info = self.main_model.equipment[equipment_id]
        equipment_info['site'] = site_id
        equipment_info['site_id'] = site_id
        equipment_info['unit_num'] = new_data['unit_num']
        equipment_info['mileage'] = new_data['mileage']
        equipment_info['last_service'] = new_data['last_service']
        equipment_info['last_inspection'] = new_data['last_inspection']
        return equipment_info
