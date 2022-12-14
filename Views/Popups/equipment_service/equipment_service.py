from os.path import join, dirname

from kivy.lang import Builder
from kivy.properties import StringProperty

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from Controller.main_screen_controller import MainScreenController
    from Controller.site_view_controller import SiteViewController


class EquipmentService(MDDialog):
    def __init__(self, title, controller: Union['MainScreenController', 'SiteViewController'], equipment_id, site_name, **kwargs):
        self.buttons = [MDFlatButton(text='Back', on_press=self.dismiss),
                        MDRaisedButton(text='Change Site', on_press=self.change_site)]
        super(EquipmentService, self).__init__(**kwargs)
        self.title = title
        self.controller = controller
        self.equipment_id = equipment_id
        self.content_cls.ids.dropdown.text = site_name

    def change_site(self, obj):
        self.controller.model.move_equipment(equipment_id=self.equipment_id, site_name=self.content_cls.ids.label.text)
        self.dismiss()


class EquipmentServicePopupContent(MDBoxLayout):
    mileage = StringProperty(allownone=True)
    last_service = StringProperty(allownone=True)
    last_inspection = StringProperty(allownone=True)
    unit_num = StringProperty(allownone=True)
    mileage_until_inspection = StringProperty(allownone=True)
    mileage_until_service = StringProperty(allownone=True)

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

    def fill_in_information(self):
        self.ids.dropdown.pre_select = self.pre_select
        self.ids.unit_num_field.text = self.unit_num
        if self.mileage:
            self.ids.mileage_field.text = self.mileage
            if self.last_service:
                self.ids.mileage_until_service_field.text = f"{int(self.mileage) - int(self.last_service)}"
        else:
            self.remove_widget(self.ids.mileage_field)
            self.remove_widget(self.ids.mileage_until_service_field)
        if self.last_inspection:
            self.ids.last_inspection_field.text = self.last_inspection
        else:
            self.remove_widget(self.ids.last_inspection_field)


Builder.load_file(join(dirname(__file__), "equipment_service.kv"))
