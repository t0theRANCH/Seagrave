import shutil
from os import getcwd

from kivymd.uix.snackbar import Snackbar
from pyobjus import autoclass, objc_str
from pyobjus.dylib_manager import load_framework, INCLUDE

from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty

from Mobile_OS.MyDocumentPickerDelegate import MyDocumentPickerDelegate
from Mobile_OS.obj_c_classes import (
    KeychainBridge,
    UIApplication,
    NSURL,
    NSString,
    UTType,
    UIDocumentPickerViewController,
)

from typing import TYPE_CHECKING

from api_requests import open_request
from image_processing import RotatedImage

if TYPE_CHECKING:
    from Controller.main_controller import MainController


class IOS(EventDispatcher):
    main_controller: 'MainController' = ObjectProperty()

    def __init__(self, **kwargs):
        super(IOS, self).__init__(**kwargs)
        load_framework(INCLUDE.Foundation)
        self.instance_item = None
        self.selected_file = None
        self.user = ''
        self.KeychainBridge = KeychainBridge()

    @staticmethod
    def get_shared_app():
        ui_application = UIApplication()
        return ui_application.sharedApplication()

    def get_user(self):
        self.retrieve_from_keychain('org.kivy.seagrave.user', 'default')

    def get_password(self):
        if not self.user:
            return ''
        return self.retrieve_from_keychain('org.kivy.seagrave.password', 'default')

    def delete_data(self, name):
        self.delete_from_keychain(f'org.kivy.seagrave.{name}', 'default')

    def save_password(self, user, password):
        self.delete_from_keychain('org.kivy.seagrave.password', 'default')
        self.delete_from_keychain('org.kivy.seagrave.user', 'default')
        self.save_to_keychain('org.kivy.seagrave.password', 'default', password)
        self.save_to_keychain('org.kivy.seagrave.user', 'default', user)

    def save_encrypted_data(self, token, name):
        self.save_to_keychain(f'org.kivy.seagrave.{name}', 'default', token)

    def get_encrypted_data(self, name):
        return self.retrieve_from_keychain(f'org.kivy.seagrave.{name}', 'default')

    def retrieve_from_keychain(self, service, account):
        if result := self.KeychainBridge.retrieveWithService_account_(
                objc_str(service), objc_str(account)
        ):
            return result.UTF8String()
        return ''

    def delete_from_keychain(self, service, account):
        return self.KeychainBridge.deleteWithService_account_(
            objc_str(service), objc_str(account)
        )

    def save_to_keychain(self, service, account, value):
        return self.KeychainBridge.saveWithService_account_value_(objc_str(service), objc_str(account),
                                                             objc_str(value))

    def dont_save_password(self, user):
        pass

    def get_directions(self, address, city):
        address = f"{address.replace(' ', '+')},+{city}+Ontario"
        url = f"https://maps.apple.com/?q={address}"
        self.open_url(url)

    def open_pdf(self, uri_path):
        self.open_url(uri_path)

    def open_url(self, url):
        shared_app = self.get_shared_app()
        url = NSURL().URLWithString_(objc_str(url))
        shared_app.openURL_(url)

    def open_file_picker(self, instance_item):
        self.instance_item = instance_item
        types = [UTType().typeWithFilenameExtension_("pdf"), UTType().typeWithFilenameExtension_("txt")]
        # Create the document picker.
        picker = UIDocumentPickerViewController().alloc().initForOpeningContentTypes_(types)

        # Setting the delegate to self so that delegate methods will be called on this instance.
        delegate = MyDocumentPickerDelegate()
        picker.setDelegate_(delegate)
        delegate.instance_item = instance_item
        delegate.phone = self
        # Present the picker.
        app = UIApplication().sharedApplication()
        if app and app.windows and app.windows.count() > 0:
            root_vc = app.windows.objectAtIndex_(0).rootViewController()
            root_vc.presentViewController_animated_completion_(picker, True, None)
        else:
            print("Failed to get root view controller.")

    def upload_image(self):
        image_type = 'blueprints' if self.selected_file.split('.')[-1] == 'pdf' else 'pictures'
        self.copy_image(image_type)
        dest_path = f"{self.main_controller.model.writeable_folder}/database/{image_type}/{self.selected_file.split('/')[-1]}"
        result = self.main_controller.model.select_image_to_upload(path=dest_path, file_type=image_type,
                                                                   blueprint_type=self.instance_item.text)
        self.instance_item = None
        if not result:
            Snackbar(text='Blueprints must be a PDF')

    def copy_image(self, image_type):
        if image_type == 'pictures':
            image = RotatedImage(self.selected_file, self.main_controller.model.writeable_folder)
            image.rotate()
        else:
            shutil.copy(self.selected_file, self.main_controller.model.get_directory("database/blueprints"))
