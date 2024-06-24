#!/usr/bin/python3
# -*- coding: utf-8 -*-
from collections import Counter
import logging
import re
import sqlite3
import time

from server.annotation_server.misc.sqlite_connect import SqliteConnect
from toolbox.design_patterns.singleton import ParamsSingleton
from toolbox.string.sqlite_escape import escape_string

logger = logging.getLogger(__file__)


class TAnnotatorWorkload(ParamsSingleton):
    def __init__(self, sqlite_connect: SqliteConnect):
        if not self._initialized:
            self.sqlite_connect = sqlite_connect
            self.create_table()
            self._initialized = True

    def create_table(self):
        try:
            sql = """
CREATE TABLE AnnotatorWorkload (
username TEXT, datetime TEXT, task TEXT, language TEXT, count INT
);
""".strip().replace('\n', ' ')
            self.sqlite_connect.execute(sql, commit=True)
        except sqlite3.OperationalError as e:
            if str(e) not in ('table AnnotatorWorkload already exists', ):
                raise e

        return

    @property
    def columns(self):
        result = ['username', 'datetime', 'task', 'language', 'count']
        return result

    def update_annotator_workload(self, username: str, task: str, language: str, increase_count: int = 1):
        local_time = time.localtime(time.time())
        datetime = time.strftime("%Y-%m-%d", local_time)

        sql = """
SELECT * FROM AnnotatorWorkload
WHERE username=='{username}' AND datetime='{datetime}' AND task='{task}' AND language='{language}';
""".format(username=username, datetime=datetime, task=task, language=language).strip().replace('\n', ' ')
        logger.debug('sql: {}'.format(sql))
        rows = self.sqlite_connect.execute(sql)
        if len(rows) == 0:
            count = increase_count
            sql = """
INSERT INTO AnnotatorWorkload (username, datetime, task, language, count)
VALUES ('{username}', '{datetime}', '{task}', '{language}', {count})
""".format(username=username, datetime=datetime, task=task, language=language, count=count).strip().replace('\n', ' ')
        else:
            count = rows[0][4] + increase_count
            sql = """
UPDATE AnnotatorWorkload
SET count={count}
WHERE username=='{username}' AND datetime=='{datetime}' AND task=='{task}' AND language=='{language}';
""".format(count=count, username=username, datetime=datetime, task=task, language=language).strip().replace('\n', ' ')
        _ = self.sqlite_connect.execute(sql, commit=True)

        return count

    def get_workload_by_annotator(self, username: str, task: str, language: str):
        sql = """
SELECT * FROM AnnotatorWorkload
WHERE username=='{username}' AND task=='{task}' AND language=='{language}';
""".format(username=username, task=task, language=language).strip().replace('\n', ' ')
        logger.debug('sql: {}'.format(sql))
        rows = self.sqlite_connect.execute(sql)
        return rows


