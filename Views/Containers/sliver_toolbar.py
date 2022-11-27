from kivymd.uix.toolbar import MDTopAppBar

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Views.Screens.site_view.site_view import SiteView


class SliverToolbar(MDTopAppBar):
    def __init__(self, view: 'SiteView', **kwargs):
        super().__init__(**kwargs)
        self.left_action_items = [["menu", lambda x: self.open_close()]]
        self.type_height = "medium"
        self.view = view

    def open_close(self):
        self.view.open_close()

