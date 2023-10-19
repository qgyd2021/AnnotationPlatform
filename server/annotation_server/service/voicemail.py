#!/usr/bin/python3
# -*- coding: utf-8 -*-
import base64
from glob import glob
import json
import logging
import os
from pathlib import Path
import random
import shutil
import sqlite3
import time
from typing import List, Tuple

import cv2
import librosa
import requests
from tqdm import tqdm

from project_settings import project_path
from server.annotation_server import settings
from server.exception import ExpectedError
from toolbox.python_speech_features.misc import wave2spectrum_image
from server.annotation_server.misc.sqlite_tables import TVoicemail, TAnnotatorWorkload
from server.annotation_server.misc.constant import Tasks
from server.annotation_server.misc.constant.voicemail import AnnotateMode, RecommendMode
from server.annotation_server.misc.sqlite_connect import SqliteConnect

logger = logging.getLogger('server')


sqlite_connect = SqliteConnect(database=settings.sqlite_database)
t_annotator_workload = TAnnotatorWorkload(sqlite_connect=sqlite_connect)
t_voicemail = TVoicemail(sqlite_connect=sqlite_connect)


class TrainerPlatform(object):
    def __init__(self):
        pass

    @staticmethod
    def post_predict_info_by_language(filename: str, language: str) -> dict:
        url = 'http://{host}:{port}/cnn_voicemail_by_language'.format(
            host=settings.training_platform_host,
            port=settings.training_platform_port,
        )

        headers = {
            'Content-Type': 'application/json'
        }

        try:
            with open(filename, 'rb') as f:
                data = f.read()
        except FileNotFoundError:
            return None

        base64string = base64.b64encode(data).decode('utf-8')

        data = {
            'language': language,
            'signal': base64string,
        }

        resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=2)
        if resp.status_code != 200:
            return None
        js = resp.json()
        if js['status_code'] != 60200:
            return None

        return js['result']

    @staticmethod
    def post_predict_info(filename: str, language: str) -> List[dict]:
        url = 'http://{host}:{port}/cnn_voicemail'.format(
            host=settings.training_platform_host,
            port=settings.training_platform_port,
        )

        headers = {
            'Content-Type': 'application/json'
        }

        try:
            with open(filename, 'rb') as f:
                data = f.read()
        except FileNotFoundError:
            return None

        base64string = base64.b64encode(data).decode('utf-8')

        data = {
            'language': language,
            'signal': base64string,
        }

        resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=2)
        if resp.status_code != 200:
            return None
        js = resp.json()
        if js['status_code'] != 60200:
            return None

        return js['result']

    @staticmethod
    def post_model_info(language: str) -> dict:
        url = 'http://{host}:{port}/cnn_voicemail_by_language_pivot_table'.format(
            host=settings.training_platform_host,
            port=settings.training_platform_port,
        )

        headers = {
            'Content-Type': 'application/json'
        }

        data = {
            'language': language,
        }

        resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=2)
        if resp.status_code != 200:
            return None
        js = resp.json()
        if js['status_code'] != 60200:
            return None

        return js['result']

    @staticmethod
    def post_correction(language: str):
        url = 'http://{host}:{port}/cnn_voicemail_correction'.format(
            host=settings.training_platform_host,
            port=settings.training_platform_port,
        )

        headers = {
            'Content-Type': 'application/json'
        }

        data = {
            'language': language,
        }

        resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=2)
        if resp.status_code != 200:
            return None
        js = resp.json()
        if js['status_code'] != 60200:
            return None

        return js['result']


