import datetime
import json
import os
from shutil import copy2

from reports_module import settings
from reports_module.reportslib.time_date_tools import get_previous_month_first_day
from reports_module.reportslib.time_date_tools import get_previous_month_last_day
from reports_module.reportslib.time_date_tools import string_to_date


class InterAnnualManager:
    def __init__(self, logger_manager):
        self.base_file = None
        self.last_update_timestamp = None
        self.factsheet = None
        self.previous_month_start_date = None
        self.previous_month_end_date = None
        self.interannual_factsheet = None
        self.logger_manager = logger_manager

    def _get_base_file(self):
        """
        Gets the base file from the hard drive.
        :return: Returns the base file.
        """
        if self.base_file is None:
            dir_name = settings.BASE_FILE_LOCATION
            file_name = settings.BASE_FILE_NAME
            file = os.path.join(dir_name, file_name)
            try:
                with open(file) as base_data:
                    base_file = json.load(base_data)
                    self.base_file = base_file
            except Exception as e:
                self.logger_manager.log_error('reading_in_base_file', '{0}'.format(repr(e)))
                self.logger_manager.log_heartbeat("error", settings.HEARTBEAT_LOGGER_PATH,
                                                  settings.INTERANNUAL_HEARTBEAT_NAME, "FAILED")
                raise e

        return self.base_file

    def _get_previous_month_start_date(self):
        """
        Gets the previous month start date.
        :return: Returns the previous month start date.
        """
        if self.previous_month_start_date is None:
            current_date = datetime.datetime.now().date()
            temp_prev_month_start_date = get_previous_month_first_day(current_date)

            if current_date.month == temp_prev_month_start_date.month:
                temp_prev_month_start_date = get_previous_month_first_day(temp_prev_month_start_date)

            self.previous_month_start_date = temp_prev_month_start_date

        return self.previous_month_start_date

    def _get_previous_month_end_date(self):
        """
        Gets the previous month end date.
        :return: Returns the previous month end date.
        """
        if self.previous_month_end_date is None:
            current_date = datetime.datetime.now().date()
            temp_prev_month_end_date = get_previous_month_last_day(current_date)

            if current_date.month == temp_prev_month_end_date.month:
                temp_prev_month_end_date = get_previous_month_last_day(temp_prev_month_end_date)

            self.previous_month_end_date = temp_prev_month_end_date

        return self.previous_month_end_date

    def _get_last_update_timestamp(self):
        """
        Gets the timestamp for current months first day at 00:00:00.
        :return: Returns the formed string of the current month's first day.
        """
        if self.last_update_timestamp is None:
            current_date = datetime.datetime.now().date()
            first_date_of_current_month = current_date.replace(day=1)
            # Format: "2017-09-01T00:00:00.000Z"
            self.last_update_timestamp = datetime.datetime.strftime(first_date_of_current_month,
                                                                    "%Y-%m-%dT%H:%M:%S.%fZ")
        return self.last_update_timestamp

    def _match_factsheet(self, factsheet):
        """
        Check if the factsheet start_date and end_date match the manager ones.
        :param factsheet: Factsheet file name.
        :return: Returns True if they are matching and False if not.
        """
        # Get start_date & end_date from the file name
        split_factsheet = factsheet.split("_")
        # Convert datetime.date objects into strings
        start_date = string_to_date(split_factsheet[0])
        end_date = string_to_date(split_factsheet[1])
        # Match the file name with object's start and end date.
        if start_date == self._get_previous_month_start_date() and end_date == self._get_previous_month_end_date():
            return True

        return False

    def _get_factsheets(self):
        """
        Gets all the available factsheets for the previous month.
        :return: Returns a list of all the previous month's factsheets.
        """
        fact_sheet_path = settings.FACTSHEET_PATH
        # List all the files in the folder
        list_of_fs = os.listdir(fact_sheet_path)
        # Returns all the matching factsheets
        return [factsheet for factsheet in list_of_fs if self._match_factsheet(factsheet)]

    def _get_latest_factsheet(self):
        """
        Gets the latest factsheet from the list of factsheets.
        :return: Returns the latest factsheet.
        """
        # Get all the matching factsheets
        all_matching_factsheets = self._get_factsheets()
        # Sort them alphabetically
        sorted_factsheets = sorted(all_matching_factsheets)
        # Return the latest one
        return sorted_factsheets[-1]

    def _get_factsheet(self):
        """
        Gets the latest Factsheet.
        :return: Returns the latest Factsheet.
        """
        if self.factsheet is None:
            # Get the latest factsheet file name
            latest_factsheet = self._get_latest_factsheet()
            # Get the factsheet full path
            dir_name = settings.FACTSHEET_PATH
            file_name = latest_factsheet
            file = os.path.join(dir_name, file_name)
            # Read in the factsheet
            try:
                with open(file) as base_data:
                    factsheet = json.load(base_data)
                    self.factsheet = factsheet
            except Exception as e:
                self.logger_manager.log_error('reading_in_factsheet_file', '{0}'.format(repr(e)))
                self.logger_manager.log_heartbeat("error", settings.HEARTBEAT_LOGGER_PATH,
                                                  settings.INTERANNUAL_HEARTBEAT_NAME, "FAILED")
                raise e

        return self.factsheet

    def _set_header_fields(self):
        """
        Sets the header fields of the base_file.
        :return: None
        """
        base_file = self._get_base_file()
        # Get fields from settings
        base_file['last_incident'] = settings.LAST_INCIDENT
        base_file['affected_parties'] = settings.AFFECTED_PARTIES
        base_file['effective_query_proportion'] = settings.EFFECTIVE_QUERY_PROPORTION
        base_file['effective_query_minutes'] = settings.EFFECTIVE_QUERY_MINUTES
        base_file['protocol_changes'] = settings.PROTOCOL_CHANGES
        base_file['last_update'] = self._get_last_update_timestamp()
        # Update base file
        self.base_file = base_file

    @staticmethod
    def _back_up_base_file():
        """
        Back-ups the current base file.
        :return: None
        """
        dir_name = settings.BASE_FILE_LOCATION
        file_name = settings.BASE_FILE_NAME
        back_up_file_name = settings.BASE_FILE_NAME + ".BAK"
        file = os.path.join(dir_name, file_name)
        new_file = os.path.join(dir_name, back_up_file_name)
        copy2(file, new_file)

    def _append_previous_month_data_to_base_file(self):
        """
        Appends the previous month's data from the factsheet into the base file.
        :return: None
        """
        base_file = self._get_base_file()
        factsheet = self._get_factsheet()
        year = str(self._get_previous_month_start_date().year)
        month = str(self._get_previous_month_start_date().month)
        previous_month_data = factsheet['stats'][year]['months'][month]
        if base_file['stats'].get(year, None) is None:
            base_file['stats'][year] = {'months': {'{0}'.format(month): previous_month_data}}
        elif base_file['stats'][year]['months'].get(month, None) is None:
            base_file['stats'][year]['months'][month] = previous_month_data
        else:
            self.logger_manager.log_error('merging_base_file_and_factsheet',
                                          'This months data is already in the base file!')
            self.logger_manager.log_heartbeat("error", settings.HEARTBEAT_LOGGER_PATH,
                                              settings.INTERANNUAL_HEARTBEAT_NAME, "FAILED")
            raise ValueError("This months data is already in the base file!")
        self.interannual_factsheet = base_file

    def _write_base_file(self):
        """
        Writes the new base file into the hard drive
        :return: None
        """
        dir_name = settings.BASE_FILE_LOCATION
        file_name = settings.BASE_FILE_NAME
        file = os.path.join(dir_name, file_name)
        interannual_factsheet = self.interannual_factsheet
        if interannual_factsheet is None:
            self.logger_manager.log_error('updating_base_file',
                                          "The interannual statiscs haven't been created, abandoning!")
            self.logger_manager.log_heartbeat("error", settings.HEARTBEAT_LOGGER_PATH,
                                              settings.INTERANNUAL_HEARTBEAT_NAME, "FAILED")
            raise ValueError("The interannual statiscs haven't been created, abandoning!")
        try:
            with open(file, "w") as base_data:
                json.dump(interannual_factsheet, base_data, indent=4)
        except Exception as e:
            self.logger_manager.log_error('writing_base_file', '{0}'.format(repr(e)))
            self.logger_manager.log_heartbeat("error", settings.HEARTBEAT_LOGGER_PATH,
                                              settings.INTERANNUAL_HEARTBEAT_NAME, "FAILED")
            raise e

    def get_interannual_factsheet(self):
        """
        Does all the steps to generate the interannual factsheet.
        :return: None
        """
        self._get_base_file()
        self._back_up_base_file()
        self._get_last_update_timestamp()
        self._get_previous_month_start_date()
        self._get_previous_month_end_date()
        self._get_factsheet()
        self._set_header_fields()
        self._append_previous_month_data_to_base_file()
        self._write_base_file()
