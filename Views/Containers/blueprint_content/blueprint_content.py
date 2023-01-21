from os.path import join, dirname

from kivy.lang import Builder

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineListItem, OneLineIconListItem, IconLeftWidget

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Controller.site_view_controller import SiteViewController


class BlueprintContent(MDBoxLayout):
    def __init__(self, blueprint_data: dict, controller: 'SiteViewController', **kwargs):
        super().__init__(**kwargs)
        self.blueprint_types = ['Architectural', 'Foundation', 'Structural', 'Cladding']
        self.controller = controller
        self.blueprint_data = blueprint_data
        self.new_blueprints = None
        self.popup = None

    def open_file_picker(self, instance_item: OneLineIconListItem):
        if phone := self.controller.model.phone:
            phone.get_storage_permissions()
            phone.open_file_picker(instance_item)
            self.popup.dismiss()
            self.popup = None

    def view_blueprints(self, instance_item: TwoLineListItem):
        blueprint_to_open = next((b['path'] for b in self.blueprint_data if b['type'] == instance_item.text), '')
        if phone := self.controller.model.phone:
            phone.open_pdf(database='blueprints', file_name=f"{blueprint_to_open}.pdf")

    def open_blueprints(self):
        items = [OneLineIconListItem(IconLeftWidget(icon='warehouse'), text=b['type'], on_release=self.view_blueprints)
                 for b in self.blueprint_data]
        self.popup = MDDialog(title='View Blueprints', items=items, type='simple')
        self.popup.size_hint_x = 1
        self.popup.open()

    def add_new_blueprints(self):
        items = [OneLineIconListItem(IconLeftWidget(icon='warehouse'), text=b, on_release=self.open_file_picker)
                 for b in self.blueprint_types]
        self.popup = MDDialog(title='Add New Blueprints', items=items, type='simple')
        self.popup.size_hint_x = 1
        self.popup.open()


Builder.load_file(join(dirname(__file__), "blueprint_content.kv"))
