from pyobjus import autoclass
from pyobjus.dylib_manager import load_dylib


def KeychainBridge():
    load_dylib('./KeychainBridge.dylib')
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


