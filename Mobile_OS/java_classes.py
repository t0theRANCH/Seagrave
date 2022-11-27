from jnius import autoclass


def FileInputStream():
    return autoclass('java.io.FileInputStream')


def FileOutputStream():
    return autoclass('java.io.FileOutputStream')


def Intent():
    return autoclass('android.content.Intent')


def Settings():
    return autoclass('android.provider.Settings')


def Uri():
    return autoclass('android.net.Uri')


def File():
    return autoclass('java.io.File')


def FileProvider():
    return autoclass('android.support.v4.content.FileProvider')


def OpenableColumns():
    return autoclass('android.provider.OpenableColumns')


def String():
    return autoclass('java.lang.String')


def GCMParameterSpec():
    return autoclass('javax.crypto.spec.GCMParameterSpec')


def KeyGenParameterSpec():
    return autoclass('android.security.keystore.KeyGenParameterSpec$Builder')


def KeyGenerator():
    return autoclass('javax.crypto.KeyGenerator')


def KeyProperties():
    return autoclass('android.security.keystore.KeyProperties')


def Cipher():
    return autoclass('javax.crypto.Cipher')


def KeyStore():
    return autoclass('java.security.KeyStore')