class TBasicIntent(ParamsSingleton):
    def __init__(self, sqlite_connect: SqliteConnect):
        if not self._initialized:
            self.sqlite_connect = sqlite_connect
            self.create_table()
            self._initialized = True

    def create_table(self):
        try:
            sql = """
CREATE TABLE BasicIntent (
text TEXT, language TEXT, 
finish INT, checked INT, annotator TEXT, 
label TEXT, predict TEXT, prob DOUBLE, correct INT, 
PRIMARY KEY (text, language)
);
""".strip().replace('\n', ' ')
            self.sqlite_connect.execute(sql, commit=True)
        except sqlite3.OperationalError as e:
            if str(e) not in ('table BasicIntent already exists', ):
                raise e
        return

    @property
    def columns(self):
        result = ['text', 'language', 'finish', 'checked', 'annotator',
                  'label', 'predict', 'prob', 'correct']
        return result

    def annotate_n(self,
                   text: str, language: str, annotator: str,
                   label: str,
                   ):
        text = escape_string(text)

        sql = """
SELECT finish FROM BasicIntent 
WHERE text='{text}' AND language=='{language}';
""".format(text=text, language=language).strip().replace('\n', ' ')
        logger.debug('sql: {}'.format(sql))
        rows = self.sqlite_connect.execute(sql)
        if len(rows) == 0:
            sql = """
INSERT INTO BasicIntent (text, language, finish, checked, annotator, label)
VALUES ('{text}', '{language}', {finish}, {checked}, '{annotator}', '{annotator}')
""".format(
                text=text,
                language=language,
                finish=1,
                checked=0,
                annotator=annotator,
                label=label
            ).strip().replace('\n', ' ')
        else:
            finish = rows[0][0]
            checked = 1 if finish == 1 else 0

            sql = """
UPDATE BasicIntent 
SET finish={finish}, checked={checked}, annotator='{annotator}', label='{label}'
WHERE text='{text}' AND language='{language}';
""".format(
                text=text,
                language=language,
                finish=1,
                checked=checked,
                annotator=annotator,
                label=label
            ).strip().replace('\n', ' ')

        logger.debug('sql: {}'.format(sql))
        _ = self.sqlite_connect.execute(sql, commit=True)
        return None

    def get_labels_count(self, language) -> dict:
        sql = """
SELECT label FROM BasicIntent 
WHERE finish={finish} AND language=='{language}';
""".format(finish=1, language=language).strip().replace('\n', ' ')
        sql = re.sub(r'[\u0020]{4,}', ' ', sql)

        logger.debug('sql: {}'.format(sql))
        rows = self.sqlite_connect.execute(sql)

        counter = Counter()
        for row in rows:
            counter.update(row)
        result = dict(counter)
        return result


class TVoicemail(ParamsSingleton):
    def __init__(self, sqlite_connect: SqliteConnect):
        if not self._initialized:
            self.sqlite_connect = sqlite_connect
            self.create_table()
            self._initialized = True

    def create_table(self):
        try:
            sql = """
CREATE TABLE Voicemail (
basename TEXT, 
filename TEXT, language TEXT, 
finish INT, checked INT, annotator TEXT,
label TEXT, predict TEXT, prob DOUBLE, correct INT,
PRIMARY KEY (basename, language)
);
""".strip().replace('\n', ' ')
            self.sqlite_connect.execute(sql, commit=True)
        except sqlite3.OperationalError as e:
            if str(e) not in ('table Voicemail already exists', ):
                raise e
        return

    @property
    def columns(self):
        result = ['basename', 'filename', 'language', 'finish', 'checked',
                  'annotator', 'label', 'predict', 'prob', 'correct']
        return result

    def annotate_one(self, basename, new_filename, annotator, label, checked: int = 0):
        sql = """
UPDATE Voicemail 
SET finish={finish}, filename='{filename}', checked={checked}, annotator='{username}', label='{label}'
WHERE basename=='{basename}';
""".format(
            basename=basename,
            filename=new_filename,
            finish=1,
            checked=checked,
            username=annotator,
            label=label
        ).strip().replace('\n', ' ')
        logger.debug('sql: {}'.format(sql))
        self.sqlite_connect.execute(sql, commit=True)
        return

    def get_labels_count(self, language) -> dict:
        sql = """
SELECT label FROM Voicemail 
WHERE finish={finish} AND language=='{language}';
""".format(finish=1, language=language).strip().replace('\n', ' ')
        logger.debug('sql: {}'.format(sql))
        rows = self.sqlite_connect.execute(sql)

        counter = Counter()
        for row in rows:
            counter.update(row)
        result = dict(counter)
        return result


def demo1():
    from server.annotation_server import settings
    print(settings.sqlite_database)

    sqlite_connect = SqliteConnect(database=settings.sqlite_database)

    t_annotator_workload = TAnnotatorWorkload(sqlite_connect=sqlite_connect)

    rows = t_annotator_workload.get_workload_by_annotator(username='田兴', task='voicemail', language='en-US')
    print(rows)
    return


def demo2():
    import sqlite3
    sqlite_database_ = sqlite3.connect("sqlite.db")

    sql = "SELECT * FROM Voicemail WHERE language='id-ID';"
    cursor = sqlite_database_.execute(sql)
    rows = cursor.fetchall()
    print(rows)

    return


if __name__ == '__main__':
    demo1()
