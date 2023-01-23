import base64
import json
import re

import boto3
import requests
from kivymd.uix.snackbar import Snackbar

from requests.exceptions import ConnectionError, HTTPError, Timeout, TooManyRedirects, RequestException

api_url = 'https://1tapy3c6x8.execute-api.us-east-2.amazonaws.com'
stage = 'test'


class Requests:

    @staticmethod
    def connection(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (ConnectionError, HTTPError, Timeout, TooManyRedirects, RequestException) as e:
                Snackbar(text=f'Connection Error: {e}').show()
                return {'error': 'Connection Error'}
        return wrapper

    @staticmethod
    @connection
    def secure_request(name, id_token, data):
        r = requests.post(f"{api_url}/{stage}/{name}",
                          data=json.dumps(data), headers={'token': id_token})
        return r.json()

    @staticmethod
    @connection
    def open_request(name, data):
        r = requests.post(f"{api_url}/{stage}/{name}",
                          data=json.dumps(data))
        return r.json()

    @staticmethod
    @connection
    def upload(path, id_token):
        with open(path, "rb") as f:
            im_bytes = f.read()
        im_b64 = base64.b64encode(im_bytes).decode("utf8")
        file_dict = {"name": path.split('/')[-1], "file": im_b64}
        r = requests.post(f"{api_url}/{stage}/upload",
                          data=json.dumps(file_dict), headers={'token': id_token})
        return r.json()

    @staticmethod
    @connection
    def download(credentials, folder, title, dl_list=None):
        s3 = boto3.client('s3', aws_access_key_id=credentials['aws_access_key_id'],
                          aws_secret_access_key=credentials['aws_secret_access_key'])
        if dl_list:
            for dl in dl_list:
                if re.search("^forms.json$", dl) or re.search("^today.json$", dl) or re.search(
                        "^undeletable.json$", dl):
                    folder = 'database'
                else:
                    folder = f"database/{dl.split('-')[0]}"

                s3.download_file(credentials['bucket'], dl, f"{folder}/{dl}")
        else:
            s3.download_file(credentials['bucket'], title, f"{folder}/{title}")
