#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import sqlite3

from toolbox.design_patterns.singleton import ParamsSingleton

logger = logging.getLogger(__file__)


class SqliteConnect(ParamsSingleton):
    def __init__(self, database: str):
        self.database = database
        self.connect = sqlite3.connect(database)

    def execute(self, sql: str, commit: bool = False):
        try:
            cursor = self.connect.execute(sql)
            if commit:
                self.connect.commit()
            rows = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            logger.error('sql: {}'.format(sql))
            raise e
        return rows


if __name__ == '__main__':
    pass
