import contextlib
import shutil
import subprocess
import webbrowser
import keyring
from os import getcwd

from kivy.uix.popup import Popup
from kivy.utils import platform
from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty
from kivy.uix.filechooser import FileChooserListView
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Controller.main_controller import MainController


class PC(EventDispatcher):
    main_controller: 'MainController' = ObjectProperty()
    file_chooser = None
    instance_item = None
    popup = None

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

    @staticmethod
    def get_encrypted_data(name):
        return keyring.get_password('token', name)

    @staticmethod
    def save_encrypted_data(data, name):
        keyring.set_password('token', name, data)

    def delete_data(self, name):
        with contextlib.suppress(Exception):
            keyring.delete_password('token', name)

    def dont_save_password(self, user):
        self.save_user(user)

    @staticmethod
    def get_user():
        return keyring.get_password('login', 'user') or ''

    def get_password(self):
        return keyring.get_password('login', self.get_user()) or ''

    def open_file_picker(self, instance_item):
        self.file_chooser = FileChooserListView()
        self.file_chooser.path = getcwd()
        self.instance_item = instance_item
        self.file_chooser.bind(on_submit=self.on_submit)
        self.popup = Popup(title='Select File', content=self.file_chooser, size_hint=(0.9, 0.9))
        self.popup.open()

    def on_submit(self, instance, selection, *args):
        image = selection[0].split('/')[-1]
        image_type = 'blueprints' if image.split('.')[-1] == 'pdf' else 'pictures'
        dest_path = f"database/{image_type}/{image}"
        blueprint_type = self.instance_item.text if self.instance_item else None

        shutil.copy(selection[0], dest_path)
        result = self.main_controller.model.select_image_to_upload(path=dest_path, file_type=image_type,
                                                                   blueprint_type=blueprint_type)
        self.instance_item = None
        if not result:
            MDSnackbar(
                MDLabel(
                    text='Blueprints must be a PDF'
                )
            ).open()

    @staticmethod
    def open_pdf(uri_path, mime_type='application/pdf'):
        if platform == 'linux':
            subprocess.run(['xdg-open', uri_path])
        elif platform == 'win':
            subprocess.run(['start', uri_path], shell=True)
        elif platform == 'macosx':
            subprocess.run(['open', '-a', 'Preview', uri_path])

    @staticmethod
    def get_directions(self, address, city):
        url = f"https://www.google.com/maps/dir/?api=1&origin=my+location&destination={address}+{city}"
        webbrowser.open(url)