class VoicemailFilename(object):

    @classmethod
    def _check_abs_filename(cls, abs_filename: str, finished: bool = None):
        abs_filename_ = Path(abs_filename)
        if not abs_filename_.as_posix().__contains__('static/datasets/voicemail'):
            raise AssertionError('this is not a voicemail filename')
        static_audio_filename = abs_filename_.as_posix().split('static/')[-1]
        cls._check_static_audio_filename(static_audio_filename, finished)

    @classmethod
    def _check_static_audio_filename(cls, static_audio_filename: str, finished: bool = None):
        static_audio_filename = Path(static_audio_filename)
        if len(static_audio_filename.parts) not in (4, 6):
            raise AssertionError('voicemail filename with not expected parts length: {}'.format(
                len(static_audio_filename.parts)))
        if finished is not None:
            cls._check_finished_by_static_audio_filename(static_audio_filename, finished)

    @classmethod
    def _check_finished_by_static_audio_filename(cls, static_audio_filename: str, finished: bool = False):
        static_audio_filename = Path(static_audio_filename)

        if finished and len(static_audio_filename.parts) != 6:
            raise AssertionError(
                'this voicemail filename may not finished. filename: {}, finished: {}'.format(
                    static_audio_filename.as_posix(), finished))

        if not finished and len(static_audio_filename.parts) != 4:
            raise AssertionError(
                'this voicemail filename may not finished. filename: {}, finished: {}'.format(
                    static_audio_filename.as_posix(), finished))

    def __init__(self, abs_filename: str, finished: bool = False):
        self.abs_filename = Path(abs_filename)
        self.finished = bool(finished)

        # property
        self._language = None
        self._task_name = None
        self._static_audio_filename = None
        self._static_spectrum_filename = None

        # check
        self._check_abs_filename(abs_filename, finished)

    def as_posix(self):
        return self.abs_filename.as_posix()

    @classmethod
    def from_static_audio_filename(cls, static_audio_filename: str):
        cls._check_static_audio_filename(static_audio_filename)

        static_audio_filename = Path(static_audio_filename)
        if len(static_audio_filename.parts) == 4:
            finished = False
        elif len(static_audio_filename.parts) == 6:
            finished = True
        else:
            raise AssertionError

        abs_filename = os.path.join(
            project_path, settings.server_dir, 'static',
            static_audio_filename
        )

        return VoicemailFilename(abs_filename, finished)

    @property
    def static_image_dir(self) -> Path:
        return Path(settings.images_directory)

    @property
    def voicemail_dataset_dir(self):
        return

    @property
    def name(self):
        return self.abs_filename.name

    @property
    def basename(self):
        return self.abs_filename.stem

    @property
    def language(self):
        if self._language is None:
            if self.finished:
                self._language = self.abs_filename.parts[-4]
            else:
                self._language = self.abs_filename.parts[-2]
        return self._language

    @property
    def task_name(self):
        if self._task_name is None:
            if self.finished:
                self._task_name = self.abs_filename.parts[-5]
            else:
                self._task_name = self.abs_filename.parts[-3]
        return self._task_name

    @property
    def label(self) -> str:
        if self.finished:
            return self.abs_filename.parts[-2]
        else:
            return 'null'

    @property
    def static_audio_filename(self) -> str:
        if self._static_audio_filename is None:
            if self.finished:
                self._static_audio_filename = '/'.join(self.abs_filename.parts[-6:])
            else:
                self._static_audio_filename = '/'.join(self.abs_filename.parts[-4:])
        return self._static_audio_filename

    @property
    def static_spectrum_filename(self) -> str:
        if self._static_spectrum_filename is None:
            signal, sample_rate = librosa.load(self.abs_filename, sr=8000)

            spectrum_image = wave2spectrum_image(signal, sample_rate=8000, nfft=256)
            spectrum_image = spectrum_image.T
            spectrum_image = spectrum_image[:200]

            images_path = self.static_image_dir / '{}/{}'.format(self.task_name, self.language)
            images_path.mkdir(parents=True, exist_ok=True)

            image_filename = images_path / '{}.jpg'.format(self.basename)
            cv2.imwrite(str(image_filename), spectrum_image)

            self._static_spectrum_filename = os.path.join('images/{}/{}/{}.jpg'.format(
                self.task_name, self.language, self.basename)
            )
        return self._static_spectrum_filename

    @property
    def static_audio_display_filename(self) -> str:
        return self.abs_filename.name

    def get_finished_abs_filename(self, label: str) -> str:
        finished_abs_filename = project_path / settings.server_dir / 'static' / settings.voicemail_datasets / self.language / 'wav_finished' / label / self.name
        return finished_abs_filename.as_posix()

    @property
    def predict_info(self) -> List[dict]:
        return TrainerPlatform.post_predict_info(self.abs_filename, self.language)

    @property
    def predict_info_by_language(self) -> dict:
        return TrainerPlatform.post_predict_info_by_language(self.abs_filename, self.language)


