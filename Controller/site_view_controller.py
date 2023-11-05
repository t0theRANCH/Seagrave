from datetime import datetime

from kivy._event import EventDispatcher
from kivy.properties import ObjectProperty, BooleanProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget

from Views.Screens.site_view.site_view import SiteView

from typing import TYPE_CHECKING, Union

from image_processing import RotatedImage

if TYPE_CHECKING:
    from Controller.main_controller import MainController
    from Model.main_model import MainModel
    from Views.Popups.multi_select_popup.multi_select_popup import MultiSelectPopup


class SiteViewController(EventDispatcher):
    main_controller: 'MainController' = ObjectProperty()
    demo_mode: bool = BooleanProperty()

    def __init__(self, model: 'MainModel', **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.view = SiteView(name='site_view', controller=self, model=self.model)
        self.popup: Union[MDDialog, None] = None

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
                               if self.model.equipment[e]['site_id'] == self.model.current_site}

    def equipment_service_popup(self, equipment_id):
        equipment_info, site = self.main_controller.equipment_service_popup(equipment_id)
        self.main_controller.view.open_equipment_service_popup(equipment_id, equipment_info, site, self)

    def refresh_form_data(self):
        self.view.new_forms = [x for x in self.model.forms if x not in ["Add Site", "Add Equipment"]]
        self.view.incomplete_forms = {f: {'name': self.model.today['forms'][f]['name'],
                                          'date': self.model.today['forms'][f]['date'],
                                          'separation': self.model.today['forms'][f]['separation']}
                                      for f in self.model.today['forms']}
        self.view.complete_forms = {x: {'name': self.model.completed_forms[x]['name'],
                                        'date': self.model.completed_forms[x]['date'],
                                        'separation': self.model.completed_forms[x]['separation'],
                                        'file_name': self.model.completed_forms[x]['file_name']}
                                    for x in self.model.sites[str(self.model.current_site)]['forms']}

    def refresh_picture_data(self):
        self.view.pictures = {x: self.model.pictures[x] for x in self.model.pictures
                              if self.model.pictures[x]['site_id'] == self.model.current_site}

    def refresh_blueprint_data(self):
        self.view.blueprints = {x: self.model.blueprints[x] for x in self.model.blueprints
                                if self.model.blueprints[x]['site_id'] == self.model.current_site}

    def set_banner_image(self):
        if not self.model.sites[self.model.current_site].get('banner_image'):
            header_image_path = 'assets/default.jpg'
        else:
            header_image = self.model.get_directory(
                self.model.pictures[self.model.sites[self.model.current_site]['banner_image']]['file_name'])
            corrected_image = RotatedImage(header_image, self.model.writeable_folder, self.model.current_site)
            corrected_image.rotate()
            header_image_path = corrected_image.image_out_path
        self.view.ids.header_image.source = header_image_path

    def change_feed(self, title, deletable=False):
        self.model.current_site = ''
        self.view.remove_widgets()
        self.main_controller.main_screen_controller.change_feed(title=title, deletable=deletable)
        self.main_controller.change_screen('main_screen')

    def danger_zone(self):
        if self.demo_mode:
            self.main_controller.demo_mode_prompt()
            return
        menu_items = [
            OneLineIconListItem(IconLeftWidget(icon='note-plus'), text=x, on_release=self.select_danger_zone_item)
            for x in ['Mark Site Complete', 'Delete Site']]
        self.popup = MDDialog(title='Danger Zone', items=menu_items, type='simple')
        self.popup.open()

    def select_danger_zone_item(self, instance_item: OneLineIconListItem):
        result = {'Mark Site Complete': 'complete', 'Delete Site': 'delete'}
        self.popup.dismiss()
        self.model.delete_site(result[instance_item.text])
        self.change_feed(title='sites', deletable=False)
        self.main_controller.change_screen('main_screen')

    def punch_clock(self, current_datetime, current_day, action):
        if self.demo_mode:
            self.main_controller.demo_mode_prompt()
            return
        self.model.punch_clock(current_datetime=current_datetime, current_day=current_day, action=action)

    def punch_other(self, popup: 'MultiSelectPopup'):
        if self.demo_mode:
            self.main_controller.demo_mode_prompt()
            return
        action = 'in' if popup.title == 'Punch In Other' else 'out'
        ids = self.get_ids() if action == 'out' else {}
        for employee in popup.selections:
            if ids:
                self.model.punch_clock(current_datetime=self.get_current_datetime(), current_day=self.get_current_day(),
                                       action=action, user=employee, sql_id=ids[employee])
            else:
                self.model.punch_clock(current_datetime=self.get_current_datetime(), current_day=self.get_current_day(),
                                       action=action, user=employee)

    def get_time_cards(self):
        time_cards = self.model.get_hours(users=self.model.forms['Safety Talk Report Form']['crew'])
        todays_time_cards = {}
        for employee, time_card in time_cards.items():
            if todays_card := self.find_current_day_card(time_card):
                todays_time_cards[employee] = todays_card
        return todays_time_cards

    def is_punched_in(self):
        todays_time_cards = self.get_time_cards()
        return [
            employee
            for employee, time_card in todays_time_cards.items()
            if time_card['clock_in'] and not time_card['clock_out']
        ]

    def get_ids(self):
        todays_time_cards = self.get_time_cards()
        return {
            employee: time_card['id']
            for employee, time_card in todays_time_cards.items()
        }

    def find_current_day_card(self, time_card):
        current_day = self.get_current_day()
        for day in time_card:
            date_obj = datetime.strptime(day['clock_in'], '%Y-%m-%d %H:%M:%S')
            if current_day == date_obj.strftime('%A'):
                return day

    def is_punched_out(self):
        punched_in = self.is_punched_in()
        return [x for x in self.model.forms["Safety Talk Report Form"]['crew'] if x not in punched_in]

    @staticmethod
    def get_current_day():
        return datetime.now().strftime('%A')

    @staticmethod
    def get_current_datetime():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def format_date(date):
        return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    def get_directions(self, address, city):
        if phone := self.model.phone:
            phone.get_directions(address=address, city=city)

    def switch_to_form_view(self, form_id):
        self.main_controller.form_view_controller.switch_to_form_view(form_id)

    def remove_widgets(self):
        self.view.remove_widgets()
