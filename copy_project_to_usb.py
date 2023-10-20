import os
import shutil


def clear_directory(directory):
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)


def copy_to_usb(destination):
    if not destination.endswith('/'):
        destination += '/'
    items = os.listdir('.')

    items_to_copy = [item for item in items if
                     not (item.startswith('.') or item.startswith('__') or item.endswith('.spec')
                          or item in ['bin', 'venv', 'log.txt'])]

    for item in items_to_copy:
        source_path = os.path.abspath(item)
        destination_path = os.path.join(destination, item)

        if os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path)
        elif os.path.isfile(source_path):
            shutil.copy(source_path, destination_path)


if __name__ == '__main__':
    dest = '/media/tyson/Install mac/Seagrave'
    clear_directory(dest)
    copy_to_usb(dest)
