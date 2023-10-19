#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import os
import sqlite3
from typing import List

from project_settings import project_path
from toolbox.os.environment import EnvironmentManager

log_directory = os.path.join(project_path, 'server/annotation_server/logs')
os.makedirs(log_directory, exist_ok=True)

images_directory = os.path.join(project_path, 'server/annotation_server/static/images')
os.makedirs(images_directory, exist_ok=True)

environment = EnvironmentManager(
    path=os.path.join(project_path, 'server/annotation_server/dotenv'),
    env=os.environ.get('environment', 'dev'),
)

port = environment.get(key='port', default=9080, dtype=int)

server_dir = environment.get(key='server_dir', default='server/annotation_server', dtype=str)

sqlite_database = environment.get(
    key='sqlite_database',
    # default='sqlite.db',
    default=os.path.join(project_path, server_dir, 'sqlite.db'),
    dtype=str
)


# task voicemail
voicemail_datasets = environment.get(key='voicemail_datasets', default='datasets/voicemail', dtype=str)
wav_finished_dir_name = environment.get(key='wav_finished_dir_name', default='wav_finished', dtype=str)


# task basic intent
basic_intent_datasets_dir = environment.get(
    key='basic_intent_datasets_dir', default='datasets/basic_intent', dtype=str)
basic_intent_datasets_fn = environment.get(
    key='basic_intent_datasets_fn', default='dataset.xlsx', dtype=str)


# training platform
training_platform_host = environment.get(key='training_platform_host', default='10.75.27.247', dtype=str)
training_platform_port = environment.get(key='training_platform_port', default=9180, dtype=int)

# bark tts
bark_tts_host = environment.get(key='bark_tts_host', default='10.75.27.247', dtype=str)
bark_tts_port = environment.get(key='bark_tts_port', default=9280, dtype=int)


if __name__ == '__main__':
    pass
