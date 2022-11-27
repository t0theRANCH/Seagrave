from os.path import join, dirname

from kivy.lang import Builder

from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Controller.site_view_controller import SiteViewController


class EquipmentContent(MDBoxLayout):
    def __init__(self, controller: 'SiteViewController', equipment_data, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.equipment_data = equipment_data
        self.popup = None
        self.move_equipment_target = None

    def add_equipment(self):
        self.controller.switch_to_form_view(form_id="add_equipment")

    def view_equipment(self):
        items = [OneLineIconListItem(IconLeftWidget(icon='excavator'), text=y['type'], id=x,
                                     on_release=self.equipment_service_popup)
                 for x, y in self.equipment_data.items()]
        if not items:
            toast('There is no equipment on this site')
            return
        self.popup = MDDialog(title='View Equipment', items=items, type='simple')
        self.popup.size_hint_x = 1
        self.popup.open()

    def move_equipment(self):
        equipment_on_other_sites = self.controller.model.get_equipment_data()
        items = [OneLineIconListItem(IconLeftWidget(icon='excavator'), text=y['type'], id=x,
                                     on_release=self.move_equipment_confirm)
                 for x, y in equipment_on_other_sites.items()]
        if not items:
            toast('There is no equipment on any other site')
            return
        self.popup = MDDialog(title='Move Equipment', items=items, type='simple')
        self.popup.size_hint_x = 1
        self.popup.open()

    def move_equipment_confirm(self, instance_item: OneLineIconListItem):
        self.popup.dismiss()
        popup_text = f"Move {instance_item.text} to {self.site_view.location}?"
        self.popup = MDDialog(title=popup_text,
                              buttons=[MDFlatButton(text='Cancel', on_release=self.cancel_move),
                                       MDFlatButton(text='Confirm', on_release=self.finalize_move)])
        self.popup.open()
        self.move_equipment_target = instance_item

    def cancel_move(self, obj):
        self.move_equipment_target = None
        self.popup.dismiss()

    def finalize_move(self, obj):
        self.popup.dismiss()
        self.controller.model.move_equipment(equipment_id=self.move_equipment_target.id,
                                             site_name=self.controller.view.location)
        self.controller.refresh_equipment_data()
        self.controller.remove_widgets()
        self.controller.switch_to_site_view(self.controller.model.current_site)
        self.site_view.on_pre_enter()

    def equipment_service_popup(self, instance_item: OneLineIconListItem):
        self.popup.dismiss()
        self.controller.equipment_service_popup(equipment_id=instance_item.id)


Builder.load_file(join(dirname(__file__), "equipment_content.kv"))
