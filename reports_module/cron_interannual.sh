#!/bin/bash

# Stop script if error
set -e 1

# Error handler function
error_handler(){
        ERROR_MSG=$1
        echo $ERROR_MSG
        python3 error_handler_interannual.py $ERROR_MSG
        return 1;
}

INSTANCE=$(python3 get_settings.py INSTANCE) || error_handler "INTERANNUAL_FACTSHEET:Error_while_getting_INSTANCE"
BASE_FILE_LOCATION=$(python3 get_settings.py BASE_FILE_LOCATION) || error_handler "INTERANNUAL_FACTSHEET:Error_while_getting_BASE_FILE_LOCATION"
BASE_FILE_NAME=$(python3 get_settings.py BASE_FILE_NAME) || error_handler "INTERANNUAL_FACTSHEET:Error_while_getting_BASE_FILE_NAME"

echo "`date "+[%F %T]"` Start ${0}"

# Run Inter-annual statistics
echo "`date "+[%F %T]"` Inter-annual statistics ..."
cd ..
python3 -m reports_module.interannual
echo "`date "+[%F %T]"` ... Done."

# Publish script for Inter-annual statistics
echo "`date "+[%F %T]"` Publish script for Inter-annual statistics ..."
# BASE_FILE_NAME, X-Road ver 6
cd reports_module
scp ${BASE_FILE_LOCATION}/${BASE_FILE_NAME} reports@web2a.vm.kit:/srv/www/www.ria.ee/x-tee/interannual_factsheets/${INSTANCE}/ || error_handler "INTERANNUAL_FACTSHEET:Error_while_publishing_V6_interannual_factsheet"
# data.js, X-Road ver 5
scp external_files/fact/js/data.js reports@web2a.vm.kit:/srv/www/www.ria.ee/x-tee/interannual_factsheets/${INSTANCE}/ || error_handler "INTERANNUAL_FACTSHEET:Error_while_publishing_V5_interannual_factsheet"

echo "`date "+[%F %T]"` End ${0}"

echo "`date "+[%F %T]"` ... Done."