class DownloadOne(object):
    def __init__(self):
        pass

    @classmethod
    def download_one(cls, username, language, annotate_mode, recommend_mode) -> VoicemailFilename:
        if annotate_mode == AnnotateMode.correction:
            row = cls._download_one_correction(username, language, annotate_mode, recommend_mode)
            filename = VoicemailFilename(row[1], finished=True)
        elif recommend_mode == RecommendMode.random:
            row = cls._download_one_random(username, language, annotate_mode, recommend_mode)
            filename = VoicemailFilename(row[1], finished=False)
        else:
            row = cls._download_one_non_random(username, language, annotate_mode, recommend_mode)
            filename = VoicemailFilename(row[1], finished=False)

        return filename

    @staticmethod
    def _download_one_random(username, language, annotate_mode, recommend_mode):
        sql = """
SELECT * FROM Voicemail WHERE finish==0 AND language='{language}' LIMIT 100;
        """.format(language=language).strip().replace('\n', ' ')
        logger.debug('sql: {}'.format(sql))
        rows = t_voicemail.sqlite_connect.execute(sql)

        if len(rows) == 0:
            raise ExpectedError(status_code=60505, message='no unfinished audio any more')

        rows = random.sample(rows, k=1)
        row = rows[0]

        return row

    @staticmethod
    def _download_one_non_random(username, language, annotate_mode, recommend_mode):
        sql = """
SELECT * FROM Voicemail WHERE finish==0 AND language='{language}' AND predict='{predict}' LIMIT 100;
        """.format(
            language=language,
            predict=recommend_mode
        ).strip().replace('\n', ' ')
        logger.debug('sql: {}'.format(sql))
        rows = t_voicemail.sqlite_connect.execute(sql)

        if len(rows) != 0:
            rows = random.sample(rows, k=1)
            row = rows[0]
            return row

        # limit 3, To avoid annotator waiting.
        sql = """
    SELECT * FROM Voicemail WHERE finish==0 AND language='{language}' AND predict is null LIMIT 3;
        """.format(
            language=language,
            predict=recommend_mode
        ).strip().replace('\n', ' ')
        logger.debug('sql: {}'.format(sql))
        rows = t_voicemail.sqlite_connect.execute(sql)

        if len(rows) == 0:
            raise ExpectedError(
                status_code=60505,
                message='no unfinished audio for recommend mode: {}'.format(recommend_mode)
            )

        for row in rows:
            filename = row[1]
            path, fn = os.path.split(filename)
            basename, exi = os.path.splitext(fn)

            js = TrainerPlatform.post_predict_info(filename, language)
            predict = js[0]['label']
            prob = js[0]['prob']

            sql = """
    UPDATE Voicemail SET predict='{predict}', prob={prob} WHERE basename='{basename}';
        """.format(
                predict=predict,
                prob=prob,
                basename=basename
            ).strip().replace('\n', ' ')
            _ = t_voicemail.sqlite_connect.execute(sql, commit=True)

        rows = random.sample(rows, k=1)
        row = rows[0]
        return row

    @staticmethod
    def _download_one_correction(username, language, annotate_mode, recommend_mode):
        sql = """
SELECT * FROM Voicemail WHERE language='{language}' AND finish==1 AND checked==0 AND correct==0 LIMIT 100;
        """.format(language=language).strip().replace('\n', ' ')

        logger.debug('sql: {}'.format(sql))
        rows = t_voicemail.sqlite_connect.execute(sql)

        if len(rows) != 0:
            rows = random.sample(rows, k=1)
            row = rows[0]
            return row

        # limit 3, To avoid annotator waiting.
        sql = """
SELECT * FROM Voicemail WHERE language='{language}' AND finish==1 AND checked==0 AND correct is null LIMIT 100;
        """.format(language=language).strip().replace('\n', ' ')
        logger.debug('sql: {}'.format(sql))
        rows = t_voicemail.sqlite_connect.execute(sql)

        if len(rows) == 0:
            raise ExpectedError(status_code=60505, message='no finished audio need to check correction')

        for row in rows:
            filename = row[1]
            label = row[6]
            path, fn = os.path.split(filename)
            basename, exi = os.path.splitext(fn)

            js = TrainerPlatform.post_predict_info(filename, language)
            predict = js[0]['label']
            prob = js[0]['prob']

            sql = """
UPDATE Voicemail SET predict='{predict}', prob={prob}, correct={correct} WHERE basename='{basename}';
        """.format(
                predict=predict,
                prob=prob,
                correct=1 if predict == label else 0,
                basename=basename
            ).strip().replace('\n', ' ')
            _ = t_voicemail.sqlite_connect.execute(sql, commit=True)

        rows = random.sample(rows, k=1)
        row = rows[0]
        return row


