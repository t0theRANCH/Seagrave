from kivy._event import EventDispatcher

from Views.Screens.picture_list_view.picture_list_view import PictureListView

from kivy.properties import ObjectProperty

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Controller.main_controller import MainController
    from Model.main_model import MainModel


class PictureListViewController(EventDispatcher):
    main_controller: 'MainController' = ObjectProperty()

    def __init__(self, model: 'MainModel', **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.view = PictureListView(name='picture_list_view', controller=self, model=self.model)

    def populate_grid(self, picture_data):
        self.view.pictures = picture_data
        self.view.populate_grid()
        self.main_controller.screen_manager._create_heroes_data(self.view)

    def go_back(self):
        self.view.clear_grid()
        screen_manager = self.main_controller.screen_manager
        screen_manager.current_heroes = []
        screen_manager.get_screen('site_view').remove_widgets()
        self.main_controller.change_screen('site_view')
