#!/usr/bin/env bash

rm -rf nohup.out
rm -rf logs/

source /data/local/bin/AnnotationPlatform/bin/activate

nohup python3 run_annotation_server.py > nohup.out &
