#!/usr/bin/python3
# -*- coding: utf-8 -*-


bark_tts_request_schema = {
    'type': 'object',
    'required': ['text', 'speaker'],
    'properties': {
        'text': {
            'type': 'string',
        },
        'speaker': {
            'type': 'string',
        },
    }
}


if __name__ == '__main__':
    pass
