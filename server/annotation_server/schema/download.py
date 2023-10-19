#!/usr/bin/python3
# -*- coding: utf-8 -*-


download_request_schema = {
    'type': 'object',
    'required': ['filename'],
    'properties': {
        'filename': {
            'type': 'string',
        },
    }
}


glob_request_schema = {
    'type': 'object',
    'required': ['pattern'],
    'properties': {
        'pattern': {
            'type': 'string',
        },
    }
}


if __name__ == '__main__':
    pass
