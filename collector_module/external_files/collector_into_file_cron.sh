#!/bin/bash

# Sample scripts to collect X-Road v6 operational monitoring data from security servers.
# Includes:
# collector_into_file_cron.sh - main script (bash) to be executed manually or from crontab. Sample: */15 * * * * /path/to/collector_into_file_cron.sh
# xrd_servers.py - Python script to prepare list of security servers, from where operational monitoring data to be collected
# collector_into_file_get_opmon.py - Python script to collect operational monitoring data from given security server
#
# Author: Toomas Mölder <toomas.molder@ria.ee> +372 5522000 skype:toomas.molder
#

#
# Variables
# 
# Executables
PYTHON="/usr/bin/python"
# Get current working directory
CWD=$(pwd)
# Deprecated
# LIST_SERVERS="${CWD}/collector_into_file_list_servers.py"
LIST_SERVERS="${CWD}/xrd_servers.py"
GET_OPMON="${CWD}/collector_into_file_get_opmon.py"

#
# IP or Name of Central Server
# Deprecated
# CENTRAL_SERVER="213.184.41.178" # HA keskserver 1 (node_0)
# CENTRAL_SERVER="213.184.41.186" # HA keskserver 2 (node_1)
# CENTRAL_SERVER="213.184.41.190" # HA keskserver 3 (node_2)
# IP or Name of Security Server
SECURITY_SERVER="10.0.1.141" # Internal IP
# SECURITY_SERVER = "195.80.123.159" # External IP

# Current timestamp
NOW=$(/bin/date +"%Y-%m-%d_%H:%M:%S%z")
# A cache file is used when Central Server does not reply
CACHE_DIR="."
CACHE_EXT="txt"
# Deprecated
# SERVERS_CACHE_NOW="${CACHE_DIR}/cache_${CENTRAL_SERVER}_${NOW}.${CACHE_EXT}"
# SERVERS_CACHE="${CACHE_DIR}/cache_${CENTRAL_SERVER}.${CACHE_EXT}"
SERVERS_CACHE_NOW="${CACHE_DIR}/cache_${SECURITY_SERVER}_${NOW}.${CACHE_EXT}"
SERVERS_CACHE="${CACHE_DIR}/cache_${SECURITY_SERVER}.${CACHE_EXT}"
# Directory to keep result files, log directory
LOG_DIR="."
LOG_EXT="log"
# LOG_FILE="log_${CENTRAL_SERVER}_${NOW}.${LOG_EXT}"
LOG_FILE="log_${SECURITY_SERVER}_${NOW}.${LOG_EXT}"
STATUS="${LOG_DIR}/${0%.*}.${LOG_EXT}"

echo "$(/bin/date +"%Y-%m-%d_%H:%M:%S%z"): ${0} started" >> ${STATUS}

#
# Basic checks before actual work
#
# We do expect Python available
if [ ! -x "${PYTHON}" ] || [ ! -f "${PYTHON}" ]
then
    echo "ERROR: ${PYTHON} is not executable or available!"
    echo "ERROR: ${PYTHON} is not executable or available!" >> ${STATUS}
    echo "$(/bin/date +"%Y-%m-%d_%H:%M:%S%z"): ${0} exit 1" >> ${STATUS}
    exit 1
fi

# We do expect Python ver 2.x available
PYTHON_VERSION=$(${PYTHON} -V 2>&1)
if [[ "${PYHON_VERSION}" =~ "2." ]]
then
    echo "ERROR: ${PYTHON} version 2.x is required!"
    echo "ERROR: ${PYTHON} version 2.x is required!" >> ${STATUS}
    echo "$(/bin/date +"%Y-%m-%d_%H:%M:%S%z"): ${0} exit 1" >> ${STATUS}
    exit 1
fi

# We do expect required Python scripts available
if [ ! -f "${LIST_SERVERS}" ]
then
    echo "ERROR: File ${LIST_SERVERS} does not exist!"
    echo "ERROR: File ${LIST_SERVERS} does not exist!" >> ${STATUS}
    echo "$(/bin/date +"%Y-%m-%d_%H:%M:%S%z"): ${0} exit 1" >> ${STATUS}
    exit 1
fi

if [ ! -f "${GET_OPMON}" ]
then
    echo "ERROR: File ${GET_OPMON} does not exist!"
    echo "ERROR: File ${GET_OPMON} does not exist!" >> ${STATUS}
    echo "$(/bin/date +"%Y-%m-%d_%H:%M:%S%z"): ${0} exit 1" >> ${STATUS}
    exit 1
fi

# We do expect working directory exists
if [ ! -d "${LOG_DIR}" ]
then
    echo "ERROR: Log directory ${LOG_DIR} does not exist!"
    echo "ERROR: Log directory ${LOG_DIR} does not exist!" >> ${STATUS}
    echo "$(/bin/date +"%Y-%m-%d_%H:%M:%S%z"): ${0} exit 1" >> ${STATUS}
    exit 1
fi

#
# Do the actual stuff
#
# Deprecated: Receive list of security servers available from -c CENTRAL_SERVER global configuration
# Receive list of security servers available from -s SECURITY_SERVER global configuration
# When succeeded, keep it in cache file
# When failed, use cache file
# Deprecated
# DATA=$(${PYTHON} ${LIST_SERVERS} ${CENTRAL_SERVER})
# DATA=$(${PYTHON} ${LIST_SERVERS} -c ${CENTRAL_SERVER}) # Use of Central Server to fetch Globalconf
DATA=$(${PYTHON} ${LIST_SERVERS} -s ${SECURITY_SERVER}) # Use of Security Server to fetch Globalconf
EXIT_CODE=$?

if [ ${EXIT_CODE} -ne 0 ]; then
    echo "WARNING: command '${PYTHON} ${LIST_SERVERS} -s ${SECURITY_SERVER}' exited with code ${EXIT_CODE}"
    echo "WARNING: command '${PYTHON} ${LIST_SERVERS} -s ${SECURITY_SERVER}' exited with code ${EXIT_CODE}" >> ${STATUS}
fi

if [[ -z ${DATA} ]]; then
    DATA=$(/bin/cat ${SERVERS_CACHE})
    if [[ -z ${DATA} ]]; then
        echo "ERROR: Server list not available"
        echo "ERROR: Server list not available" >> ${STATUS}
        echo "$(/bin/date +"%Y-%m-%d_%H:%M:%S%z"): ${0} exit 1" >> ${STATUS}
        exit 1
    fi
else
    echo "${DATA}" > ${SERVERS_CACHE_NOW}
        /bin/rm -f ${SERVERS_CACHE}
        /bin/ln -s ${SERVERS_CACHE_NOW} ${SERVERS_CACHE}
fi

# Receive operational monitoring data from security servers in list
# Script GET_OPMON keeps the status of data received in ${LOG_DIR}/nextRecordsFrom.json
cd ${LOG_DIR}/
echo "${DATA}" | ${PYTHON} -u ${GET_OPMON} > ${LOG_FILE} 2>&1
EXIT_CODE=$?
cd ${CWD}/
echo "$(/bin/date +"%Y-%m-%d_%H:%M:%S%z"): ${0} exit ${EXIT_CODE}" >> ${STATUS}
