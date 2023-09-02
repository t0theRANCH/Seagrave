from os.path import join, dirname

from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu

from Views.Containers.label_switch.label_switch import LabelSwitch


class Settings(MDDialog):
    def __init__(self, **kwargs):
        self.buttons = [MDFlatButton(text='Exit Without Saving', on_press=self.dismiss),
                        MDRaisedButton(text='Save and Exit', on_press=self.save_changes)]
        super().__init__(**kwargs)

    def save_changes(self, obj):
        self.content_cls.save_settings()
        self.dismiss()


class SettingsContent(MDBoxLayout):
    def __init__(self, model, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.switches = {'Save Password': self.ids.save_password, 'Keep Me Logged In': self.ids.keep_logged_in}
        self.menus = {'Cache Documents (Weeks)':
                          {'widget': self.ids.cache_documents,
                           'menu_items': ['1', '2', '3', '4', '5', 'Completion of Site'],
                           'integer': True,
                           'accepted_values': ['Completion of Site'],
                           }
                      }
        self.load_settings()
        self.load_menus()

    def load_menus(self):
        for text, menu in self.menus.items():
            menu['widget'].hint_text = text
            pre_select = [{"text": f"{m}", "viewclass": "OneLineListItem", "height": dp(56), 'popup_content': self,
                            "on_release": lambda x=f"{m}": self.call_back(x, menu['widget'])} for m in menu['menu_items']]
            menu['widget'].menu = MDDropdownMenu(items=pre_select, caller=menu['widget'].arrow, width_mult=6)

    def call_back(self, value, menu):
        if self.menus[menu.hint_text]['integer'] and not self.check_int(value) and value not in self.menus[menu.hint_text]['accepted_values']:
            self.model.display_error_snackbar('Please enter an integer')
            menu.menu.dismiss()
            return
        menu.text = value
        menu.menu.dismiss()

    def load_settings(self):
        settings = dict(self.model.settings)
        for switch in self.switches.values():
            switch.switch_active = settings.get(switch.label_text, False)
        for menu in self.menus.values():
            menu['widget'].text = settings.get(menu['widget'].text, '')


    def save_settings(self):
        settings = dict(self.model.settings)
        for text, switch in self.switches.items():
            settings[text] = switch.switch_active
        for text, menu in self.menus.items():
            settings[text] = menu['widget'].text
        self.model.save_db_file('settings', settings)

    @staticmethod
    def bool_to_str(boolean):
        return 'True' if boolean else 'False'

    @staticmethod
    def check_int(value):
        try:
            int(value)
            return True
        except ValueError:
            return False


Builder.load_file(join(dirname(__file__), "settings.kv"))
