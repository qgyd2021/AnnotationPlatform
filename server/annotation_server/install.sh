#!/usr/bin/env bash


system_version="centos";
verbose=true;
stage=0 # start from 0 if you need to start from data preparation
stop_stage=9

work_dir="$(pwd)"


# parse options
while true; do
  [ -z "${1:-}" ] && break;  # break if there are no arguments
  case "$1" in
    --*) name=$(echo "$1" | sed s/^--// | sed s/-/_/g);
      eval '[ -z "${'"$name"'+xxx}" ]' && echo "$0: invalid option $1" 1>&2 && exit 1;
      old_value="(eval echo \\$$name)";
      if [ "${old_value}" == "true" ] || [ "${old_value}" == "false" ]; then
        was_bool=true;
      else
        was_bool=false;
      fi

      # Set the variable to the right value-- the escaped quotes make it work if
      # the option had spaces, like --cmd "queue.pl -sync y"
      eval "${name}=\"$2\"";

      # Check that Boolean-valued arguments are really Boolean.
      if $was_bool && [[ "$2" != "true" && "$2" != "false" ]]; then
        echo "$0: expected \"true\" or \"false\": $1 $2" 1>&2
        exit 1;
      fi
      shift 2;
      ;;

    *) break;
  esac
done


cd "${work_dir}/../.." || exit 1;


if [ $system_version == "centos" ]; then
  source /data/local/bin/AnnotationPlatform/bin/activate || exit 1;
  echo "source /data/local/bin/AnnotationPlatform/bin/activate";

  if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
    $verbose && echo "stage 0: pip3 install requirements.txt"

    echo "flask==2.0.2
    gevent==21.12.0
    pandas==1.1.5
    xlrd==1.2.0
    openpyxl==3.0.9
    python-dotenv==0.19.2
    jsonschema==4.0.0
    requests==2.26.0
    opencv-contrib-python==3.4.2.16
    librosa==0.8.1
    python_speech_features==0.6
    tqdm==4.64.1
    flask_apscheduler==1.12.4
    " > requirements.txt

  #  pip3 install -r requirements.txt
    pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
  fi

  if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
    $verbose && echo "stage 1: build datasets soft link"

    mkdir -p static/datasets/voicemail && cd static/datasets/voicemail || exit 1;
    for language in "en-PH" "en-SG" "en-US" "id-ID" "ja-JP" "zh-TW";
    do
      # ln -s /data/tianxing/PycharmProjects/datasets/voicemail/zh-TW zh-TW
      ln -s "/data/tianxing/PycharmProjects/datasets/voicemail/${language}" "${language}";
    done
  fi

fi
