#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging

from flask import render_template, request
import jsonschema

from server.annotation_server.schema import basic_intent as basic_intent_schema
from server.exception import ExpectedError
from server.annotation_server.service import basic_intent as basic_intent_service
from server.flask_server.route_wrap.common_route_wrap import common_route_wrap

from toolbox.logging.misc import json_2_str

logger = logging.getLogger('server')


def basic_intent():
    return render_template('basic_intent.html')


@common_route_wrap
def get_choice_of_language_view_func():
    args = request.form
    logger.info('get_choice_of_language_view_func, args: {}'.format(json_2_str(args)))
    return basic_intent_service.get_choice_of_language()


@common_route_wrap
def get_choice_of_label_view_func():
    args = request.form
    logger.info('get_choice_of_label_view_func, args: {}'.format(json_2_str(args)))

    # request body verification
    try:
        jsonschema.validate(args, basic_intent_schema.get_choice_of_label_request_schema)
    except (jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError, ) as e:
        raise ExpectedError(
            status_code=60401,
            message='request body invalid. ',
            detail=str(e)
        )

    language = args['language']

    result = basic_intent_service.get_choice_of_label(language)
    return result


@common_route_wrap
def get_choice_of_recommend_mode_view_func():

    args = request.form
    logger.info('get_choice_of_label_view_func, args: {}'.format(json_2_str(args)))

    # request body verification
    try:
        jsonschema.validate(args, basic_intent_schema.get_choice_of_recommend_mode_request_schema)
    except (jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError, ) as e:
        raise ExpectedError(
            status_code=60401,
            message='request body invalid. ',
            detail=str(e)
        )

    language = args['language']

    result = basic_intent_service.get_choice_of_recommend_mode(language)
    return result


@common_route_wrap
def get_annotator_workload_view_func():
    args = request.form
    logger.info('get_annotator_workload_view_func, args: {}'.format(json_2_str(args)))

    # request body verification
    try:
        jsonschema.validate(args, basic_intent_schema.get_annotator_workload_request_schema)
    except (jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError, ) as e:
        raise ExpectedError(
            status_code=60401,
            message='request body invalid. ',
            detail=str(e)
        )

    username = args['username']
    language = args['language']
    result = basic_intent_service.get_annotator_workload(username, language)

    return result


@common_route_wrap
def get_labels_count_view_func():
    args = request.form
    logger.info('get_labels_count_view_func, args: {}'.format(json_2_str(args)))

    # request body verification
    try:
        jsonschema.validate(args, basic_intent_schema.get_labels_count_request_schema)
    except (jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError, ) as e:
        raise ExpectedError(
            status_code=60401,
            message='request body invalid. ',
            detail=str(e)
        )

    language = args['language']
    result = basic_intent_service.get_labels_count(language)

    return result


@common_route_wrap
def get_model_info_view_func():
    args = request.form
    logger.info('get_model_info_view_func, args: {}'.format(json_2_str(args)))

    # request body verification
    try:
        jsonschema.validate(args, basic_intent_schema.get_model_info_request_schema)
    except (jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError, ) as e:
        raise ExpectedError(
            status_code=60401,
            message='request body invalid. ',
            detail=str(e)
        )

    language = args['language']
    result = basic_intent_service.get_model_info(language)
    return result


@common_route_wrap
def download_n_view_func():
    args = request.form
    logger.info('download_n_view_func, args: {}'.format(json_2_str(args)))

    # request body verification
    try:
        jsonschema.validate(args, basic_intent_schema.download_n_request_schema)
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
    n = int(args['n'])

    result = basic_intent_service.download_n(username, language, annotate_mode, recommend_mode, n)

    return result


@common_route_wrap
def annotate_n_view_func():
    args = request.json
    logger.info('annotate_n_view_func, args: {}'.format(json_2_str(args)))

    # request body verification
    try:
        jsonschema.validate(args, basic_intent_schema.annotate_n_request_schema)
    except (jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError, ) as e:
        raise ExpectedError(
            status_code=60401,
            message='request body invalid. ',
            detail=str(e)
        )

    username = args['username']
    language = args['language']
    annotates = args['annotates']

    count = basic_intent_service.annotate_n(
        username=username,
        language=language,
        annotates=annotates
    )

    return count


@common_route_wrap
def predict_by_language_view_func():
    args = request.form
    logger.info('predict_by_language, args: {}'.format(json_2_str(args)))

    # request body verification
    try:
        jsonschema.validate(args, basic_intent_schema.predict_request_schema)
    except (jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError, ) as e:
        raise ExpectedError(
            status_code=60401,
            message='request body invalid. ',
            detail=str(e)
        )

    language = args['language']
    text = args['text']

    result = basic_intent_service.predict_by_language(language, text)

    return result


if __name__ == '__main__':
    pass
