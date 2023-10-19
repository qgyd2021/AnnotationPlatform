#!/usr/bin/env bash

kill -9 `ps -aef | grep 'run_annotation_server.py' | grep -v grep | awk '{print $2}'`

