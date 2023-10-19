#!/usr/bin/python3
# -*- coding: utf-8 -*-
from collections import Counter
from glob import glob
import json
import logging
import os
from pathlib import Path
import random
import re
import shutil
import sqlite3
from typing import List, Tuple
import time

from cacheout import Cache
import pandas as pd
import requests
from tqdm import tqdm

from project_settings import project_path
from server.annotation_server import settings
from server.annotation_server.misc.constant import Tasks
from server.annotation_server.misc.constant.basic_intent import AnnotateMode, RecommendMode
from server.annotation_server.misc.sqlite_tables import TBasicIntent, TAnnotatorWorkload
from server.annotation_server.misc.sqlite_connect import SqliteConnect
from server.exception import ExpectedError
from toolbox.string.sqlite_escape import escape_string


logger = logging.getLogger('server')

sqlite_connect = SqliteConnect(database=settings.sqlite_database)
t_annotator_workload = TAnnotatorWorkload(sqlite_connect=sqlite_connect)
t_basic_intent = TBasicIntent(sqlite_connect=sqlite_connect)
cache = Cache(maxsize=256, ttl=1*60*60, timer=time.time)


class TrainerPlatform(object):
    def __init__(self):
        pass

    @staticmethod
    def post_basic_intent_by_language(language: str, text: str):
        url = 'http://{host}:{port}/basic_intent_by_language'.format(
            host=settings.training_platform_host,
            port=settings.training_platform_port,
        )

        headers = {
            'Content-Type': 'application/json'
        }

        data = {
            'language': language,
            'text': text,
        }

        resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=2)
        if resp.status_code != 200:
            logger.info('basic_intent_by_language failed. resp text: {}'.format(resp.text))
            return None
        js = resp.json()
        if js['status_code'] != 60200:
            return None

        # {'label': '', 'prob': ''}
        return js['result']

    @staticmethod
    def post_model_info(language: str) -> dict:
        url = 'http://{host}:{port}/basic_intent_by_language_pivot_table'.format(
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


class DownloadN(object):
    def __init__(self):
        pass

    @classmethod
    def download_n(cls, username, language, annotate_mode, recommend_mode, n: int):
        if annotate_mode == AnnotateMode.correction:
            rows = cls._download_n_correction(username, language, annotate_mode, recommend_mode, n)
        elif annotate_mode == AnnotateMode.relabel:
            rows = cls._download_n_relabel(username, language, annotate_mode, recommend_mode, n)
        elif recommend_mode == RecommendMode.random:
            rows = cls._download_n_random(username, language, annotate_mode, recommend_mode, n)
        else:
            rows = cls._download_n_non_random(username, language, annotate_mode, recommend_mode, n)

        return rows

    @classmethod
    def _download_n_random(cls, username, language, annotate_mode, recommend_mode, n: int):
        sql = """
SELECT * FROM BasicIntent WHERE finish==0 AND language=='{language}' LIMIT 1000;
        """.format(language=language).strip().replace('\n', ' ')
        logger.debug('sql: {}'.format(sql))
        rows = t_basic_intent.sqlite_connect.execute(sql)

        if len(rows) == 0:
            raise ExpectedError(status_code=60505, message='no unfinished audio any more')

        # row[7]: prob
        rows_ = [row for row in rows if (row[7] is not None and row[7] < 0.9)]
        if len(rows_) == 0:
            rows_ = [row for row in rows if row[7] is None]
        rows = random.sample(rows_, k=n)

        return rows

    @classmethod
    def _download_n_non_random(cls, username, language, annotate_mode, recommend_mode, n: int):
        sql = """
SELECT * FROM BasicIntent WHERE finish==0 AND language=='{language}' AND predict=='{predict}' LIMIT 1000;
        """.format(
            language=language,
            predict=recommend_mode
        ).strip().replace('\n', ' ')
        logger.debug('sql: {}'.format(sql))
        rows = t_basic_intent.sqlite_connect.execute(sql)

        if len(rows) != 0:
            try:
                rows = random.sample(rows, k=n)
            except ValueError:
                rows = rows
        else:
            # random.
            rows = cls._download_n_random(username, language, annotate_mode, recommend_mode, n)
        return rows

    @classmethod
    def _download_n_correction(cls, username, language, annotate_mode, recommend_mode, n: int):
        sql = """
SELECT * FROM BasicIntent WHERE language='{language}' AND finish==1 AND checked==0 AND correct==0 LIMIT 1000;
        """.format(language=language).strip().replace('\n', ' ')

        logger.debug('sql: {}'.format(sql))
        rows = t_basic_intent.sqlite_connect.execute(sql)

        if len(rows) != 0:
            try:
                rows = random.sample(rows, k=n)
            except ValueError:
                rows = rows
        else:
            # random
            rows = cls._download_n_random(username, language, annotate_mode, recommend_mode, n)
        return rows

    @classmethod
    def _download_n_relabel(cls, username, language, annotate_mode, recommend_mode, n: int):
        sql = """
SELECT * FROM BasicIntent WHERE language='{language}' AND label=='{label}' LIMIT 1000;
        """.format(language=language, label=recommend_mode).strip().replace('\n', ' ')

        logger.debug('sql: {}'.format(sql))
        rows = t_basic_intent.sqlite_connect.execute(sql)

        if len(rows) != 0:
            try:
                rows = random.sample(rows, k=n)
            except ValueError:
                rows = rows
        else:
            # random
            rows = cls._download_n_random(username, language, annotate_mode, recommend_mode, n)
        return rows


# ----------------- service -----------------

def get_choice_of_language():
    sql = """
    SELECT DISTINCT language FROM BasicIntent;
    """.strip().replace('\n', ' ')
    sql = re.sub(pattern=r'\s{4,}', repl=' ', string=sql)

    logger.debug('sql: {}'.format(sql))
    rows = t_basic_intent.sqlite_connect.execute(sql)

    result = list()
    for row in rows:
        result.append(row[0])

    result = list(sorted(result))
    return result


def get_choice_of_label(language: str) -> List[str]:
    sql = """
    SELECT DISTINCT label FROM BasicIntent WHERE language=='{language}' AND finish==1;
    """.format(language=language).strip().replace('\n', ' ')
    sql = re.sub(pattern=r'\s{4,}', repl=' ', string=sql)

    logger.debug('sql: {}'.format(sql))
    rows = t_basic_intent.sqlite_connect.execute(sql)

    result = list()
    for row in rows:
        result.append(row[0])

    result = list(sorted(result))
    return result


def get_choice_of_recommend_mode(language: str):
    result = [RecommendMode.random, *get_choice_of_label(language)]
    return result


def get_annotator_workload(username: str, language: str):
    result = list()
    thead = t_annotator_workload.columns
    thead.pop(2)
    result.append(thead)

    rows = t_annotator_workload.get_workload_by_annotator(username, task=Tasks.basic_intent, language=language)

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
    key = 'get_labels_count_{}'.format(language.lower())
    value = cache.get(key)
    if value is not None:
        return value

    result = [('label', 'count')]

    # from sqlite
    counter = t_basic_intent.get_labels_count(language)
    data = counter.items()

    # from pandas
    # language = str(language).lower()
    # filename = os.path.join(project_path, settings.server_dir, 'static',
    #                         settings.basic_intent_datasets_dir, language,
    #                         settings.basic_intent_datasets_fn)
    #
    # df = pd.read_excel(filename)
    # df = df[df['selected'] == 1]
    # labels = df['label1'].tolist()
    # counter = Counter()
    # counter.update(labels)
    # data = dict(counter).items()

    data = list(sorted(data, key=lambda x: x[1], reverse=True))
    result.extend(data)

    cache.set(key, value)
    return result


def get_model_info(language: str):
    return TrainerPlatform.post_model_info(language)


def download_n(username, language, annotate_mode, recommend_mode, n):
    rows = DownloadN.download_n(username, language, annotate_mode, recommend_mode, n)

    rows = [
        {
            'text': row[0],
            'label': '',
        }
        for row in rows
    ]

    return rows


def annotate_n(username, language, annotates: List[dict]):

    count = 0
    for annotate in annotates:
        text = annotate['text']
        label = annotate['label']
        if len(label) == 0:
            continue
        count += 1

        t_basic_intent.annotate_n(
            text=text,
            language=language,
            annotator=username,
            label=label,
        )

    # workload
    t_annotator_workload.update_annotator_workload(
        username=username,
        task=Tasks.basic_intent,
        language=language,
        increase_count=count,
    )
    return annotates


def predict_by_language(language: str, text: str) -> dict:
    outputs = TrainerPlatform.post_basic_intent_by_language(language, text)

    label = outputs['label']
    prob = outputs['prob']

    label = str(label).strip().split('_')[-1]

    sql = """
    UPDATE BasicIntent 
    SET predict='{predict}', prob={prob}
    WHERE text='{text}' AND language='{language}';
    """.format(
            text=escape_string(text),
            language=language,
            predict=label,
            prob=prob,
        ).strip().replace('\n', ' ')
    sql = re.sub(pattern=r'\s{4,}', repl=' ', string=sql)
    logger.debug('sql: {}'.format(sql))
    sqlite_connect.execute(sql, commit=True)

    result = {
        'label': label,
        'prob': prob
    }
    return result


# ----------------- scheduler tasks -----------------
def task_basic_intent_update_from_excel_to_sqlite_db():
    sqlite_database = sqlite3.connect(settings.sqlite_database)

    filename_pattern1 = os.path.join(project_path, settings.server_dir, 'static',
                                     settings.basic_intent_datasets_dir, '*',
                                     settings.basic_intent_datasets_fn)

    filename_list = glob(filename_pattern1)
    for filename in tqdm(filename_list):
        filename = Path(filename)

        language = filename.parts[-2]

        df = pd.read_excel(filename.as_posix())
        for i, row in tqdm(df.iterrows(), total=len(df)):
            text = row['text']
            label1 = row['label1']
            selected = row['selected']
            checked = row['checked']

            if pd.isna(text):
                continue
            text = str(text)
            if len(str(text).strip()) == 0:
                continue
            if pd.isna(label1):
                label1 = None
            if pd.isna(selected):
                selected = 0
            if pd.isna(checked):
                checked = 0

            # insert when not exist
            try:
                sql = """
                SELECT * FROM BasicIntent WHERE text='{text}' AND language='{language}';
                """.format(text=escape_string(text), language=language).strip().replace('\n', ' ')
                sql = re.sub(pattern=r'\s{4,}', repl=' ', string=sql)
                logger.debug('sql: {}'.format(sql))
                cursor = sqlite_database.execute(sql)
                data = cursor.fetchall()
                if len(data) != 0:
                    # logger.debug('skip: {}'.format(text))
                    continue

                if label1 is None:
                    sql = """
                    INSERT INTO BasicIntent (text, language, finish, checked)
                    VALUES ('{text}', '{language}', {finish}, {checked})
                    """.format(text=escape_string(text),
                               language=language,
                               finish=0,
                               checked=0,
                               ).strip().replace('\n', ' ')
                else:
                    sql = """
                    INSERT INTO BasicIntent (text, language, finish, checked, label)
                    VALUES ('{text}', '{language}', {finish}, {checked}, '{label}')
                    """.format(text=escape_string(text),
                               language=language,
                               finish=selected,
                               checked=checked,
                               label=label1,
                               ).strip().replace('\n', ' ')
                sql = re.sub(r'[\u0020]{4,}', ' ', sql)
                logger.debug('sql: {}'.format(sql))

                sqlite_database.execute(sql)

            except Exception as e:
                logger.error('task_basic_intent_update_from_excel_to_sqlite_db; error: {}'.format(str(e)))
                continue

            if i > 0 and i % 10000 == 0:
                sqlite_database.commit()

    sqlite_database.commit()
    sqlite_database.close()
    return


def task_basic_intent_update_from_sqlite_db_to_excel():
    sqlite_database = sqlite3.connect(settings.sqlite_database)

    filename_pattern1 = os.path.join(project_path, settings.server_dir, 'static',
                                     settings.basic_intent_datasets_dir, '*',
                                     settings.basic_intent_datasets_fn)

    filename_list = glob(filename_pattern1)
    for filename in tqdm(filename_list):
        filename = Path(filename)

        language = filename.parts[-2]

        df = pd.read_excel(filename.as_posix())
        new_df = list()
        for i, row in tqdm(df.iterrows(), total=len(df)):
            text = row['text']

            if pd.isna(text):
                continue
            text = str(text)
            if len(str(text).strip()) == 0:
                continue

            # query
            try:
                sql = """
                SELECT * FROM BasicIntent WHERE text='{text}' AND language='{language}';
                """.format(text=escape_string(text), language=language).strip().replace('\n', ' ')
                sql = re.sub(pattern=r'\s{4,}', repl=' ', string=sql)
                logger.debug('sql: {}'.format(sql))

                cursor = sqlite_database.execute(sql)
                data = cursor.fetchall()

                row = dict(row)
                if len(data) == 0:
                    new_df.append(row)
                else:
                    data = data[0]
                    # text, language, finish, checked, annotator, label, predict, prob, correct
                    text, _, finish, checked, _, label, _, _, _ = data

                    row['text'] = text
                    row['selected'] = finish
                    row['checked'] = checked
                    row['label0'] = '相关领域' if label != '无关领域' or len(label) != 0 or label is None else '无关领域'
                    row['label1'] = label
                    new_df.append(row)

            except (UnicodeEncodeError,) as e:
                logger.error('task_basic_intent_update_from_sqlite_db_to_excel; error: {}'.format(str(e)))
                continue

        path, fn = os.path.split(filename.as_posix())
        basename, _ = os.path.splitext(fn)
        backup_filename = os.path.join(path, '{}_backup.xlsx'.format(basename))
        shutil.move(filename.as_posix(), backup_filename)
        new_df = pd.DataFrame(new_df)
        new_df = pd.concat([new_df, df], axis=0, ignore_index=True)
        new_df.drop_duplicates(subset=['text'], keep='first', inplace=True, ignore_index=True)
        new_df.to_excel(filename.as_posix(), index=False, encoding='utf_8_sig')

    sqlite_database.close()

    return


def task_basic_intent_predict_info_update_to_sqlite_db():
    sqlite_database = sqlite3.connect(settings.sqlite_database)

    for language in ['chinese', 'language']:
        sql = """
SELECT * FROM BasicIntent WHERE language='{language}' LIMIT 20000;
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
            text = row[0]
            language = row[1]

            outputs = TrainerPlatform.post_basic_intent_by_language(language, text)
            if outputs is None:
                continue
            label = outputs['label']
            label = str(label).strip().split('_')[-1]
            prob = outputs['prob']

            sql = """
UPDATE BasicIntent SET predict='{predict}', prob={prob} WHERE text='{text}' AND language='{language}';
        """.format(
                text=text,
                language=language,
                predict=label,
                prob=prob,
            ).strip().replace('\n', ' ')
            logger.debug('sql: {}'.format(sql))
            _ = sqlite_database.execute(sql)

    sqlite_database.commit()
    sqlite_database.close()
    return


if __name__ == '__main__':
    pass
