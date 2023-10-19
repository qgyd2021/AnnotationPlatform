#!/usr/bin/python3
# -*- coding: utf-8 -*-


get_choice_of_label_request_schema = {
    'type': 'object',
    'required': ['language'],
    'properties': {
        'language': {
            'type': 'string',
        },
    }
}


get_choice_of_recommend_mode_request_schema = {
    'type': 'object',
    'required': ['language'],
    'properties': {
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


download_n_request_schema = {
    'type': 'object',
    'required': ['username', 'language', 'annotate_mode', 'recommend_mode', 'n'],
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
        'n': {
            'type': 'string',
        },
    }
}


annotate_n_request_schema = {
    'type': 'object',
    'required': ['username', 'language', 'annotates'],
    'properties': {
        'username': {
            'type': 'string',
        },
        'language': {
            'type': 'string',
        },
        'annotates': {
            'type': 'array',
            'items': {
                'type': 'object',
                'required': ['text', 'label'],
                'properties': {
                    'text': {
                        'type': 'string'
                    },
                    'label': {
                        'type': 'string'
                    }
                }
            }
        },
    }
}


predict_request_schema = {
    'type': 'object',
    'required': ['language', 'text'],
    'properties': {
        'language': {
            'type': 'string',
        },
        'text': {
            'type': 'string',
        },
    }
}


if __name__ == '__main__':
    pass
