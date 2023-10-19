#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import logging
import os
import shutil
import sqlite3
import sys

pwd = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(pwd, '../../../../../'))

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
    parser.add_argument(
        '--output_dir',
        default='output_dir',
        type=str,
    )
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    sqlite_database_path = args.sqlite_database_path
    language = args.language
    output_dir = args.output_dir

    sqlite_database_ = sqlite3.connect(sqlite_database_path)
    to_path = os.path.join(output_dir, language)
    os.makedirs(to_path, exist_ok=False)

    # Voicemail:
    sql = """
SELECT * FROM Voicemail WHERE language='{language}' AND finish={finish};
""".format(language=language, finish=1).strip()
    # logger.info('sql: {}'.format(sql))
    cursor = sqlite_database_.execute(sql)
    rows = cursor.fetchall()

    for row in tqdm(rows):
        basename = row[0]
        filename = row[1]
        finish = row[3]
        label = row[6]

        if finish != 1:
            continue

        to_path_temp = os.path.join(to_path, label)
        os.makedirs(to_path_temp, exist_ok=True)
        shutil.move(filename, to_path_temp)
        sql = """
DELETE FROM Voicemail
WHERE basename='{basename}';
""".format(basename=basename).strip()
        sqlite_database_.execute(sql)
        sqlite_database_.commit()

    return


if __name__ == '__main__':
    main()