# ----------------- service -----------------

def get_choice_of_language():
    sql = """
SELECT DISTINCT language FROM Voicemail WHERE finish==0;
    """.strip().replace('\n', ' ')
    logger.debug('sql: {}'.format(sql))
    rows = t_voicemail.sqlite_connect.execute(sql)

    result = list()
    for row in rows:
        result.append(row[0])
    return result


def download_one(username, language, annotate_mode, recommend_mode):
    unfinished_filename = DownloadOne.download_one(username, language, annotate_mode, recommend_mode)

    result = {
        'audio_filename': unfinished_filename.static_audio_filename,
        'image_filename': unfinished_filename.static_spectrum_filename,
        'audio_display_name': unfinished_filename.static_audio_display_filename,
        'predict_info': unfinished_filename.predict_info
    }
    return result


def annotate_one(username, static_audio_filename, label, language):
    voicemail_filename = VoicemailFilename.from_static_audio_filename(
        static_audio_filename=static_audio_filename
    )

    abs_new_filename = voicemail_filename.get_finished_abs_filename(label)

    t_voicemail.annotate_one(
        basename=voicemail_filename.basename,
        new_filename=abs_new_filename,
        annotator=username,
        label=label,
        checked=1 if voicemail_filename.finished else 0
    )
    _ = t_annotator_workload.update_annotator_workload(
        username, task=Tasks.voicemail, language=language, increase_count=1)

    os.makedirs(os.path.split(abs_new_filename)[0], exist_ok=True)
    shutil.move(voicemail_filename.abs_filename, abs_new_filename)
    return VoicemailFilename(abs_new_filename, finished=True).static_audio_filename


def get_annotator_workload(username, language):
    result = list()
    thead = t_annotator_workload.columns
    thead.pop(2)
    result.append(thead)

    rows = t_annotator_workload.get_workload_by_annotator(username, task=Tasks.voicemail, language=language)

    now = time.localtime(time.time())
    now = time.mktime(now)
    for row in rows:
        row = list(row)
        datetime = row[1]
        datetime = time.strptime(datetime, "%Y-%m-%d")
        datetime = time.mktime(datetime)

        delta_time = now - datetime
        delta_time = time.gmtime(delta_time)

        # 只展示最近 7 天的.
        if delta_time.tm_mday > 8:
            continue

        row.pop(2)
        result.append(row)
    return result


