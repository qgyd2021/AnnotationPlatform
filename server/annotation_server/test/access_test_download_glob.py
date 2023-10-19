#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
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
        '--pattern',
        # default='D:/Users/tianx/PycharmProjects/AnnotationPlatform/*',
        default='/data/tianxing/PycharmProjects/datasets/voicemail/*/wav_finished/*/*.wav',
        type=str,
    )
    args = parser.parse_args()

    return args


def main():
    args = get_args()

    url = 'http://{host}:{port}/download/glob'.format(
        host=args.host,
        port=args.port,
    )

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'pattern': args.pattern,
    }

    resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=None)
    print(resp.status_code)
    print(resp.text)

    return


if __name__ == '__main__':
    main()
