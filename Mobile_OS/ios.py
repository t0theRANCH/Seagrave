import shutil
from os import listdir, remove

from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel

from pyobjus import autoclass, objc_str

from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty

from Mobile_OS.MyDocumentPickerDelegate import MyDocumentPickerDelegate
from Mobile_OS.MyImagePickerDelegate import MyImagePickerDelegate
from Mobile_OS.obj_c_classes import (
    KeychainBridge,
    UIApplication,
    NSURL,
    NSString,
    NSError,
    NSFileManager,
    UTType,
    UIDocumentPickerViewController,
    UIImagePickerController,
    UINavigationController,
    PHPickerConfiguration,
    PHPickerViewController,
    PDFModalViewController,
)

from typing import TYPE_CHECKING

from api_requests import open_request

if TYPE_CHECKING:
    from Controller.main_controller import MainController


class IOS(EventDispatcher):
    main_controller: 'MainController' = ObjectProperty()

    def __init__(self, **kwargs):
        super(IOS, self).__init__(**kwargs)
        self.instance_item = None
        self.selected_file = None
        self.selected_file_name = None
        self.KeychainBridge = KeychainBridge()

    @staticmethod
    def get_shared_app():
        ui_application = UIApplication()
        return ui_application.sharedApplication()

    def get_user(self):
        return self.retrieve_from_keychain('org.kivy.seagrave.user', 'default')

    def get_password(self):
        return self.retrieve_from_keychain('org.kivy.seagrave.password', 'default')

    def delete_data(self, name):
        self.delete_from_keychain(f'org.kivy.seagrave.{name}', 'default')

    def save_password(self, user, password):
        self.delete_from_keychain('org.kivy.seagrave.password', 'default')
        self.delete_from_keychain('org.kivy.seagrave.user', 'default')
        self.save_to_keychain('org.kivy.seagrave.password', 'default', password)
        self.save_to_keychain('org.kivy.seagrave.user', 'default', user)

    def save_encrypted_data(self, token, name):
        self.delete_from_keychain(f'org.kivy.seagrave.{name}', 'default')
        self.save_to_keychain(f'org.kivy.seagrave.{name}', 'default', token)

    def get_encrypted_data(self, name):
        return self.retrieve_from_keychain(f'org.kivy.seagrave.{name}', 'default')

    def retrieve_from_keychain(self, service, account):
        if result := self.KeychainBridge.retrieveWithService_account_(
                objc_str(service), objc_str(account)
        ):
            result = result.UTF8String()
            # for some reason, the ios-sim returns a bytes object, but the actual phone returns a str object that you can't use isinstance on
            if 'bytes' in str(type(result)):
                result = result.decode('utf-8')
            return result
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
        pdf_modal, pdf_modal_view_controller = PDFModalViewController()
        ui_navigation_controller = UINavigationController()
        ns_string = NSString()
        ns_pdf_path = ns_string.stringWithUTF8String_(uri_path)

        pdf_modal_vc = pdf_modal_view_controller.alloc().initWithPDFAtPath_(ns_pdf_path)

        nav_controller = ui_navigation_controller.alloc().initWithRootViewController_(pdf_modal_vc)
        nav_controller.modalPresentationStyle = 0
        if root_vc := self.get_root_view_controller():
            root_vc.presentModalViewController_animated_(nav_controller, True)

    def open_url(self, url):
        shared_app = self.get_shared_app()
        url = NSURL().URLWithString_(objc_str(url))
        shared_app.openURL_(url)

    def open_file_picker(self, instance_item):
        self.instance_item = instance_item
        if not instance_item:
            self.pick_image()
            return

        types = [UTType().typeWithFilenameExtension_("pdf")]
        # Create the document picker.
        picker = UIDocumentPickerViewController().alloc().initForOpeningContentTypes_(types)

        # Setting the delegate to self so that delegate methods will be called on this instance.
        delegate = MyDocumentPickerDelegate()
        picker.setDelegate_(delegate)
        delegate.phone = self
        if root_vc := self.get_root_view_controller():
            root_vc.presentViewController_animated_completion_(picker, True, None)

    def pick_image(self):
        ui_image_picker_controller = UIImagePickerController()
        picker = ui_image_picker_controller.alloc().init()
        delegate = MyImagePickerDelegate()
        picker.setDelegate_(delegate)
        delegate.phone = self
        # Set the source type using the associated integer value
        picker.sourceType = 0  # 0 corresponds to UIImagePickerControllerSourceTypePhotoLibrary
        if root_vc := self.get_root_view_controller():
            root_vc.presentViewController_animated_completion_(picker, True, None)

    @staticmethod
    def get_root_view_controller():
        app = UIApplication().sharedApplication()
        if app and app.windows and app.windows.count() > 0:
            return app.windows.objectAtIndex_(0).rootViewController()
        print("Failed to get root view controller.")
        return None

    def upload_image(self):
        if self.selected_file_name.endswith('.pdf'):
            image_type = 'blueprints'
        else:
            image_type = 'pictures'
        dest_path = self.main_controller.model.get_directory(f"database/{image_type}/{self.selected_file_name}")
        self.copy_image(image_type)
        blueprint_type = self.instance_item.text if self.instance_item else None
        result = self.main_controller.model.select_image_to_upload(path=dest_path, file_type=image_type,
                                                                   blueprint_type=blueprint_type)
        self.instance_item = None
        self.selected_file = None
        if not result:
            MDSnackbar(
                MDLabel(
                    text='Unsupported file type',
                )
            ).open()

    def copy_image(self, image_type):
        if image_type == 'blueprints':
            self.access_scoped_resource()
            return
        shutil.copy(self.selected_file,
                    self.main_controller.model.get_directory(
                        f"database/{image_type}/{self.selected_file_name}"))

    def access_scoped_resource(self):
        if self.selected_file_name in listdir(self.main_controller.model.get_directory('database/blueprints')):
            # This should only be temporary until I implement a popup to ask if they want to overwrite the file
            remove(self.main_controller.model.get_directory(f"database/blueprints/{self.selected_file_name}"))
        ns_url = NSURL()
        ns_file_manager = NSFileManager()
        # 1. Start accessing the security-scoped resource
        source_url = ns_url.URLWithString_(self.selected_file)  # str_url is the URL string you got from the picker
        source_url.startAccessingSecurityScopedResource()

        destination_path = self.main_controller.model.get_directory(f"database/blueprints/{self.selected_file_name}")
        destination_url = ns_url.fileURLWithPath_(destination_path)

        # 3. Copy the file
        file_manager = ns_file_manager.defaultManager()
        error = None
        success = file_manager.copyItemAtURL_toURL_error_(source_url, destination_url, error)
        if not success:
            open_request(
                'log',
                {
                    'log_type': 'error',
                    'data': f"Failed to copy file: {self.selected_file_name}",
                },
            )
        # 4. Stop accessing the security-scoped resource
        source_url.stopAccessingSecurityScopedResource()
        self.selected_file_name = None
