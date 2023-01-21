from kivy.core.window import Window
from kivymd.uix.screenmanager import MDScreenManager


class WindowManager(MDScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)

    def events(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 27:
            if self.current != 'login_screen':
                previous_screen = self.get_previous_screen()
                if previous_screen not in ['login_screen', 'form_view']:
                    self.current = previous_screen
                else:
                    self.get_screen('login_screen').back()
            return True

    def get_previous_screen(self):
        return self.get_screen(self.current).previous_screen
