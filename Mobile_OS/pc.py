import shutil
import subprocess
import webbrowser
from os import getcwd

from kivy.utils import platform
from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty

import keyring

from typing import TYPE_CHECKING

from kivy.uix.filechooser import FileChooserListView
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar

if TYPE_CHECKING:
    from Controller.main_controller import MainController


class PC(EventDispatcher):
    main_controller: 'MainController' = ObjectProperty()
    file_chooser = None
    instance_item = None

    def save_password(self, user, password):
        self.save_user(user)
        keyring.set_password('login', user, password)

    @staticmethod
    def save_user(user):
        keyring.set_password('login', 'user', user)

    @staticmethod
    def save_token(token, name):
        keyring.set_password('token', name, token)

    @staticmethod
    def get_token(name):
        return keyring.get_password('token', name)

    def dont_save_password(self, user):
        self.save_user(user)

    @staticmethod
    def get_user():
        return keyring.get_password('login', 'user') or ''

    def get_password(self):
        return keyring.get_password('login', self.get_user()) or ''

    def open_file_picker(self, instance_item):
        self.file_chooser = FileChooserListView()
        self.instance_item = instance_item
        self.file_chooser.bind(on_submit=self.on_submit)
        self.file_chooser.open()

    def on_submit(self, instance, selection):
        image_type = 'blueprints' if selection.split('.')[-1] == 'pdf' else 'pictures'
        dest_path = f"{getcwd()}/database/{image_type}/{selection}"
        result = self.main_controller.model.select_image_to_upload(path=dest_path, file_type=image_type,
                                                                   blueprint_type=self.instance_item.text)
        # copy file to database
        shutil.copy(selection, dest_path)
        self.instance_item = None
        if not result:
            MDSnackbar(
                MDLabel(
                    text='Blueprints must be a PDF'
                )
            ).open()

    @staticmethod
    def open_pdf(uri_path):
        if platform == 'Linux':
            subprocess.run(['xdg-open', uri_path])
        elif platform == 'win':
            subprocess.run(['start', uri_path], shell=True)
        elif platform == 'macosx':
            subprocess.run(['open', '-a', 'Preview', uri_path])

    @staticmethod
    def get_directions(self, address, city):
        url = f"https://www.google.com/maps/dir/?api=1&origin=my+location&destination={address}+{city}"
        webbrowser.open(url)
