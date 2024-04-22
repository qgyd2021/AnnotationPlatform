#!/usr/bin/env bash

# sh install.sh --stage 3 --stop_stage 4 --system_version centos


system_version=windows;
verbose=true;
stage=0
stop_stage=0

python_version=3.6.5

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


voicemail_language_array=(
  "en-IN"
  "en-PH"
  "en-SG"
  "en-US"
  "es-MX"
  "id-ID"
  "ja-JP"
  "ms-MY"
  "th-TH"
  "zh-TW"
)


basic_intent_language_array=(
  "chinese"
  "english"
)


if [ $system_version == "centos" ]; then
  if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
    $verbose && echo "stage 1: install python"
    cd "${work_dir}" || exit 1;

    sh ./script/install_python.sh --system_version "centos" --python_version "${python_version}"

  fi

  if [ ${stage} -le 2 ] && [ ${stop_stage} -ge 2 ]; then
    $verbose && echo "stage 2: create virtualenv"

    /usr/local/python-${python_version}/bin/pip3 install virtualenv
    mkdir -p /data/local/bin
    cd /data/local/bin || exit 1;
    # source /data/local/bin/AnnotationPlatform/bin/activate
    /usr/local/python-${python_version}/bin/virtualenv AnnotationPlatform

  fi

  if [ ${stage} -le 3 ] && [ ${stop_stage} -ge 3 ]; then
    $verbose && echo "stage 3: create voicemail soft link"
    cd "${work_dir}/server/annotation_server/static" || exit 1;

    mkdir -p "datasets/voicemail";
    cd "datasets/voicemail" || exit 1;

    for voicemail_language in ${voicemail_language_array[*]}
    do
      if [ ! -d "${voicemail_language}" ]; then
        ln -s "/data/tianxing/PycharmProjects/datasets/voicemail/${voicemail_language}" "${voicemail_language}";

      fi
    done

  fi

  if [ ${stage} -le 4 ] && [ ${stop_stage} -ge 4 ]; then
    $verbose && echo "stage 4: create basic intent soft link"
    cd "${work_dir}/server/annotation_server/static" || exit 1;

    mkdir -p "datasets/basic_intent";
    cd "datasets/basic_intent" || exit 1;

    for basic_intent_language in ${basic_intent_language_array[*]}
    do
      if [ ! -d "${basic_intent_language}" ]; then
        ln -s "/data/tianxing/PycharmProjects/datasets/basic_intent/${basic_intent_language}" "${basic_intent_language}";

      fi
    done

  fi

fi
