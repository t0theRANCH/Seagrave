import base64
import json
import re

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
def secure_request(name, id_token, data, url=api_url):
    r = requests.post(f"{url}/{stage}/{name}",
                      data=json.dumps(data), headers={'token': id_token})
    return r.json()


@connection
def open_request(name, data, url=api_url):
    r = requests.post(f"{url}/{stage}/{name}",
                      data=json.dumps(data))
    return r.json()


@connection
def upload(path, id_token, url):
    with open(path, "rb") as f:
        im_bytes = f.read()
    im_b64 = base64.b64encode(im_bytes).decode("utf8")
    file_dict = {"name": path.split('/')[-1], "file": im_b64}
    r = requests.post(f"{url}/{stage}/upload",
                      data=json.dumps(file_dict), headers={'token': id_token})
    return r.json()


@connection
def download(url, id_token, access_token, folder, title, dl_list=None):
    if dl_list:
        dl_list.append('flha.pdf')
        for dl in dl_list:
            if re.search("^forms.json$", dl) or re.search("^today.json$", dl) or re.search(
                    "^undeletable.json$", dl):
                folder = 'database'
            else:
                folder = 'assets'
                # folder = f"database/{dl.split('-')[0]}"
            data = {'path': dl, 'function_name': 'download', 'AccessToken': access_token}
            if download_url := secure_request(
                name='check_credentials', data=data, id_token=id_token, url=url
            ):
                print(download_url)
                response = requests.get(download_url)
                with open(f"{folder}/{dl}", "wb") as f:
                    f.write(response.content)
        return

    data = {'path': f"{folder}/{title}"}
    r = requests.post(f"{url}/{stage}/download", data=json.dumps(data), headers={'token': id_token})
    with open(f"{folder}/{title}", "wb") as f:
        f.write(r.content)
