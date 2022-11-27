from os.path import join, dirname

from kivy.lang import Builder

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import TwoLineListItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Controller.site_view_controller import SiteViewController


class BlueprintContent(MDBoxLayout):
    def __init__(self, blueprint_data: dict, controller: 'SiteViewController', **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.blueprint_data = blueprint_data
        self.new_blueprints = None

    def add_existing_items(self):
        for x, y in self.blueprint_data.items():
            path = y['path'].split('/')[-1].rstrip('.pdf')
            self.add_widget(TwoLineListItem(text=path, on_release=self.open_blueprints))

    def clear_panel(self):
        for c in self.children:
            if c.text != 'Add Blueprints':
                self.remove_widget(c)

    def open_file_picker(self):
        if phone := self.controller.model.phone:
            phone.get_storage_permissions()
            phone.open_file_picker()

    def open_blueprints(self, instance_item: TwoLineListItem):
        if phone := self.controller.model.phone:
            phone.open_pdf(database='blueprints', file_name=f"{instance_item.text}.pdf")

    def add_new_blueprints(self):
        self.open_file_picker()


Builder.load_file(join(dirname(__file__), "blueprint_content.kv"))
