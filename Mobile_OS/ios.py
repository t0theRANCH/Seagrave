from os import getcwd

from kivymd.uix.snackbar import Snackbar
from pyobjus import autoclass, protocol, objc_str
from pyobjus.dylib_manager import load_framework, INCLUDE

from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty

from Mobile_OS.obj_c_classes import (
    Keychain,
    UIApplication,
    NSURL,
    UIDocumentPickerViewController,
    UIViewController,
    UIDocumentPickerMode
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Controller.main_controller import MainController


class IOS(EventDispatcher):
    main_controller: 'MainController' = ObjectProperty()

    def __init__(self, **kwargs):
        super(IOS, self).__init__(**kwargs)
        self.instance_item = None
        self.selected_file = None
        self.user = ''

    @staticmethod
    def get_shared_app():
        ui_application = UIApplication()
        return ui_application.sharedApplication()

    def get_user(self):
        keychain = Keychain()
        attributes = {
            "kSecClass": keychain.kSecClassGenericPassword,
            "kSecAttrService": 'com.sbs',
            "kSecAttrLabel": 'username_seagrave',
            "kSecReturnData": True
        }
        data_type, data = keychain.SecItemCopyMatching(attributes, None)
        self.user = data.stringValue() if data else ''
        return self.user

    def get_password(self):
        if not self.user:
            return ''
        keychain = Keychain()
        attributes = {
            'kSecClass': keychain.kSecClassGenericPassword,
            'kSecAttrAccount': self.user,
            'kSecReturnData': True,
            'kSecAttrService': "com.sbs"
        }
        data_type, data = keychain.SecItemCopyMatching(attributes, None)
        return data.stringValue() if data else ''

    @staticmethod
    def save_password(user, password):
        keychain = Keychain()
        attributes = {
            "kSecClass": keychain.kSecClassGenericPassword,
            "kSecAttrAccount": user,
            "kSecValueData": password,
            "kSecAttrService": "com.sbs",
            "kSecAttrLabel": "username_seagrave"
        }
        keychain.SecItemAdd(attributes, None)

    def dont_save_password(self, user):
        pass

    def get_directions(self, address, city):
        shared_app = self.get_shared_app()
        ns_url = NSURL()
        address = f"{address.replace(' ', '+')}, +{city}+Ontario"
        address_str = objc_str(address)
        url = ns_url.URLWithString_(f"http://maps.apple.com/?q={address_str}")
        shared_app.openURL_(url)

    def open_pdf(self, uri_path):
        shared_app = self.get_shared_app()
        ns_url = NSURL()
        url = ns_url.URLWithString_(uri_path)
        shared_app.openURL_(url)

    def open_file_picker(self, instance_item):
        self.instance_item = instance_item
        ui_document_picker_view_controller = UIDocumentPickerViewController()
        ui_view_controller = UIViewController()
        ui_document_picker_mode = UIDocumentPickerMode()
        current_vc = ui_view_controller.alloc().init()
        document_picker = ui_document_picker_view_controller.alloc().initWithDocumentTypes_inMode_(
            ['public.data'], ui_document_picker_mode.Import
        )
        document_picker.setDelegate_(current_vc)
        current_vc.presentViewController_animated_completion_(document_picker, True, None)
        current_vc.didPickDocumentAtURL_ = self.access_file_tree_result

    def access_file_tree_result(self, controller, url):
        self.selected_file = url
        controller.dismissViewControllerAnimated_completion_(True, None)
        self.upload_image()

    def upload_image(self):
        image_type = 'blueprints' if self.selected_file.split('.')[-1] == 'pdf' else 'pictures'
        dest_path = f"{getcwd()}/database/{image_type}/{self.selected_file}"
        result = self.main_controller.model.select_image_to_upload(path=dest_path, file_type=image_type,
                                                                   blueprint_type=self.instance_item.text)
        self.instance_item = None
        if not result:
            Snackbar(text='Blueprints must be a PDF')
