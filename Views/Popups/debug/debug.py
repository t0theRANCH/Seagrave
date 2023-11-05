from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from os.path import dirname, join
import os

from kivymd.uix.list import OneLineListItem


class Debug(MDDialog):
    def __init__(self, **kwargs):
        self.title = "Debug Menu"
        self.size_hint = (0.9, 0.9)
        self.buttons = [MDFlatButton(text='Exit', on_press=self.dismiss)]
        super().__init__(**kwargs)


class DebugContent(MDBoxLayout):
    def __init__(self, model, **kwargs):
        self.model = model
        super().__init__(**kwargs)
        self.data = {'Files': ['Main', 'Database', 'Blueprints', 'Forms', 'Pictures'],
                     'Json_Database': ['sites', 'forms', 'pictures', 'equipment', 'users', 'settings', 'file_cache',
                                  'register', 'time_clock', 'today', 'undeletable', 'completed_forms'],
                     }

    def display_content(self, instance):
        self.ids.debug_list.clear_widgets()
        if instance.text in self.data:
            self.ids.content_label.text = instance.text
            for list_item in self.data[instance.text]:
                self.ids.debug_list.add_widget(OneLineListItem(text=list_item, on_release=self.display_content))
            self.ids.debug_list.add_widget(OneLineListItem(text='Back', on_release=self.display_content))
        elif instance.text == 'Back':
            self.ids.content_label.text = ''
            for list_item in self.data:
                self.ids.debug_list.add_widget(OneLineListItem(text=list_item, on_release=self.display_content))
        elif self.ids.content_label.text == 'Files':
            if instance.text.lower() == 'main':
                self.display_files('')
            elif instance.text.lower() == 'database':
                self.display_files('database')
            else:
                self.display_files(os.path.join('database', instance.text.lower()))
        elif self.ids.content_label.text == 'Json_Database':
            if instance.text in ['blueprints', 'forms', 'pictures', 'completed_forms']:
                if 'form' in instance.text:
                    path = os.path.join('database', 'forms', f"{instance.text}.json")
                else:
                    path = os.path.join('database', instance.text, f"{instance.text}.json")
            else:
                path = os.path.join('database', f"{instance.text}.json")
            self.model.phone.open_pdf(self.model.get_directory(path), mime_type='application/json')
        else:
            print('exceptions')

    def display_files(self, directory):
        for file in os.listdir(self.model.get_directory(directory)):
            self.ids.debug_list.add_widget(OneLineListItem(text=file))
        self.ids.debug_list.add_widget(OneLineListItem(text='Back', on_release=self.display_content))


Builder.load_file(join(dirname(__file__), "debug.kv"))
