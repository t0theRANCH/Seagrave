from Views.Buttons.rv_button.delete_icon import DeleteIcon
from kivymd.uix.list import ThreeLineAvatarIconListItem

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from Controller.main_screen_controller import MainScreenController
    from Controller.form_view_controller import FormViewController
    from Model.main_model import MainModel


class RVButton(ThreeLineAvatarIconListItem):
    def __init__(self, id: str, controller: Union['MainScreenController', 'FormViewController'], model: 'MainModel',
                 deletable: bool = False, equipment: bool = False, blueprints: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.model = model
        self.main_screen = None
        self.ftype = None
        self.clickable = True
        self.feed = ''
        self.id = id
        self.deletable = deletable
        self.delete_icon = None
        self.download_link = None
        self.existing_form = False
        self.equipment = equipment
        self.blueprints = blueprints

    def on_release(self):
        if not self.clickable:
            return
        if self.equipment:
            self.controller.equipment_service_popup(equipment_id=self.id)
            return
        elif self.existing_form:
            self.controller.switch_to_form_view(form_id=self.id)
        elif any(x in self.feed for x in ['today', 'forms']):
            self.controller.switch_to_form_view(form_id=self.id)
        else:
            self.controller.switch_to_site_view(site_id=self.id)

    def danger_zone(self):
        if self.deletable and self.delete_icon is None:
            self.delete_icon = DeleteIcon(rvbutton=self)
            self.add_widget(self.delete_icon)
        elif self.delete_icon:
            screen = self.screen_manager.get_screen('main_screen')
            screen.change_feed(title=self.feed, deletable=True)