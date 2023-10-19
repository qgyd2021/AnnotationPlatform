#!/usr/bin/python3
# -*- coding: utf-8 -*-
import base64
import logging

from flask import render_template, request, send_file
from glob import glob
import jsonschema

from server.annotation_server.schema.download import download_request_schema, glob_request_schema
from server.exception import ExpectedError
from server.flask_server.route_wrap.common_route_wrap import common_route_wrap, functional_route_wrap
from toolbox.logging.misc import json_2_str

logger = logging.getLogger('server')


@common_route_wrap
def download_view_func():
    args = request.json
    logger.info('download_view_func, args: {}'.format(json_2_str(args)))

    # 请求体校验
    try:
        jsonschema.validate(args, download_request_schema)
    except (jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError, ) as e:
        raise ExpectedError(
            status_code=60401,
            message='request body invalid. ',
            detail=str(e)
        )

    filename = args['filename']

    with open(filename, 'rb') as f:
        data = f.read()

    base64string = base64.b64encode(data).decode('utf-8')

    return base64string


@common_route_wrap
def glob_view_func():
    args = request.json
    logger.info('glob_view_func, args: {}'.format(json_2_str(args)))

    # 请求体校验
    try:
        jsonschema.validate(args, glob_request_schema)
    except (jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError, ) as e:
        raise ExpectedError(
            status_code=60401,
            message='request body invalid. ',
            detail=str(e)
        )

    pattern = args['pattern']

    filename_list = glob(pattern)

    return filename_list


if __name__ == '__main__':
    pass
