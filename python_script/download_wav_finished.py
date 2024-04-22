#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import base64
from collections import defaultdict
from glob import glob
import hashlib
import json
import os
from pathlib import Path
import sys

pwd = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(pwd, "../../../"))

import requests
from tqdm import tqdm


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        # default="127.0.0.1",
        default="10.75.27.247",

        type=str,
    )
    parser.add_argument(
        "--port",
        default=9080,
        type=int,
    )
    parser.add_argument(
        "--pattern",
        # default="E:/Users/tianx/PycharmProjects/AnnotationPlatform/*",
        default="/data/tianxing/PycharmProjects/datasets/voicemail/*/wav_finished/*/*.wav",
        type=str,
    )
    parser.add_argument(
        "--local_wav_finished",
        default="E:/programmer/asr_datasets/voicemail/wav_finished/",
        type=str,
    )
    args = parser.parse_args()

    return args


def main():
    args = get_args()

    local_wav_finished = Path(args.local_wav_finished)

    # local wav finished
    filename_list = local_wav_finished.glob("*/wav_finished/*/*.wav")
    language2label2fn = defaultdict(lambda: defaultdict(list))
    for filename in tqdm(filename_list):
        filename = Path(filename)
        language = filename.parts[-4]
        label = filename.parts[-2]
        fn = filename.parts[-1]

        language2label2fn[language][label].append(fn)

    # linux wav finished
    glob_url = "http://{host}:{port}/download/glob".format(
        host=args.host,
        port=args.port,
    )

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "pattern": args.pattern,
    }

    resp = requests.post(glob_url, headers=headers, data=json.dumps(data), timeout=None)

    js = resp.json()
    filename_list = js["result"]

    download_url = "http://{host}:{port}/download/download".format(
        host=args.host,
        port=args.port,
    )
    for filename in tqdm(filename_list):
        filename = Path(filename)
        language = filename.parts[-4]
        label = filename.parts[-2]
        fn = filename.parts[-1]

        if fn in language2label2fn[language][label]:
            continue

        # print("download filename: {}".format(filename))

        to_path = local_wav_finished / language / "wav_finished" / label
        to_path.mkdir(parents=True, exist_ok=True)
        to_filename = to_path / fn
        data = {
            "filename": filename.as_posix(),
        }

        resp = requests.post(download_url, headers=headers, data=json.dumps(data), timeout=None)
        if resp.status_code == 200:
            js = resp.json()

            base64string = js["result"]

            data_bytes = base64.b64decode(str(base64string).encode("utf-8"))

            with open(to_filename.as_posix(), "wb") as f:
                f.write(data_bytes)
    return


if __name__ == "__main__":
    main()
