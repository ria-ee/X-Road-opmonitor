#!/bin/bash

# Stop script if error
set -e 1

# Error handler function
error_handler(){
        ERROR_MSG=${1}
        echo ${ERROR_MSG}
        python3 error_handler.py ${ERROR_MSG}
        return 1;
}

INSTANCE=$(python3 get_settings.py INSTANCE) || error_handler "REPORTS:Error_while_getting_INSTANCE"
REPORTS_PATH=$(python3 get_settings.py REPORTS_PATH) || error_handler "REPORTS:Error_while_getting_REPORTS_PATH"

echo "`date "+[%F %T]"` Start ${0}"

#
# Run reports
#

echo "`date "+[%F %T]"` Run reports ..."
cd ..
python3 -m reports_module.report --language et
echo "`date "+[%F %T]"` ... Done."

#
# Publish reports
#

echo "`date "+[%F %T]"` Publish reports ..."
cd ./reports_module
/usr/bin/rsync -qtzr --include='*.pdf' --include='*/' --exclude='*' ${REPORTS_PATH} reports@web2a.vm.kit:/srv/www/www.ria.ee/x-tee/reports/${INSTANCE}/ || error_handler "Error_while_publishing_reports"
echo "`date "+[%F %T]"` ... Done."

#
# Run notification manager
#
echo "`date "+[%F %T]"` Run notification manager ..."
cd ..
python3 -m reports_module.notifications
echo "`date "+[%F %T]"` ... Done."

echo "`date "+[%F %T]"` End ${0}"
