from kivy._event import EventDispatcher
from kivy.properties import ObjectProperty

from Views.Screens.main_screen.main_screen import MainScreen

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Controller.main_controller import MainController
    from Model.main_model import MainModel


class MainScreenController(EventDispatcher):
    main_controller: 'MainController' = ObjectProperty()

    def __init__(self, model: 'MainModel', **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.view = MainScreen(name='main_screen', controller=self, model=self.model)
        self.feed = 'sites'
        self.feed_list = ['sites', 'equipment', 'forms', 'today']
        self.view.ids.speed_dial.data = {"Add New Site": ["map-marker-plus", "on_release", self.add_site],
                                         "Add New Equipment": ["excavator", "on_release", self.add_equipment],
                                         "Fill Out New Form": ["note-plus", "on_release", self.add_form],
                                         "Refresh Database": ["database-refresh", "on_release", self.refresh_auth]
                                         }

    def input_data_into_view(self):
        self.view.ids.toolbar.title = f"Logged in as {self.model.user['given_name']}"
        self.change_feed(title='sites')

    def close_speed_dial(self):
        if self.view.ids.speed_dial.state == "open":
            self.view.ids.speed_dial.close_stack()

    def add_site(self, *args):
        self.close_speed_dial()
        self.main_controller.form_view_controller.switch_to_form_view(form_id="add_site")

    def add_equipment(self, *args):
        self.close_speed_dial()
        self.main_controller.form_view_controller.switch_to_form_view(form_id="add_equipment")

    def add_form(self, *args):
        self.close_speed_dial()
        self.change_feed(title='forms', deletable=False)

    def equipment_service_popup(self, equipment_id):
        equipment_info, site = self.main_controller.equipment_service_popup(equipment_id)
        self.main_controller.view.open_equipment_service_popup(equipment_id, equipment_info, site, self)

    def refresh_auth(self, *args):
        self.close_speed_dial()
        self.main_controller.login_controller.refresh_auth()

    def open_close(self):
        self.main_controller.nav_drawer.open_close()

    def change_feed(self, title, deletable=False):
        widget_tree, new_feed = self.get_feed_info(title)
        self.clear_current_feed(widget_tree)
        self.feed = title
        self.view.add_widgets_to_feed(new_feed, title, deletable)

    def get_feed_info(self, title):
        tree = list(self.view.walk())
        feeds = [self.model.site_rows, self.model.equipment_rows, self.model.form_rows, self.model.today_rows]
        new_feed = feeds[self.feed_list.index(title)]
        return tree, new_feed

    def clear_current_feed(self, widget_tree):
        for t in widget_tree:
            widget_type = str(type(t))
            if 'RVButton' in widget_type:
                self.view.ids.main_feed.remove_widget(t)

    def danger_zone(self):
        for x in self.view.ids.main_feed.children:
            x.danger_zone()

    def switch_to_site_view(self, site_id):
        self.main_controller.site_view_controller.switch_to_site_view(site_id)

    def switch_to_form_view(self, form_id):
        self.main_controller.form_view_controller.switch_to_form_view(form_id)
