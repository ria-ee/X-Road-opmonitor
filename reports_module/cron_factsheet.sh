#!/bin/bash

# Stop script if error
set -e 1

# Error handler function
error_handler(){
        ERROR_MSG=${1}
        echo ${ERROR_MSG}
        python3 error_handler_factsheet.py ${ERROR_MSG}
        return 1;
}

# INSTANCE=$(python3 get_settings.py INSTANCE) || error_handler "FACTSHEET:Error_while_getting_INSTANCE"
FACTSHEET_PATH=$(python3 get_settings.py FACTSHEET_PATH) || error_handler "FACTSHEET:Error_while_getting_FACTSHEET_PATH"
FACTSHEET_TARGET=$(python3 get_settings.py FACTSHEET_TARGET) || error_handler "FACTSHEET:Error_while_getting_FACTSHEET_TARGET"

echo "`date "+[%F %T]"` Start ${0}"

#
# Run factsheet
#
echo "`date "+[%F %T]"` Run factsheet ..."
cd ..
python3 -m reports_module.factsheet
echo "`date "+[%F %T]"` ... Done."

#
# Publish factsheet
#
echo "`date "+[%F %T]"` Publish factsheet ..."
cd ./reports_module
/usr/bin/rsync -qtzr --include='*.txt' --include='*/' --exclude='*' ${FACTSHEET_PATH} ${FACTSHEET_TARGET} || error_handler "FACTSHEET:Error_while_publishing_factsheets"
echo "`date "+[%F %T]"` ... Done."

echo "`date "+[%F %T]"` End ${0}"