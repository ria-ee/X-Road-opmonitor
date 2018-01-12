import subprocess
import time

from . import settings
from .factsheet_worker import generate_factsheet
from .reportslib.logger_manager import LoggerManager


def get_start_and_end_time(file_path):
    """
    Get start date and end date from the given bash file.
    :param file_path: The path to bash file that generates the start and end dates.
    :return: Returns the start date and the end date.
    """
    proc = subprocess.Popen(file_path, stdout=subprocess.PIPE)
    tmp = proc.stdout.read()
    dates = str(tmp).split(" ")

    return dates[0][2:], dates[1][:len(dates[1]) - 3]


def generate_factsheets(logger_manager):
    """
    Checks if the FactSheet needs to be created or not. If needed, generates it.
    :param logger_manager: LoggerManager object.
    :return:
    """
    create_factsheet = True
    start_processing_time = time.time()
    logger_manager.log_heartbeat("Starting Factsheet", settings.HEARTBEAT_LOGGER_PATH,
                                 settings.FACTSHEET_HEARTBEAT_NAME, "SUCCEEDED")
    logger_manager.log_info("factsheet_start", "Starting FactSheet generation")

    previous_month_start_date_str, previous_month_end_date_str = get_start_and_end_time(settings.FACTSHEET_DATES_PATH)
    print("Start date: {0}".format(previous_month_start_date_str))
    print("End date: {0}".format(previous_month_end_date_str))

    if create_factsheet:
        logger_manager.log_heartbeat("Creating Factsheet", settings.HEARTBEAT_LOGGER_PATH,
                                     settings.FACTSHEET_HEARTBEAT_NAME, "SUCCEEDED")
        generate_factsheet(settings.FACTSHEET_PATH, previous_month_start_date_str, previous_month_end_date_str,
                           logger_manager)
        logger_manager.log_info("factsheet_generated",
                                "Finishing generating FactSheet for: {0}_{1}".format(previous_month_start_date_str,
                                                                                     previous_month_end_date_str))

    end_processing_time = time.time()
    total_time = time.strftime("%H:%M:%S", time.gmtime(end_processing_time - start_processing_time))
    logger_manager.log_info("factsheet_end", "Finished FactSheet process. Processing time: {0}".format(total_time))
    logger_manager.log_heartbeat("Factsheet finished", settings.HEARTBEAT_LOGGER_PATH,
                                 settings.FACTSHEET_HEARTBEAT_NAME, "SUCCEEDED")


def main(logger_manager):
    """
    The main method.
    :param logger_manager: LoggerManager object.
    :return:
    """
    generate_factsheets(logger_manager)


if __name__ == '__main__':

    logger_m = LoggerManager(settings.LOGGER_NAME, 'factsheet_module')
    try:
        main(logger_m)
    except Exception as e:
        logger_m.log_error('running_factsheet_main', '{0}'.format(repr(e)))
        logger_m.log_heartbeat("error", settings.HEARTBEAT_LOGGER_PATH, settings.FACTSHEET_HEARTBEAT_NAME, "FAILED")
        raise e
