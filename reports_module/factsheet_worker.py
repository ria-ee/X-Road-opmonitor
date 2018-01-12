import argparse
import datetime
import json

from . import settings
from .reportslib.database_manager import DatabaseManager
from .reportslib.factsheet_manager import FactSheetManager
from .reportslib.logger_manager import LoggerManager
from .reportslib.mongodb_handler import MongoDBHandler


def string_format(input_string):
    """
    Checks if given input string matches the specified format.
    :param input_string: The input date string.
    :return: Raises an ArgumentTypeError if the input date string doesn't match.
    """
    try:
        datetime.datetime.strptime(input_string, '%Y-%m-%d')
    except ValueError:
        raise argparse.ArgumentTypeError("Incorrect data format for '{0}', should be YYYY-MM-DD".format(input_string))


def parse_command_line_input():
    """
    Parses the command line arguments and returns error if wrong input is given.
    :return:
    """
    # Initialize ArgumentParser
    parser = argparse.ArgumentParser(description="Generate FactSheet for given 'start_date' and 'end_date'.")

    # Add mandatory arguments
    parser.add_argument('start_date')
    parser.add_argument('end_date')

    arguments = parser.parse_args()

    string_format(arguments.start_date)
    string_format(arguments.end_date)

    return arguments.start_date, arguments.end_date


def read_in_json(file_name):
    """
    Reads in the given .json file.
    :param file_name: Path to the .json file.
    :return: Returns the data that is in the file.
    """
    with open(file_name, 'r') as f:
        json_data = f.read()

    data = json.loads(json_data)
    return data


def generate_factsheet(factsheet_path, start_date, end_date, logger_manager):
    """
    Generates the FactSheet.
    :param factsheet_path: The path where the FactSheet will be saved.
    :param start_date: Starting date of the FactSheet.
    :param end_date: Ending date of the FactSheet.
    :param logger_manager: The LoggerManager object.
    :return:
    """

    mdb_suffix = settings.MONGODB_SUFFIX
    mdb_user = settings.MONGODB_USER
    mdb_pwd = settings.MONGODB_PWD
    mdb_server = settings.MONGODB_SERVER
    db_handler = MongoDBHandler(mdb_suffix, mdb_user, mdb_pwd, mdb_server)

    database_manager = DatabaseManager(db_handler, logger_manager)

    member_subsystem_info = read_in_json(settings.SUBSYSTEM_INFO_PATH)

    factsheet_manager = FactSheetManager(database_manager, logger_manager, factsheet_path,
                                         start_date, end_date,
                                         settings.number_of_top_producers, settings.number_of_top_consumers,
                                         settings.excluded_client_member_code, member_subsystem_info)

    factsheet_manager.get_facts()
    factsheet_manager.write_facts_to_file()


def main(logger_manager):
    """
    The main method.
    :param logger_manager: The LoggerManager object.
    :return:
    """
    start_date, end_date = parse_command_line_input()
    generate_factsheet(settings.FACTSHEET_PATH, start_date, end_date, logger_manager)


if __name__ == '__main__':

    logger_m = LoggerManager(settings.LOGGER_NAME, 'factsheet_module')
    try:
        main(logger_m)
    except Exception as e:
        logger_m.log_error('running_factsheet_main', '{0}'.format(repr(e)))
        logger_m.log_heartbeat("error", settings.HEARTBEAT_LOGGER_PATH, settings.FACTSHEET_HEARTBEAT_NAME, "FAILED")
        raise e
