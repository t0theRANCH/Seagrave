from pyobjus import autoclass


def Keychain():
    instance = autoclass("Keychain")
    return instance()


def UIApplication():
    return autoclass('UIApplication')


def NSURL():
    return autoclass('NSURL')


def UIDocumentPickerViewController():
    return autoclass('UIDocumentPickerViewController')


def UIViewController():
    return autoclass('UIViewController')


def UIDocumentPickerMode():
    return autoclass('UIDocumentPickerMode')
