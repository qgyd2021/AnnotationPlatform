#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import base64
import hashlib
import json
import os
import sys

pwd = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(pwd, '../../../'))

import requests


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host',
        # default='127.0.0.1',
        default='10.75.27.247',

        type=str,
    )
    parser.add_argument(
        '--port',
        default=9080,
        type=int,
    )
    parser.add_argument(
        '--filename',
        default='D:/Users/tianx/PycharmProjects/AnnotationPlatform/install.sh',
        # default='D:/programmer/asr_datasets/voicemail/wav_finished/zh-TW/wav_finished/voicemail/00a1d109-23c2-4b8b-a066-993ac2ae8260_zh-TW_1672210791636.wav',
        type=str,
    )
    args = parser.parse_args()

    return args


def main():
    args = get_args()

    url = 'http://{host}:{port}/download/download'.format(
        host=args.host,
        port=args.port,
    )

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'filename': args.filename,
    }

    resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=None)
    if resp.status_code == 200:
        js = resp.json()

        base64string = js['result']

        data_bytes = base64.b64decode(str(base64string).encode('utf-8'))

        _, fn = os.path.split(args.filename)
        with open(fn, 'wb') as f:
            f.write(data_bytes)

    return


if __name__ == '__main__':
    main()
