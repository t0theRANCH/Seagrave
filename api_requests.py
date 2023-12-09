import base64
import json

import requests

from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar

from requests.exceptions import ConnectionError, HTTPError, Timeout, TooManyRedirects, RequestException


def connection(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ConnectionError, HTTPError, Timeout, TooManyRedirects, RequestException) as e:
            MDSnackbar(
                MDLabel(
                    text='Connection Error'
                )
            ).open()
            return {'error': 'Connection Error',
                    'body': 'Connection Error'}

    return wrapper


api_url = 'https://1tapy3c6x8.execute-api.us-east-2.amazonaws.com'
stage = 'test'


@connection
def secure_request(id_token, data, url=api_url):
    headers = {'token': id_token}
    r = requests.post(f"{url}/{stage}/check_credentials",
                      data=json.dumps(data), headers=headers)
    return r.json()


@connection
def open_request(name, data, url=api_url, auth=None):
    if auth:
        r = requests.post(f"{url}/{stage}/{name}",
                          data=json.dumps(data), headers={'token': auth})
    else:
        r = requests.post(f"{url}/{stage}/{name}",
                          data=json.dumps(data))
    return r.json()


@connection
def old_upload(path, id_token, url):
    with open(path, "rb") as f:
        im_bytes = f.read()
    im_b64 = base64.b64encode(im_bytes).decode("utf8")
    file_dict = {"name": path.split('/')[-1], "file": im_b64}
    return secure_request(id_token, file_dict, url)


@connection
def upload(path, local_path, id_token, url, access_token):
    file_path = path.split('/')
    if file_path[-1] in ['forms.json', 'undeletable.json', 'today.json']:
        upload_path = file_path[-1]
    else:
        upload_path = path
    data = {'AccessToken': access_token,
            'function_name': 'upload',
            'path': upload_path
            }
    upload_file(data, id_token, url, local_path)


@connection
def upload_file(data, id_token, url, local_path):
    if not (
            upload_url := secure_request(data=data, id_token=id_token, url=url)
    ):
        return
    with (open(local_path, "rb") as f):
        r = requests.put(upload_url, data=f)


@connection
def download(url, id_token, access_token, dl_list):
    for read_path, write_path in dl_list.items():
        data = {'path': read_path, 'function_name': 'download', 'AccessToken': access_token}
        download_file(data, id_token, url, write_path)


@connection
def download_file(data, id_token, url, write_path):
    if download_url := secure_request(
            data=data, id_token=id_token, url=url
    ):
        response = requests.get(download_url)
        with open(write_path, "wb") as f:
            f.write(response.content)


@connection
def download_update(url, destination):
    response = requests.get(url)
    response.raise_for_status()

    with open(destination, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
