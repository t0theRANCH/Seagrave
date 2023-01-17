from os.path import join, dirname

from kivy.lang import Builder
from kivy.properties import ObjectProperty

from Views.Containers.equipment_content.equipment_content import EquipmentContent
from Views.Containers.form_content.form_content import FormContent
from Views.Containers.picture_content.picture_content import PictureContent
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.screen import MDScreen

from Views.Containers.address_content.address_content import AddressContent
from Views.Containers.blueprint_content.blueprint_content import BlueprintContent
from Views.Containers.sliver_toolbar import SliverToolbar
from Views.Containers.time_clock_content.time_clock_content import TimeClockContent


from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from Model.main_model import MainModel
    from Controller.site_view_controller import SiteViewController


class SiteView(MDScreen):
    controller: 'SiteViewController' = ObjectProperty()
    model: 'MainModel' = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.location = ''
        self.address = ''
        self.city = ''
        self.content = []
        self.time_clock_data = None
        self.blueprints = None
        self.new_forms = None
        self.incomplete_forms = None
        self.complete_forms = None
        self.equipment = None
        self.pictures = None

    def on_pre_enter(self, *args):
        self.ids.top_appbar.toolbar_cls = SliverToolbar(headline_text=self.location, view=self)
        address_content = AddressContent(address=self.address, city=self.city, controller=self.controller)
        time_clock_content = MDExpansionPanel(
            icon='clock-time-seven',
            content=TimeClockContent(time_clock_data=self.time_clock_data, controller=self.controller),
            panel_cls=MDExpansionPanelOneLine(
                text='Punch Clock'
            )
        )
        blueprint_content = MDExpansionPanel(
            icon='warehouse',
            content=BlueprintContent(blueprint_data=self.blueprints, controller=self.controller),
            panel_cls=MDExpansionPanelOneLine(
                text='Blueprints'
            )
        )
        equipment_content = MDExpansionPanel(
            icon='excavator',
            content=EquipmentContent(equipment_data=self.equipment, controller=self),
            panel_cls=MDExpansionPanelOneLine(
                text='Equipment'
            )
        )
        picture_content = MDExpansionPanel(
            icon='image',
            content=PictureContent(picture_data=self.pictures, controller=self.controller),
            panel_cls=MDExpansionPanelOneLine(
                text='Pictures'
            )
        )

        form_content = MDExpansionPanel(
            icon="note",
            content=FormContent(controller=self.controller, new_form_data=self.new_forms,
                                incomplete_form_data=self.incomplete_forms, complete_form_data=self.complete_forms),
            panel_cls=MDExpansionPanelOneLine(
                text='Forms'
            )
        )
        self.content = [address_content, time_clock_content, blueprint_content, equipment_content, picture_content,
                        form_content]
        for c in self.content:
            self.ids.content.add_widget(c)

    def open_close(self):
        self.controller.main_controller.nav_drawer.open_close()

    def remove_widgets(self):
        for c in self.content:
            self.ids.content.remove_widget(c)
        self.content = []


Builder.load_file(join(dirname(__file__), "siteview.kv"))
