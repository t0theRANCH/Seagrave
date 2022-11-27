import base64
import json
import re

import boto3
import requests
from offline_requests import OfflineRequest


def offline_request(name, data):
    r = OfflineRequest(func_string=name, data=data)
    return r.func()


class Requests:

    @staticmethod
    def secure_request(name, id_token, data):
        return offline_request(name, data)
        #r = requests.post(f"https://fv8863t87d.execute-api.us-east-1.amazonaws.com/default/{name}",
        #                     data=json.dumps(data), headers={'token': id_token})
        #return r.json()

    @staticmethod
    def open_request(name, data):
        return offline_request(name, data)
        #r = requests.post(f"https://fv8863t87d.execute-api.us-east-1.amazonaws.com/default/{name}",
        #                     data=json.dumps(data))
        #return r.json()

    @staticmethod
    def upload(path, id_token):
        with open(path, "rb") as f:
            im_bytes = f.read()
        im_b64 = base64.b64encode(im_bytes).decode("utf8")
        file_dict = {"name": path.split('/')[-1], "file": im_b64}
        return offline_request(name='upload', data=file_dict)
        #r = requests.post("https://fv8863t87d.execute-api.us-east-1.amazonaws.com/default/upload",
        #                     data=json.dumps(file_dict), headers={'token': id_token})
        #return r.json()

    @staticmethod
    def download(credentials, folder, title, dl_list=None):
        pass
        """
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
        """