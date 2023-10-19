#!/usr/bin/python3
# -*- coding: utf-8 -*-


download_one_request_schema = {
    'type': 'object',
    'required': ['username', 'language', 'annotate_mode', 'recommend_mode'],
    'properties': {
        'username': {
            'type': 'string',
        },
        'language': {
            'type': 'string',
        },
        'annotate_mode': {
            'type': 'string',
        },
        'recommend_mode': {
            'type': 'string',
        },
    }
}


upload_one_request_schema = {
    'type': 'object',
    'required': ['username', 'audio_filename', 'label', 'language'],
    'properties': {
        'username': {
            'type': 'string',
        },
        'audio_filename': {
            'type': 'string',
        },
        'label': {
            'type': 'string',
        },
        'language': {
            'type': 'string',
        },
    }
}


get_annotator_workload_request_schema = {
    'type': 'object',
    'required': ['username', 'language'],
    'properties': {
        'username': {
            'type': 'string',
        },
        'language': {
            'type': 'string',
        },
    }
}


get_labels_count_request_schema = {
    'type': 'object',
    'required': ['language'],
    'properties': {
        'language': {
            'type': 'string',
        },
    }
}


get_model_info_request_schema = {
    'type': 'object',
    'required': ['language'],
    'properties': {
        'language': {
            'type': 'string',
        },
    }
}


if __name__ == '__main__':
    pass
