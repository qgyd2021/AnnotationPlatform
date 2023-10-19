#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask import render_template, url_for

from server.annotation_server.misc.constant import Pages


def index():
    kwargs = {
        'voicemail_url': url_for(Pages.voicemail_page),
        'basic_intent_url': url_for(Pages.basic_intent_page),
        'test_tts_url': url_for(Pages.test_tts_page),
    }
    return render_template('index.html', **kwargs)


if __name__ == '__main__':
    pass
