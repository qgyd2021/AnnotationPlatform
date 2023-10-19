#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import logging

import requests

from server.annotation_server import settings

logger = logging.getLogger('server')


class BarkTTS(object):

    @classmethod
    def bark_tts(cls, text: str, speaker: str):
        url = 'http://{host}:{port}/bark_tts'.format(
            host=settings.bark_tts_host,
            port=settings.bark_tts_port,
        )
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'text': text,
            'speaker': speaker,
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=60)
        if resp.status_code != 200:
            logger.info('basic_intent_by_language failed. resp text: {}'.format(resp.text))
            return None
        js = resp.json()
        if js['status_code'] != 60200:
            return None

        return js['result']

    @classmethod
    def bark_speakers(cls) -> list:
        url = 'http://{host}:{port}/bark_speakers'.format(
            host=settings.bark_tts_host,
            port=settings.bark_tts_port,
        )

        resp = requests.get(url)
        if resp.status_code != 200:
            logger.info('basic_intent_by_language failed. resp text: {}'.format(resp.text))
            return None
        js = resp.json()
        if js['status_code'] != 60200:
            return None

        return js['result']


if __name__ == '__main__':
    pass
