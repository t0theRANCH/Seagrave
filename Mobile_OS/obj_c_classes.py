from pyobjus import autoclass
from pyobjus.dylib_manager import load_dylib
from os import getcwd


def KeychainBridge():
    load_dylib(f'{getcwd()}/Mobile_OS/KeychainBridge.dylib')
    return autoclass('KeychainBridge')


def UIApplication():
    return autoclass('UIApplication')


def NSURL():
    return autoclass('NSURL')


def NSString():
    return autoclass('NSString')


def UTType():
    return autoclass('UTType')


def UIDocumentPickerViewController():
    return autoclass('UIDocumentPickerViewController')


