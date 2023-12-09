from pyobjus import autoclass
from pyobjus.dylib_manager import load_dylib, load_framework, INCLUDE
from os import getcwd


"""
KeychainBridge compile commands

First compile the ios-sim dylib:
clang -target x86_64-apple-ios13.0-simulator -isysroot $(xcrun --sdk iphonesimulator --show-sdk-path) \
-F$(xcrun --sdk iphonesimulator --show-sdk-path)/System/Library/Frameworks -framework Security -framework Foundation \
-shared -o KeychainBridge_sim.dylib KeychainBridge.m


Then compile the ios dylib:
clang -target arm64-apple-ios13.0 -isysroot $(xcrun --sdk iphoneos --show-sdk-path) -F$(xcrun --sdk iphoneos \
--show-sdk-path)/System/Library/Frameworks -framework Security -framework Foundation -shared -o \
KeychainBridge_device.dylib KeychainBridge.m

then run this command to create a fat dylib:
lipo -create -output KeychainBridge.dylib KeychainBridge_sim.dylib KeychainBridge_device.dylib
"""


def KeychainBridge():
    load_framework(INCLUDE.Foundation)
    load_dylib(f'{getcwd()}/Mobile_OS/KeychainBridge.dylib')
    return autoclass('KeychainBridge')


def UIApplication():
    return autoclass('UIApplication')


def NSURL():
    return autoclass('NSURL')


def NSFileManager():
    return autoclass('NSFileManager')


def NSString():
    return autoclass('NSString')


def NSError():
    return autoclass('NSError')


def UTType():
    return autoclass('UTType')


def UIDocumentPickerViewController():
    return autoclass('UIDocumentPickerViewController')


def UIImagePickerController():
    return autoclass('UIImagePickerController')


def UINavigationController():
    return autoclass('UINavigationController')


def PHPickerViewController():
    return autoclass('PHPickerViewController')


def PHPickerConfiguration():
    return autoclass('PHPickerConfiguration')


def PDFModalViewController():
    load_framework(f"{getcwd()}/PDFModalViewController.framework")
    PDFModalViewController_ = autoclass('PDFModalViewController')
    return PDFModalViewController_.alloc().init(), PDFModalViewController_
