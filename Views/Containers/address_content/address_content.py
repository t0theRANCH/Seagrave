from os.path import join, dirname

from kivy.lang import Builder

from kivymd.uix.boxlayout import MDBoxLayout

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Controller.site_view_controller import SiteViewController


class AddressContent(MDBoxLayout):
    def __init__(self, controller: 'SiteViewController', address: str, city: str, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.address = address
        self.city = city
        self.set_address()

    def set_address(self):
        self.ids.address.text = f"{self.address}\n{self.city}, Ontario"

    def get_directions(self):
        self.controller.get_directions(address=self.address, city=self.city)


Builder.load_file(join(dirname(__file__), "address_content.kv"))
