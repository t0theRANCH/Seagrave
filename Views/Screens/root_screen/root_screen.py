from os.path import join, dirname

from kivy.lang import Builder
from kivy.properties import ObjectProperty

from Views.Popups.equipment_service.equipment_service import EquipmentServicePopupContent, EquipmentService
from kivymd.uix.screen import MDScreen
from Views.Screens.root_screen.window_manager import WindowManager
from Views.Containers.nav_drawer.nav_drawer import NavDrawer
from Views.Containers.editable_label.editable_label import EditableLabel
from Views.Containers.dropdown_menu.dropdown_menu import DropdownMenu

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Controller.main_controller import MainController


class RootScreen(MDScreen):
    controller: 'MainController' = ObjectProperty()
    model: 'MainModel' = ObjectProperty()

    def __init__(self, **kwargs):
        super(RootScreen, self).__init__(**kwargs)

    def open_equipment_service_popup(self, equipment_id, equipment_info, site, controller):
        popup_content = EquipmentServicePopupContent(pre_select=[f"{x['text']}" for x in self.model.site_rows],
                                                     mileage=equipment_info['mileage'],
                                                     last_service=equipment_info['last_service'],
                                                     unit_num=equipment_info['unit_num'])
        popup = EquipmentService(title=equipment_info['type'], type='custom', controller=controller,
                                 equipment_id=equipment_id,
                                 site_name=site, content_cls=popup_content)
        popup.open()


Builder.load_file(join(dirname(__file__), "root_screen.kv"))
