#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import logging
import os
import shutil
import sqlite3
import sys

pwd = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(pwd, '../../../../'))

from tqdm import tqdm

from project_settings import project_path

logger = logging.getLogger(__file__)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--sqlite_database_path',
        default=os.path.join(project_path, 'server/annotation/sqlite.db'),
        type=str,
    )
    parser.add_argument(
        '--language',
        default='id-ID',
        type=str,
    )
    args = parser.parse_args()
    return args


def main():
    # python3 delete_from_voicemail_by_language.py --language zh-TW-on_annotation_platform
    args = get_args()

    sqlite_database_path = args.sqlite_database_path
    language = args.language

    sqlite_database_ = sqlite3.connect(sqlite_database_path)

    sql = """
SELECT COUNT(*) FROM Voicemail WHERE language='{language}';
""".format(language=language, finish=1).strip()
    # logger.info('sql: {}'.format(sql))
    cursor = sqlite_database_.execute(sql)
    rows = cursor.fetchall()
    print(rows)

    # Voicemail:
    sql = """
DELETE FROM Voicemail WHERE language='{language}'
""".format(language=language).strip()
    # logger.info('sql: {}'.format(sql))
    _ = sqlite_database_.execute(sql)
    sqlite_database_.commit()

    sql = """
SELECT COUNT(*) FROM Voicemail WHERE language='{language}';
""".format(language=language, finish=1).strip()
    # logger.info('sql: {}'.format(sql))
    cursor = sqlite_database_.execute(sql)
    rows = cursor.fetchall()
    print(rows)

    return


if __name__ == '__main__':
    main()
