from Views.Popups.confirm_delete.confirm_delete import ConfirmDelete
from kivymd.uix.list import IconRightWidget

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rv_button import RVButton


class DeleteIcon(IconRightWidget):
    def __init__(self, rvbutton: 'RVButton', **kwargs):
        super(IconRightWidget, self).__init__(**kwargs)
        self.icon = 'close-box'
        self.rvbutton = rvbutton

    def on_release(self):
        cd = ConfirmDelete(self.rvbutton.model, self.rvbutton.text, self.rvbutton.feed, self.rvbutton)
        cd.open()

