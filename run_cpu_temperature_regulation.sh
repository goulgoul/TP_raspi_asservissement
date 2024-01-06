#!/bin/bash

# shell script to run a python code in a venv and output errors to a log file


ROOT_DIRECTORY='/cputemp'
PROGRAM_TO_RUN='/cputemp/encoder_lab_code/app_cpu_tempature_regulation.py'   
LOGS_DIRECTORY='/cputemp/logs'
RUN_LOG_FILE_PATH=$LOGS_DIRECTORY/run_cpu_temperature_regulation.log
PROGRAM_LOG_FILE_PATH=$LOGS_DIRECTORY/app_cpu_temperature_regulation.log

echo $(date)' Starting bash script' >> $RUN_LOG_FILE_PATH 2>&1

cd $ROOT_DIRECTORY
source $ROOT_DIRECTORY'/bin/activate'
echo $(date)' Running python script '$PROGRAM_TO_RUN >> $RUN_LOG_FILE_PATH 2>&1
date >> $PROGRAM_LOG_FILE_PATH 2>&1
python $PROGRAM_TO_RUN >> $PROGRAM_LOG_FILE_PATH 2>&1
deactivate
echo $(date)' End of bash run script' >> $RUN_LOG_FILE_PATH