def get_labels_count(language: str) -> List[Tuple[str, int]]:
    counter = t_voicemail.get_labels_count(language)

    result = [('label', 'count')]
    result.extend(counter.items())
    return result


def get_model_info(language):
    return TrainerPlatform.post_model_info(language)


# ----------------- scheduler tasks -----------------
def task_voicemail_filename_update_to_sqlite_db():
    sqlite_database = sqlite3.connect(settings.sqlite_database)

    filename_list = list()

    filename_pattern1 = os.path.join(project_path, settings.server_dir, 'static',
                                     settings.voicemail_datasets, '*/*.wav')
    filename_list1 = glob(filename_pattern1)
    filename_list.extend(zip(filename_list1, [0] * len(filename_list1)))

    filename_pattern2 = os.path.join(project_path, settings.server_dir, 'static',
                                     settings.voicemail_datasets, '*/wav_finished/*/*.wav')
    filename_list2 = glob(filename_pattern2)
    filename_list.extend(zip(filename_list2, [1] * len(filename_list2)))

    logger.debug('filename_pattern1: {}'.format(filename_pattern1))
    logger.debug('filename_pattern2: {}'.format(filename_pattern2))

    count = 0
    for filename, finished in tqdm(filename_list):
        filename = VoicemailFilename(filename, finished=bool(finished))

        # insert when not exist
        sql = """
SELECT * FROM Voicemail WHERE basename='{basename}' AND language='{language}';
""".format(basename=filename.basename, language=filename.language).strip().replace('\n', ' ')
        logger.debug('sql: {}'.format(sql))
        cursor = sqlite_database.execute(sql)
        data = cursor.fetchall()
        if len(data) != 0:
            logger.debug('skip: {}'.format(filename.basename))
            continue

        sql = """
INSERT INTO Voicemail (basename, filename, language, finish, checked, label)
VALUES ('{basename}', '{filename}', '{language}', {finish}, {checked}, '{label}')
""".format(basename=filename.basename,
           filename=filename.as_posix(),
           language=filename.language,
           finish=int(filename.finished),
           checked=0,
           label=filename.label,
           ).strip().replace('\n', ' ')
        logger.debug('sql: {}'.format(sql))
        try:
            sqlite_database.execute(sql)
        except sqlite3.IntegrityError as e:
            logger.error('error: {}'.format(str(e)))
            continue

        if count % 10000 == 0:
            sqlite_database.commit()
        count += 1
    sqlite_database.commit()
    sqlite_database.close()
    return


def task_voicemail_predict_info_update_to_sqlite_db():
    sqlite_database = sqlite3.connect(settings.sqlite_database)

    for language in ['es-MX', 'id-ID', 'en-PH', 'en-IN']:
        sql = """
SELECT * FROM Voicemail WHERE language='{language}';
        """.format(language=language).strip().replace('\n', ' ')

        logger.debug('sql: {}'.format(sql))
        cursor = sqlite_database.execute(sql)
        rows = cursor.fetchall()

        logger.debug('len(rows): {}'.format(len(rows)))

        if len(rows) == 0:
            return

        if len(rows) > 5000:
            rows = random.sample(rows, k=5000)
        for row in tqdm(rows):
            filename = row[1]
            finish = row[3]
            filename = VoicemailFilename(filename, finished=finish)
            if filename.predict_info is None:
                continue

            sql = """
UPDATE Voicemail SET predict='{predict}', prob={prob} WHERE basename='{basename}';
        """.format(
                predict=filename.predict_info[0]['label'],
                prob=filename.predict_info[0]['prob'],
                basename=filename.basename
            ).strip().replace('\n', ' ')
            logger.debug('sql: {}'.format(sql))
            _ = sqlite_database.execute(sql)

    sqlite_database.commit()
    sqlite_database.close()
    return


if __name__ == '__main__':
    pass
