#!/bin/bash
#
# Usage: make_riha.sh <Central Server IP/Name>
#

# Stop script if error
set -e 1

# Error handler function
error_handler(){
        ERROR_MSG=${1}
        echo ${ERROR_MSG}
        python3 error_handler.py ${ERROR_MSG}
        return 1;
}

if [ ${1} = "-h" ] || [ ${1} = "--help" ]; then
    echo -e "Usage: ${0}
        The IP/Name of Central Server can be found in configuration anchor http://x-road.eu/packages/
        # XTEE-CI-XM
        # CENTRAL_SERVER=\"xtee7.ci.kit\"
        #
        # ee-dev http://x-road.eu/packages/ee-dev_public_anchor.xml
        # CENTRAL_SERVER=\"195.80.109.140\"
        #
        # ee-test http://x-road.eu/packages/ee-test_public_anchor.xml
        # CENTRAL_SERVER=\"195.80.127.40\"
        #
        # EE http://x-road.eu/packages/EE_public-anchor.xml
        # CENTRAL_SERVER=\"213.184.41.178\"
"
    exit 1;
fi

# CENTRAL_SERVER=${1}
CENTRAL_SERVER=$(python3 ../get_settings.py CENTRAL_SERVER)

#
# Input file: riha_systems.json, configurable as parameter --riha <filename>
# Deprecated: Output file: riha.json, hardcoded into ./subsystems_json.py
# Output file: riha.json, hardcoded into ./subsystems_json_riha.py
#
INPUT_RIHA="./riha_systems.json"
OUTPUT_RIHA="./riha.json"

# Check existence of ${INPUT_RIHA}
if [ ! -f "${INPUT_RIHA}" ]; then
    echo "`date "+[%F %T]"` ERROR: File ${INPUT_RIHA} does not exist! Exiting ..."
	exit 1
fi

# Make a backup of result file ${OUTPUT_RIHA}
if [[ $(find ${OUTPUT_RIHA} -type f -size +100c 2>/dev/null) ]]; then
    /bin/cp --preserve ${OUTPUT_RIHA} ${OUTPUT_RIHA}.bak
else
    echo "`date "+[%F %T]"` Warning: Size of ${OUTPUT_RIHA} was less than 100 bytes. Do not make backup"
fi

# Do the job
# Deprecated
# python3 ./subsystems_json.py -c ${CENTRAL_SERVER} || error_handler "Error_while_make_riha.json"
python3 ./subsystems_json_riha.py -c ${CENTRAL_SERVER} --riha ${INPUT_RIHA} || error_handler "ERROR: ${0} while make ${OUTPUT_RIHA}"

# Check the result file ${OUTPUT_RIHA}, restore from backup if needed
if [[ $(find ${OUTPUT_RIHA} -type f -size -100c 2>/dev/null) ]]; then
   /bin/cp --preserve ${OUTPUT_RIHA}.bak ${OUTPUT_RIHA}
   echo "`date "+[%F %T]"` Warning: Size of ${OUTPUT_RIHA} was less than 100 bytes. Restore from backup"
fi
