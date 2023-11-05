import threading
import traceback
from os.path import join, dirname

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar

from Views.Popups.equipment_service.equipment_service import EquipmentServicePopupContent, EquipmentService
from kivymd.uix.screen import MDScreen
from Views.Containers.scrim.scrim import Scrim
from Views.Screens.root_screen.window_manager import WindowManager
from Views.Containers.nav_drawer.nav_drawer import NavDrawer
from Views.Containers.editable_label.editable_label import EditableLabel
from Views.Containers.dropdown_menu.dropdown_menu import DropdownMenu

from typing import TYPE_CHECKING

from api_requests import open_request

if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Controller.main_controller import MainController


class RootScreen(MDScreen):
    controller: 'MainController' = ObjectProperty()
    model: 'MainModel' = ObjectProperty()

    def __init__(self, **kwargs):
        super(RootScreen, self).__init__(**kwargs)
        self.scrim = Scrim()

    @staticmethod
    def send_crash_report(crash_report):
        data = {'log_type': 'crash_report', 'data': str(crash_report)}
        open_request(name='log', data=data)

    def scrim_on(self, message=''):
        def show_scrim(dt):
            self.scrim.message = message
            self.scrim.is_visible = True
        # Schedule the scrim to be displayed on the main thread
        Clock.schedule_once(show_scrim, 0)

    def scrim_off(self):
        def hide_scrim(dt):
            self.scrim.is_visible = False
            self.scrim.message = ''
        # Schedule the scrim to be hidden on the main thread
        Clock.schedule_once(hide_scrim, 0)

    def async_task(self, some_function, *args, **kwargs):
        def task():
            try:
                some_function(*args, **kwargs)  # Run your blocking operation
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                self.send_crash_report(traceback.format_exc())
                #self.error_prompt("An error has occurred. Check with your administrator.")
            finally:
                Clock.schedule_once(lambda dt: self.scrim_off(), 0)
        # Run the task in a separate thread
        threading.Thread(target=task).start()

    def demo_mode_prompt(self):
        self.error_prompt("This feature is disabled in demo mode")

    @staticmethod
    def error_prompt(message):
        MDSnackbar(
            MDLabel(
                text=message
            )
        ).open()

    def update_fab_pos(self, widget):
        widget._update_pos_buttons(Window, Window.width, Window.height)

    def open_equipment_service_popup(self, equipment_id, equipment_info, site, controller):
        popup_content = EquipmentServicePopupContent(pre_select=[f"{x['text']} - {x['tertiary_text']}"
                                                                 for x in self.model.site_rows],
                                                     mileage=equipment_info['mileage'],
                                                     last_service=equipment_info['last_service'],
                                                     unit_num=equipment_info['unit_num'],
                                                     last_inspection=equipment_info['last_inspection'])
        popup = EquipmentService(title=equipment_info['type'], type='custom', controller=controller,
                                 equipment_id=equipment_id,
                                 site_name=site, content_cls=popup_content)
        popup.open()


Builder.load_file(join(dirname(__file__), "root_screen.kv"))
