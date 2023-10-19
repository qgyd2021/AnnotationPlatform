#!/usr/bin/env bash


# sh run.sh --system_version windows --language id-ID --stage 0 --stop_stage 1
# sh run.sh --system_version centos --language en-IN --stage 0 --stop_stage 1


# params
system_version="windows";
verbose=true;
stage=0 # start from 0 if you need to start from data preparation
stop_stage=5
language=zh-TW
output_dir=output_dir

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


export PYTHONPATH="${work_dir}/../.."


if [ $system_version == "windows" ]; then
  alias python3='C:/Users/tianx/PycharmProjects/virtualenv/AnnotationPlatform/Scripts/python.exe'
elif [ $system_version == "centos" ]; then
  source /data/local/bin/AnnotationPlatform/bin/activate
  alias python3='/data/local/bin/AnnotationPlatform/bin/python3'
elif [ $system_version == "ubuntu" ]; then
  source /data/local/bin/AnnotationPlatform/bin/activate
  alias python3='/data/local/bin/AnnotationPlatform/bin/python3'
fi

if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
  $verbose && echo "stage 0: collect annotated data (make sure the param: 'language'=${language})"
  python3 collect_annotated_data.py \
  --language "${language}" \
  --output_dir "${output_dir}"

fi

if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
  $verbose && echo "stage 1: zip -r ${language}.zip ${output_dir}"
  zip -r ${language}.zip ${output_dir}

fi

# rm -rf ${output_dir}

