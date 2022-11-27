from colors import colors

from kivymd.uix.button.button import MDFloatingActionButton, MDFloatingActionButtonSpeedDial


class M3FloatingActionButton(MDFloatingActionButton):
    def __init__(self, icon, **kwargs):
        super(M3FloatingActionButton, self).__init__(**kwargs)
        self.theme_cls.bind()