import json
from os import getcwd, listdir
from jnius import autoclass, cast
from android import activity
from android.storage import primary_external_storage_path
from android.permissions import request_permissions, Permission
from kivy._event import EventDispatcher
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivymd.uix.snackbar import Snackbar

from Mobile_OS.java_classes import (
    FileInputStream,
    FileOutputStream,
    Intent,
    Settings,
    Uri,
    File,
    FileProvider,
    OpenableColumns,
    String,
    GCMParameterSpec,
    KeyGenParameterSpec,
    KeyGenerator,
    KeyProperties,
    Cipher,
    KeyStore
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Controller.main_controller import MainController


class CipherTextWrapper:
    def __init__(self, cipher, iv):
        self.cipher = ','.join([str(x) for x in cipher])
        self.iv = ','.join([str(x) for x in iv])


class Android(EventDispatcher):
    main_controller: 'MainController' = ObjectProperty()

    def __init__(self, **kwargs):
        super(Android, self).__init__(**kwargs)
        self.PythonActivity = None
        self.get_activity()
        self.currentActivity = None
        self.get_current_activity()
        self.context = self.get_context()
        self.prefs = self.get_shared_prefs()
        self.package_name = self.context.getPackageName()
        self.file_directory = self.context.getFilesDir().toString()

    def get_activity(self):
        self.PythonActivity = autoclass('org.kivy.android.PythonActivity')

    def get_current_activity(self):
        self.currentActivity = cast('android.app.Activity', self.PythonActivity.mActivity)

    @staticmethod
    def get_primary_storage_path():
        return primary_external_storage_path()

    def get_context(self):
        return cast('android.content.Context', self.currentActivity.getApplicationContext())

    def get_shared_prefs(self):
        return self.context.getSharedPreferences("SEAGRAVE", self.context.MODE_PRIVATE)

    @staticmethod
    def get_storage_permissions():
        request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

    def get_content_resolver(self):
        return self.context.getContentResolver()

    def get_key(self, prefs):
        key_store = KeyStore()
        keyStore = key_store.getInstance("AndroidKeyStore")
        keyStore.load(None)
        key = keyStore.getKey("SEAGRAVE", None)
        if key:
            cipherTextWrapper = json.loads(prefs.getString('password', None))
        else:
            cipherTextWrapper = None
        return key, cipherTextWrapper

    def get_cipher(self):
        cipher = Cipher()
        return cipher.getInstance("AES/GCM/NoPadding")

    def encrypt_key(self, password):
        key_properties = KeyProperties()
        key_generator = KeyGenerator()
        key_gen_parameter_spec = KeyGenParameterSpec()
        string = String()

        kg = key_gen_parameter_spec("SEAGRAVE", key_properties.PURPOSE_ENCRYPT | key_properties.PURPOSE_DECRYPT)
        kg.setBlockModes(key_properties.BLOCK_MODE_GCM)
        kg.setEncryptionPaddings(key_properties.ENCRYPTION_PADDING_NONE)
        keygenerator = key_generator.getInstance(key_properties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        keygenerator.init(kg.build())

        cipher = self.get_cipher()
        cipher.init(1, cast('java.security.Key', keygenerator.generateKey()))
        return cipher.doFinal(string(password).getBytes("UTF-8")), cipher.getIV()

    def decrypt_key(self):
        gcm_parameter_spec = GCMParameterSpec()
        string = String()

        secretKey, cipherTextWrapper = self.get_key(self.prefs)
        cipher = self.get_cipher()

        iv = [int(x) for x in cipherTextWrapper['iv'].split(",")]
        e = [int(x) for x in cipherTextWrapper['cipher'].split(",")]

        cipher.init(2, secretKey, gcm_parameter_spec(128, iv))
        decryptedData = cipher.doFinal(e)
        p = string(decryptedData, "UTF-8").toCharArray()
        return ''.join(p)

    def add_shared_prefs(self, key, value):
        editor = self.prefs.edit()
        editor.putString(key, value)
        editor.commit()

    def add_password_shared_prefs(self, cipher, iv):
        editor = self.prefs.edit()
        j = json.dumps(CipherTextWrapper(cipher, iv).__dict__)
        editor.putString('password', j)
        editor.commit()

    def get_prefs_entry(self, key):
        return self.prefs.getString(key, None)

    def create_intent(self, action, grant_uri_read_permission=False, action_openable=False):
        intent = Intent()
        settings = Settings()
        intent_actions = {
            'view': intent.ACTION_VIEW,
            'open_document_tree': intent.ACTION_OPEN_DOCUMENT_TREE,
            'open_document': intent.ACTION_OPEN_DOCUMENT,
            'manage_all_files': settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION
        }
        intent.setAction(intent_actions[action])
        if grant_uri_read_permission:
            intent.setFlags(intent.FLAG_GRANT_READ_URI_PERMISSION)
            intent.setFlags(intent.FLAG_GRANT_WRITE_URI_PERMISSION)
            intent.setFlags(intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)
        if action_openable:
            intent.addCategory(intent.CATEGORY_OPENABLE)
        return intent

    def open_file_picker(self):
        intent = self.create_intent(action='open_document', grant_uri_read_permission=True, action_openable=True)
        intent.setType('application/pdf')
        self.start_intent(intent, result_code=5, result=self.access_file_tree_result)

    def get_file_name_from_uri(self, uri):
        openable_columns = OpenableColumns()
        return_cursor = self.get_content_resolver().query(uri, None, None, None, None)
        name_index = return_cursor.getColumnIndex(openable_columns.DISPLAY_NAME)
        return_cursor.moveToFirst()
        name = return_cursor.getString(name_index)
        return_cursor.close()
        return name

    def write_file_content(self, uri, path):
        fileinputstream = FileInputStream()
        fileoutputstream = FileOutputStream()
        pfd = self.get_content_resolver().openFileDescriptor(uri, 'w')
        try:
            file_input_stream = fileinputstream(pfd.fileDescriptor)
            file_output_stream = fileoutputstream(path)
            buffer = bytearray(1024)
            length = None
            while (length == file_input_stream.read(buffer)) > 0:
                length = file_input_stream.read(buffer)
                file_output_stream.write(buffer, 0, length)
        finally:
            file_input_stream.close()
            file_output_stream.close()

    def access_file_tree_result(self, request_code, result_code, intent):
        name = self.get_file_name_from_uri(intent.data)
        dest_path = f"{getcwd()}/database/blueprints/{name}"
        self.write_file_content(uri=intent.data, path=dest_path)
        result = self.main_controller.model.select_image_to_upload(path=dest_path, file_type='blueprints')
        if not result:
            Snackbar(text='Blueprints must be a PDF')
        #site_view = self.screen_manager.get_screen('site_view')
        #site_id = site_view.site_id
        #refresh_blueprint_data(site_id=site_id, screen_manager=self.screen_manager)
        #switch_to_site_view(screen_manager=self.screen_manager, site_id=site_id)
        #site_view.refresh_blueprint_panel()
        activity.unbind(on_activity_result=self.access_file_tree_result)

    def open_pdf(self, database, file_name):
        # file_provider = FileProvider()
        intent = self.create_intent(action='view', grant_uri_read_permission=True)
        # file = File()
        # share_file = file(f"{self.file_directory}/app/database/{database}/{file_name}")
        # uri = file_provider.getUriForFile(self.context.getApplicationContext(), f"{self.package_name}.fileprovider",
        #                                  share_file)
        # construct url name from s3 url and file name
        uri_path = 'https://buildmedia.readthedocs.org/media/pdf/pyjnius/latest/pyjnius.pdf'
        uri = Uri()
        intent.setDataAndType(uri.parse(uri_path), "application/pdf")
        self.start_intent(intent)

    def get_directions(self, address, city):
        uri = Uri()
        intent = self.create_intent(action='view')
        intent.setData(uri.parse(f"google.navigation:q={address.replace(' ', '+')}, +{city}+Ontario"))
        intent.setPackage("com.google.android.apps.maps")
        self.start_intent(intent)

    def start_intent(self, intent, result=None, result_code=None):
        if not result_code:
            self.currentActivity.startActivity(intent)
        else:
            self.get_activity()
            self.get_current_activity()
            if result:
                activity.bind(on_activity_result=result)
            self.currentActivity.startActivityForResult(intent, result_code)

