from os.path import join, dirname

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog

from typing import TYPE_CHECKING, Union

from kivymd.uix.menu import MDDropdownMenu

if TYPE_CHECKING:
    from Controller.main_screen_controller import MainScreenController
    from Controller.site_view_controller import SiteViewController


class EquipmentService(MDDialog):
    def __init__(self, title, controller: Union['MainScreenController', 'SiteViewController'], equipment_id, site_name,
                 **kwargs):
        self.buttons = [MDFlatButton(text='Exit Without Saving', on_press=self.dismiss),
                        MDRaisedButton(text='Save and Exit', on_press=self.save_changes)]
        super(EquipmentService, self).__init__(**kwargs)
        self.title = title
        self.controller = controller
        self.equipment_id = equipment_id
        self.content_cls.ids.dropdown.text = site_name

    def save_changes(self, obj):
        new_data = {
            'site': self.content_cls.ids.dropdown.text,
            'mileage': self.content_cls.ids.mileage_field.text,
            'unit_num': self.content_cls.ids.unit_num_field.text,
            'last_service': self.content_cls.ids.last_service_field.text,
            'last_inspection': self.content_cls.ids.last_inspection_field.text,
        }
        self.controller.model.edit_equipment_data(equipment_id=self.equipment_id,
                                                  site_name=self.content_cls.ids.dropdown.text,
                                                  new_data=new_data)
        self.dismiss()


class EquipmentServicePopupContent(MDBoxLayout):
    def __init__(self, pre_select, mileage, last_service, unit_num, last_inspection=None, **kwargs):
        super().__init__(**kwargs)
        self.pre_select = pre_select
        self.mileage = mileage or ''
        self.last_service = last_service or ''
        self.last_inspection = last_inspection or ''
        self.unit_num = unit_num or ''
        self.mileage_until_inspection = ''
        self.mileage_until_service = ''
        self.fill_in_information()
        self.pre_select = [{"text": f"{p}", "viewclass": "OneLineListItem", "height": dp(56),
                            "on_release": lambda x=f"{p}": self.call_back(x)} for p in pre_select]
        self.menu = MDDropdownMenu(items=self.pre_select, caller=self.ids.dropdown.arrow, width_mult=4)
        self.ids.dropdown.menu = self.menu

    def call_back(self, text):
        self.ids.dropdown.text = text
        self.menu.dismiss()

    def fill_in_information(self):
        self.ids.dropdown.pre_select = self.pre_select
        self.ids.unit_num_field.text = self.unit_num
        if self.mileage:
            self.ids.mileage_field.text = self.mileage
            if self.last_service:
                self.ids.mileage_until_service_field.text = f"{int(self.mileage) - int(self.last_service)}"
        if self.last_inspection:
            self.ids.last_inspection_field.text = self.last_inspection
            self.ids.mileage_until_inspection_field.text = f"{int(self.mileage) - int(self.last_inspection)}"


Builder.load_file(join(dirname(__file__), "equipment_service.kv"))
