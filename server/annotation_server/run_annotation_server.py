#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import logging
import os
import sys
from datetime import datetime, timedelta

pwd = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(pwd, '../../'))

from flask import Flask
from gevent import pywsgi

from server import log
from server.annotation_server import settings

log.setup(log_directory=settings.log_directory)

from server.flask_server.view_func.heart_beat import heart_beat
from server.annotation_server.view_func import basic_intent, download, index, test_tts, voicemail

from flask_apscheduler import APScheduler
from server.annotation_server.service.basic_intent import task_basic_intent_update_from_excel_to_sqlite_db, \
    task_basic_intent_update_from_sqlite_db_to_excel, task_basic_intent_predict_info_update_to_sqlite_db
from server.annotation_server.service.voicemail import task_voicemail_filename_update_to_sqlite_db, \
    task_voicemail_predict_info_update_to_sqlite_db
from server.annotation_server.misc.constant import Pages


logger = logging.getLogger('server')


# 初始化服务
flask_app = Flask(
    __name__,
    static_url_path='/',
    static_folder='static',
    template_folder='static/templates',
)

flask_app.add_url_rule(rule='/HeartBeat', view_func=heart_beat, methods=['GET', 'POST'], endpoint='HeartBeat')
flask_app.add_url_rule(rule='/index', view_func=index.index, methods=['GET'], endpoint=Pages.index_page)

flask_app.add_url_rule(rule='/voicemail', view_func=voicemail.voicemail, methods=['GET'], endpoint=Pages.voicemail_page)
flask_app.add_url_rule(rule='/voicemail/get_choice_of_language', view_func=voicemail.get_choice_of_language_view_func, methods=['POST'], endpoint='VoicemailGetChoiceOfLanguage')
flask_app.add_url_rule(rule='/voicemail/get_choice_of_label', view_func=voicemail.get_choice_of_label_view_func, methods=['POST'], endpoint='VoicemailGetChoiceOfLabel')
flask_app.add_url_rule(rule='/voicemail/get_choice_of_recommend_mode', view_func=voicemail.get_choice_of_recommend_mode_view_func, methods=['POST'], endpoint='VoicemailGetChoiceOfRecommendMode')
flask_app.add_url_rule(rule='/voicemail/get_annotator_workload', view_func=voicemail.get_annotator_workload_view_func, methods=['POST'], endpoint='VoicemailGetAnnotatorWorkload')
flask_app.add_url_rule(rule='/voicemail/get_labels_count', view_func=voicemail.get_labels_count_view_func, methods=['POST'], endpoint='VoicemailGetLabelsCount')
flask_app.add_url_rule(rule='/voicemail/get_model_info', view_func=voicemail.get_model_info_view_func, methods=['POST'], endpoint='VoicemailGetModelInfo')
flask_app.add_url_rule(rule='/voicemail/download_one', view_func=voicemail.download_one_view_func, methods=['POST'], endpoint='VoicemailDownloadOne')
flask_app.add_url_rule(rule='/voicemail/annotate_one', view_func=voicemail.annotate_one_view_func, methods=['POST'], endpoint='VoicemailAnnotateOne')

flask_app.add_url_rule(rule='/basic_intent', view_func=basic_intent.basic_intent, methods=['GET'], endpoint=Pages.basic_intent_page)
flask_app.add_url_rule(rule='/basic_intent/get_choice_of_language', view_func=basic_intent.get_choice_of_language_view_func, methods=['POST'], endpoint='BasicIntentGetChoiceOfLanguage')
flask_app.add_url_rule(rule='/basic_intent/get_choice_of_label', view_func=basic_intent.get_choice_of_label_view_func, methods=['POST'], endpoint='BasicIntentGetChoiceOfLabel')
flask_app.add_url_rule(rule='/basic_intent/get_choice_of_recommend_mode', view_func=basic_intent.get_choice_of_recommend_mode_view_func, methods=['POST'], endpoint='BasicIntentGetChoiceOfRecommendMode')
flask_app.add_url_rule(rule='/basic_intent/get_annotator_workload', view_func=basic_intent.get_annotator_workload_view_func, methods=['POST'], endpoint='BasicIntentGetAnnotatorWorkload')
flask_app.add_url_rule(rule='/basic_intent/get_labels_count', view_func=basic_intent.get_labels_count_view_func, methods=['POST'], endpoint='BasicIntentGetLabelsCount')
flask_app.add_url_rule(rule='/basic_intent/get_model_info', view_func=basic_intent.get_model_info_view_func, methods=['POST'], endpoint='BasicIntentGetModelInfo')
flask_app.add_url_rule(rule='/basic_intent/download_n', view_func=basic_intent.download_n_view_func, methods=['POST'], endpoint='BasicIntentDownloadN')
flask_app.add_url_rule(rule='/basic_intent/annotate_n', view_func=basic_intent.annotate_n_view_func, methods=['POST'], endpoint='BasicIntentAnnotateN')
flask_app.add_url_rule(rule='/basic_intent/predict_by_language', view_func=basic_intent.predict_by_language_view_func, methods=['POST'], endpoint='BasicIntentPredictByLanguage')

