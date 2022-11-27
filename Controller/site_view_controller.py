from kivy._event import EventDispatcher
from kivy.properties import ObjectProperty

from image_processing import RotatedImage
from Views.Screens.site_view.site_view import SiteView

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Controller.main_controller import MainController
    from Model.main_model import MainModel


class SiteViewController(EventDispatcher):
    main_controller: 'MainController' = ObjectProperty()

    def __init__(self, model: 'MainModel', **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.view = SiteView(name='site_view', controller=self, model=self.model)

    def remove_delete_button(self):
        self.view.ids.rail.remove_widget(self.view.ids.delet)

    def switch_to_site_view(self, site_id):
        self.model.current_site = site_id
        self.fill_location_details()
        self.fill_item_details()
        self.set_banner_image()
        self.main_controller.change_screen('site_view')

    def fill_location_details(self):
        self.view.location = f"{self.model.sites[self.model.current_site]['customer']} - {self.model.sites[self.model.current_site]['city']}"
        self.view.address = self.model.sites[self.model.current_site]['address']
        self.view.city = self.model.sites[self.model.current_site]['city']

    def fill_item_details(self):
        self.view.time_clock_data = self.model.time_clock
        self.refresh_blueprint_data()
        self.refresh_form_data()
        self.refresh_equipment_data()
        self.refresh_picture_data()

    def refresh_equipment_data(self):
        self.view.equipment = {e: self.model.equipment[e] for e in self.model.equipment
                               if self.model.equipment[e]['site'] == self.model.current_site}

    def equipment_service_popup(self, equipment_id):
        equipment_info, site = self.main_controller.equipment_service_popup(equipment_id)
        self.main_controller.view.open_equipment_service_popup(equipment_id, equipment_info, site, self)

    def refresh_form_data(self):
        self.view.new_forms = [x for x in self.model.forms if x not in ["Add Site", "Add Equipment"]]
        self.view.incomplete_forms = {f: {'name': self.model.today['forms'][f]['name'],
                                          'date': self.model.today['forms'][f]['date'],
                                          'separator': self.model.today['forms'][f]['separator']}
                                      for f in self.model.today['forms']}
        self.view.complete_forms = {x: {'name': self.model.completed_forms[x]['name'],
                                        'date': self.model.completed_forms[x]['date'],
                                        'separator': self.model.completed_forms[x]['separator'],
                                        'file_name': self.model.completed_forms[x]['file_name']}
                                    for x in self.model.sites[str(self.model.current_site)]['forms']}

    def refresh_picture_data(self):
        self.view.pictures = {x: self.model.pictures[x] for x in self.model.pictures
                              if self.model.pictures[x]['site'] == self.model.current_site}

    def refresh_blueprint_data(self):
        self.view.blueprints = {x: self.model.blueprints[x] for x in self.model.blueprints
                                if self.model.blueprints[x]['site'] == self.model.current_site}

    def set_banner_image(self):
        if header_image := self.model.get_banner_image():
            header_image = RotatedImage(image_path='assets/20220926_162254.jpg', site=self.view.location)
            header_image.rotate()
            header_image_path = header_image.image_out_path
        else:
            header_image_path = 'assets/sbs-icon-transparent.png'
        self.view.ids.header_image.source = header_image_path

    def change_feed(self, title, deletable=False):
        self.model.current_site = ''
        self.view.remove_widgets()
        self.main_controller.main_screen_controller.change_feed(title=title, deletable=deletable)
        self.main_controller.change_screen('main_screen')

    def punch_clock(self, current_datetime, current_day, action):
        self.view.punch_clock(current_datetime=current_datetime, current_day=current_day, action=action)

    def get_directions(self, address, city):
        if phone := self.model.phone:
            phone.get_directions(address=address, city=city)

    def switch_to_form_view(self, form_id):
        self.main_controller.form_view_controller.switch_to_form_view(form_id)

    def remove_widgets(self):
        self.view.remove_widgets()
