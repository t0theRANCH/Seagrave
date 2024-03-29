import json
from jnius import autoclass, cast
from android import activity
from android.storage import primary_external_storage_path
from android.permissions import request_permissions, Permission
from android.runnable import run_on_ui_thread
from kivy.event import EventDispatcher
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
    MediaStore,
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
        self.intent = None
        self.PythonActivity = None
        self.get_activity()
        self.currentActivity = None
        self.get_current_activity()
        self.context = self.get_context()
        self.prefs = self.get_shared_prefs()
        self.package_name = self.context.getPackageName()
        self.file_directory = self.context.getFilesDir().toString()
        self.instance_item = None

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

    def save_password(self, user, password):
        cipher, iv = self.encrypt_key(password)
        self.add_password_shared_prefs(cipher, iv)
        self.add_shared_prefs('user', user)

    def save_encrypted_data(self, token, name):
        cipher, iv = self.encrypt_key(token, name)
        self.add_password_shared_prefs(cipher, iv, name)

    def get_encrypted_data(self, name):
        return self.decrypt_key(name) if (s := self.get_prefs_entry(name)) else ''

    def dont_save_password(self, user):
        self.add_shared_prefs('user', user)
        self.add_shared_prefs('password', '')

    @staticmethod
    def get_key(prefs, name='password'):
        key_store = KeyStore()
        keyStore = key_store.getInstance("AndroidKeyStore")
        keyStore.load(None)
        key = keyStore.getKey(name, None)
        pw = prefs.getString(name, None)
        if key and pw:
            cipherTextWrapper = json.loads(prefs.getString(name, None))
        else:
            cipherTextWrapper = None
        return key, cipherTextWrapper

    @staticmethod
    def get_cipher():
        cipher = Cipher()
        return cipher.getInstance("AES/GCM/NoPadding")

    def encrypt_key(self, password, name='password'):
        key_properties = KeyProperties()
        key_generator = KeyGenerator()
        key_gen_parameter_spec = KeyGenParameterSpec()
        string = String()

        kg = key_gen_parameter_spec(name, key_properties.PURPOSE_ENCRYPT | key_properties.PURPOSE_DECRYPT)
        kg.setBlockModes(key_properties.BLOCK_MODE_GCM)
        kg.setEncryptionPaddings(key_properties.ENCRYPTION_PADDING_NONE)
        keygenerator = key_generator.getInstance(key_properties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        keygenerator.init(kg.build())

        cipher = self.get_cipher()
        cipher.init(1, cast('java.security.Key', keygenerator.generateKey()))
        return cipher.doFinal(string(password).getBytes("UTF-8")), cipher.getIV()

    def decrypt_key(self, name='password'):
        gcm_parameter_spec = GCMParameterSpec()
        string = String()

        secretKey, cipherTextWrapper = self.get_key(self.prefs, name)
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

    def delete_data(self, name):
        editor = self.prefs.edit()
        editor.putString(name, '')
        editor.commit()

    def add_password_shared_prefs(self, cipher, iv, name='password'):
        editor = self.prefs.edit()
        j = json.dumps(CipherTextWrapper(cipher, iv).__dict__)
        editor.putString(name, j)
        editor.commit()

    def get_user(self):
        return self.get_prefs_entry('user')

    def get_password(self):
        return self.decrypt_key() if (s := self.get_prefs_entry('password')) else ''

    def get_prefs_entry(self, key):
        return self.prefs.getString(key, None)

    @staticmethod
    def create_intent(action, grant_uri_read_permission=False, action_openable=False):
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
            intent.setFlags(
                intent.FLAG_GRANT_READ_URI_PERMISSION | intent.FLAG_GRANT_WRITE_URI_PERMISSION | intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)

        if action_openable:
            intent.addCategory(intent.CATEGORY_OPENABLE)
        return intent

    def open_file_picker(self, instance_item):
        self.get_storage_permissions()
        self.instance_item = instance_item
        intent = self.create_intent(action='open_document', grant_uri_read_permission=True, action_openable=True)
        if not instance_item:
            intent.setType("image/*")
        else:
            intent.setType('application/pdf')
        self.start_intent(intent, result_code=5, result=self.access_file_tree_result)

    def get_file_name_from_uri(self, intent_data):
        openable_columns = OpenableColumns()
        return_cursor = self.get_content_resolver().query(intent_data, None, None, None, None)
        name_index = return_cursor.getColumnIndex(openable_columns.DISPLAY_NAME)
        return_cursor.moveToFirst()
        name = return_cursor.getString(name_index)
        return_cursor.close()
        return name

    def write_file_content(self, uri, path):
        fileinputstream = FileInputStream()
        fileoutputstream = FileOutputStream()
        pfd = self.get_content_resolver().openFileDescriptor(uri, 'r')  # Use 'r' for reading
        try:
            file_input_stream = fileinputstream(pfd.getFileDescriptor())
            file_output_stream = fileoutputstream(path)

            buffer = bytearray(1024)
            length = file_input_stream.read(buffer)
            while length > 0:
                file_output_stream.write(buffer, 0, length)
                length = file_input_stream.read(buffer)
        finally:
            file_input_stream.close()
            file_output_stream.close()

    @run_on_ui_thread
    def access_file_tree_result(self, request_code, result_code, intent):
        self.intent = intent
        self.main_controller.view.scrim_on(message='Uploading File')
        self.main_controller.view.async_task(self.copy_and_upload_file)

    def copy_and_upload_file(self):
        name = self.get_file_name_from_uri(self.intent.data)
        image_type = 'blueprints' if name.split('.')[-1] == 'pdf' else 'pictures'
        dest_path = f"database/{image_type}/{name}"
        self.write_file_content(uri=self.intent.data, path=dest_path)
        result = self.main_controller.model.select_image_to_upload(path=dest_path, file_type=image_type,
                                                                   blueprint_type=self.instance_item.text)
        self.instance_item = None
        self.intent = None
        if not result:
            Snackbar(text='Blueprints must be a PDF')
        activity.unbind(on_activity_result=self.access_file_tree_result)

    def open_pdf(self, uri_path, mime_type='application/pdf'):
        self.get_storage_permissions()
        intent = self.create_intent(action='view', grant_uri_read_permission=True)
        file = File()
        file_provider = FileProvider()
        share_file = file(f"{self.file_directory}/app/{uri_path}")
        uri = file_provider.getUriForFile(self.context.getApplicationContext(), f"{self.package_name}.fileprovider",
                                          share_file)
        intent.setDataAndType(uri, mime_type)
        self.start_intent(intent)

    def get_directions(self, address, city):
        uri = Uri()
        intent = self.create_intent(action='view')
        intent.setData(uri.parse(f"google.navigation:q={address.replace(' ', '+')}, +{city}+Ontario"))
        intent.setPackage("com.google.android.apps.maps")
        self.start_intent(intent)

    def install_apk(self, path):
        intent = self.create_intent(action='view')
        file_provider = FileProvider()
        content_uri = file_provider.getUriForFile(self.context.getApplicationContext(),
                                                  f"{self.package_name}.fileprovider", path)

        intent.setDataAndType(content_uri, "application/vnd.android.package-archive")
        intent.setFlags(intent.FLAG_ACTIVITY_NEW_TASK)
        intent.addFlags(intent.FLAG_GRANT_READ_URI_PERMISSION)
        self.start_intent(intent)

    def start_intent(self, intent, result=None, result_code=None):
        self.get_activity()
        self.get_current_activity()
        if not result_code:
            self.currentActivity.startActivity(intent)
        else:
            if result:
                activity.bind(on_activity_result=result)
            self.currentActivity.startActivityForResult(intent, result_code)