flask_app.add_url_rule(rule='/test_tts', view_func=test_tts.test_tts, methods=['GET'], endpoint=Pages.test_tts_page)
flask_app.add_url_rule(rule='/test_tts/bark_tts', view_func=test_tts.bark_tts_view_func, methods=['POST'], endpoint='BarkTTS')
flask_app.add_url_rule(rule='/test_tts/bark_speakers', view_func=test_tts.bark_speakers_view_func, methods=['GET'], endpoint='BarkSpeakers')
flask_app.add_url_rule(rule='/test_tts/bark_tts_by_excel', view_func=test_tts.bark_tts_by_excel_view_func, methods=['POST'], endpoint=Pages.bark_tts_by_excel)

flask_app.add_url_rule(rule='/download/glob', view_func=download.glob_view_func, methods=['POST'], endpoint='DownloadGlob')
flask_app.add_url_rule(rule='/download/download', view_func=download.download_view_func, methods=['POST'], endpoint='DownloadDownload')


scheduler = APScheduler(app=flask_app)
scheduler.init_app(flask_app)
# scheduler.add_job(
#     id='task_basic_intent_update_from_excel_to_sqlite_db',
#     func=task_basic_intent_update_from_excel_to_sqlite_db,
#     trigger='cron',
#     day_of_week='0-6',
#     hour=1,
#     minute=0,
#     # next_run_time=datetime.now() + timedelta(seconds=5)
# )
# scheduler.add_job(
#     id='task_basic_intent_update_from_sqlite_db_to_excel',
#     func=task_basic_intent_update_from_sqlite_db_to_excel,
#     trigger='cron',
#     day_of_week='0-6',
#     hour=1,
#     minute=30,
#     # next_run_time=datetime.now() + timedelta(seconds=5)
# )
# scheduler.add_job(
#     id='task_basic_intent_predict_info_update_to_sqlite_db',
#     func=task_basic_intent_predict_info_update_to_sqlite_db,
#     trigger='cron',
#     day_of_week='0-6',
#     hour=2,
#     # next_run_time=datetime.now() + timedelta(seconds=5)
# )
scheduler.add_job(
    id='task_voicemail_filename_update_to_sqlite_db',
    func=task_voicemail_filename_update_to_sqlite_db,
    trigger='interval',
    seconds=1 * 60 * 60,
    next_run_time=datetime.now() + timedelta(seconds=5)
)
# scheduler.add_job(
#     id='task_voicemail_predict_info_update_to_sqlite_db',
#     func=task_voicemail_predict_info_update_to_sqlite_db,
#     trigger='cron',
#     day_of_week='0-6',
#     hour=4,
#     minute=30,
#     # next_run_time=datetime.now() + timedelta(seconds=5)
# )
scheduler.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--port',
        default=settings.port,
        type=int,
    )
    args = parser.parse_args()

    logger.info('model server is already, 127.0.0.1:{}'.format(args.port))

    # flask_app.run(
    #     host='0.0.0.0',
    #     port=args.port,
    # )

    server = pywsgi.WSGIServer(
        listener=('0.0.0.0', args.port),
        application=flask_app
    )
    server.serve_forever()
