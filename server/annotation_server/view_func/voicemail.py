#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import os

import cv2
from flask import render_template, request
import jsonschema
import librosa

from project_settings import project_path
from toolbox.cv2.misc import show_image
from toolbox.python_speech_features.misc import wave2spectrum_image
from server.exception import ExpectedError
from server.flask_server.route_wrap.common_route_wrap import common_route_wrap
from toolbox.logging.misc import json_2_str
from server.annotation_server.schema.voicemail import download_one_request_schema, upload_one_request_schema, \
    get_annotator_workload_request_schema, get_labels_count_request_schema, get_model_info_request_schema
from server.annotation_server.service.voicemail import get_choice_of_language
from server.annotation_server.service.voicemail import download_one, annotate_one, \
    get_annotator_workload, get_labels_count, get_model_info
from server.annotation_server.misc.constant.voicemail import ChoiceOfLabel, RecommendMode

logger = logging.getLogger('server')


def voicemail():
    return render_template('voicemail.html')


@common_route_wrap
def get_choice_of_language_view_func():
    args = request.form
    logger.info('get_choice_of_language_view_func, args: {}'.format(json_2_str(args)))
    return get_choice_of_language()


@common_route_wrap
def get_choice_of_label_view_func():
    args = request.form
    logger.info('get_choice_of_label_view_func, args: {}'.format(json_2_str(args)))
    return ChoiceOfLabel.all()


@common_route_wrap
def get_choice_of_recommend_mode_view_func():
    args = request.form
    logger.info('get_choice_of_recommend_mode_view_func, args: {}'.format(json_2_str(args)))
    return RecommendMode.all()


@common_route_wrap
def download_one_view_func():
    args = request.form
    logger.info('download_one_view_func, args: {}'.format(json_2_str(args)))

    # 请求体校验
    try:
        jsonschema.validate(args, download_one_request_schema)
    except (jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError, ) as e:
        raise ExpectedError(
            status_code=60401,
            message='request body invalid. ',
            detail=str(e)
        )

    username = args['username']
    language = args['language']
    annotate_mode = args['annotate_mode']
    recommend_mode = args['recommend_mode']

    result = download_one(username, language, annotate_mode, recommend_mode)

    return result


@common_route_wrap
def annotate_one_view_func():
    # args = request.json
    args = request.form
    logger.info('annotate_one_view_func, args: {}'.format(json_2_str(args)))

    # 请求体校验
    try:
        jsonschema.validate(args, upload_one_request_schema)
    except (jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError, ) as e:
        raise ExpectedError(
            status_code=60401,
            message='request body invalid. ',
            detail=str(e)
        )

    username = args['username']
    audio_filename = args['audio_filename']
    label = args['label']
    language = args['language']

    if len(label) == 0:
        raise ExpectedError(
            status_code=60401,
            message='invalid label: {}.'.format(label),
        )

    new_filename = annotate_one(username, audio_filename, label, language)

    return new_filename


@common_route_wrap
def get_annotator_workload_view_func():
    args = request.form
    logger.info('get_annotator_workload_view_func, args: {}'.format(json_2_str(args)))

    # 请求体校验
    try:
        jsonschema.validate(args, get_annotator_workload_request_schema)
    except (jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError, ) as e:
        raise ExpectedError(
            status_code=60401,
            message='request body invalid. ',
            detail=str(e)
        )

    username = args['username']
    language = args['language']
    result = get_annotator_workload(username, language)

    return result


@common_route_wrap
def get_labels_count_view_func():
    args = request.form
    logger.info('get_labels_count_view_func, args: {}'.format(json_2_str(args)))

    # 请求体校验
    try:
        jsonschema.validate(args, get_labels_count_request_schema)
    except (jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError, ) as e:
        raise ExpectedError(
            status_code=60401,
            message='request body invalid. ',
            detail=str(e)
        )

    language = args['language']

    result = get_labels_count(language)
    return result


@common_route_wrap
def get_model_info_view_func():
    args = request.form
    logger.info('get_model_info_view_func, args: {}'.format(json_2_str(args)))

    # 请求体校验
    try:
        jsonschema.validate(args, get_model_info_request_schema)
    except (jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError, ) as e:
        raise ExpectedError(
            status_code=60401,
            message='request body invalid. ',
            detail=str(e)
        )

    language = args['language']

    result = get_model_info(language)
    return result


if __name__ == '__main__':
    pass
