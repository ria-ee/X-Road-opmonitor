import copy
import datetime
import time
import json
import os
from operator import itemgetter

from ..reportslib import time_date_tools


class FactSheetManager:
    def __init__(self, database_manager, logger_manager, file_path, start_date, end_date, number_of_top_producers,
                 number_of_top_consumers, excluded_member_codes, member_subsystem_info):
        """
        Creates a FactSheetManager object that keeps the information about a single FactSheet inside.
        :param database_manager: The DatabaseManager object.
        :param logger_manager: The LoggerManager object.
        :param file_path: The path of the FactSheet (where it will be saved).
        :param start_date: The start date of the report.
        :param end_date: The end date of the report.
        :param number_of_top_producers: How many producers to include in the top list.
        :param number_of_top_consumers: How many consumers to include in the top list.
        :param excluded_member_codes: The member codes that will be excluded from the top lists.
        :param member_subsystem_info: List of dictionaries containing information about the members + subsystems.
        """
        self.database_manager = database_manager
        self.logger_manager = logger_manager

        self.member_subsystem_info = member_subsystem_info
        self.excluded_member_codes = excluded_member_codes
        self.number_of_top_producers = number_of_top_producers
        self.number_of_top_consumers = number_of_top_consumers
        self.start_date = start_date
        self.end_date = end_date
        self.start_date_timestamp = time_date_tools.date_to_timestamp_milliseconds(
            time_date_tools.string_to_date(self.start_date))
        self.end_date_timestamp = time_date_tools.date_to_timestamp_milliseconds(
            time_date_tools.string_to_date(self.end_date), False)
        self.file_path = file_path

        self.query_count = 0
        self.service_count = 0
        self.producer_count = 0
        self.member_count = 0
        self.gov_member_count = 0
        self.subsystem_count = 0
        self.sec_srv_services = 0
        self.producers_top = {}
        self.consumers_top = {}

    @staticmethod
    def get_unique_set(service_list, client_list):
        """
        Gets all the unique combinations of the 2 input lists.
        :param service_list: input list A.
        :param client_list: input list B.
        :return: returns the set of all the combinations of the 2 input lists.
        """
        member_set = set()

        for service in service_list:
            sorted_keys = sorted(service)
            t = ()
            for key in sorted_keys:
                t = t + (key, service[key])
            member_set.add(t)

        for client in client_list:
            sorted_keys = sorted(client)
            t = ()
            for key in sorted_keys:
                t = t + (key, client[key])
            member_set.add(t)

        return member_set

    @staticmethod
    def unify_sec_srv(sec_srv_list, services=False):
        """
        Unifies the security servers by removing unnecessary fields.
        :param sec_srv_list: List of documents to be unified.
        :param services: Boolean that defines if these are service documents or not.
        :return: Returns a unified list of documents.
        """
        new_list = []

        for service in sec_srv_list:
            doc = service["_id"]

            if services:
                doc["securityServerAddress"] = doc.pop("serviceSecurityServerAddress")
            else:
                doc["securityServerAddress"] = doc.pop("clientSecurityServerAddress")

            new_list.append(doc)

        return new_list

    @staticmethod
    def unify_service_subsystems(service_subsystems_list):
        """
        Unifies the service subsystem documents by removing unnecessary fields.
        :param service_subsystems_list: List of documents to be unified.
        :return: Returns a unified list of documents.
        """
        new_list = []

        for service in service_subsystems_list:
            doc = service["_id"]
            doc["xRoadInstance"] = doc.pop("serviceXRoadInstance")
            doc["memberClass"] = doc.pop("serviceMemberClass")
            doc["memberCode"] = doc.pop("serviceMemberCode")
            doc["subsystemCode"] = doc.pop("serviceSubsystemCode")
            new_list.append(doc)

        return new_list

    @staticmethod
    def unify_client_subsystems(client_subsystems_list):
        """
        Unifies the client subsystem documents by removing unnecessary fields.
        :param client_subsystems_list: List of documents to be unified.
        :return: Returns a unified list of documents.
        """
        new_list = []

        for service in client_subsystems_list:
            doc = service["_id"]
            doc["xRoadInstance"] = doc.pop("clientXRoadInstance")
            doc["memberClass"] = doc.pop("clientMemberClass")
            doc["memberCode"] = doc.pop("clientMemberCode")
            doc["subsystemCode"] = doc.pop("clientSubsystemCode")
            new_list.append(doc)

        return new_list

    @staticmethod
    def unify_service_members(service_list, gov_member=False):
        """
        Unifies the service member documents by removing unnecessary fields.
        :param service_list: List of documents to be unified.
        :param gov_member: Boolean that defines if these are GOV member documents or not.
        :return: Returns a unified list of documents.
        """
        new_list = []
        copied_list = copy.deepcopy(service_list)

        for service in copied_list:
            doc = service["_id"]

            if gov_member and doc["serviceMemberClass"] == "GOV" or not gov_member:
                doc["xRoadInstance"] = doc.pop("serviceXRoadInstance")
                doc["memberClass"] = doc.pop("serviceMemberClass")
                doc["memberCode"] = doc.pop("serviceMemberCode")
                new_list.append(doc)

        return new_list

    @staticmethod
    def unify_client_members(client_list, gov_member=False):
        """
        Unifies the client member documents by removing unnecessary fields.
        :param client_list:  List of documents to be unified.
        :param gov_member: Boolean that defines if these are GOV member documents or not.
        :return: Returns a unified list of documents.
        """
        new_list = []
        copied_list = copy.deepcopy(client_list)

        for client in copied_list:
            doc = client["_id"]

            if gov_member and doc["clientMemberClass"] == "GOV" or not gov_member:
                doc["xRoadInstance"] = doc.pop("clientXRoadInstance")
                doc["memberClass"] = doc.pop("clientMemberClass")
                doc["memberCode"] = doc.pop("clientMemberCode")
                new_list.append(doc)

        return new_list

    @staticmethod
    def remove_excluded(list_of_documents, list_of_exclusions):
        """
        Remove all the excluded memberCodes from all the elements in the documents list.
        :param list_of_documents: list of documents to be processed.
        :param list_of_exclusions: list of memberCodes to be excluded.
        :return: Return a list of documents that has the required memberCodes removed.
        """
        final_list = []

        for document in list_of_documents:
            if 'clientMemberCode' in document['_id']:
                if document['_id']['clientMemberCode'] not in list_of_exclusions:
                    final_list.append(document)
            if 'serviceMemberCode' in document['_id']:
                if document['_id']['serviceMemberCode'] not in list_of_exclusions:
                    final_list.append(document)

        return final_list

    @staticmethod
    def generate_top(list_of_documents, number_of_results):
        """
        Sort the list of documents by count and keep only the top number_of_results documents.
        :param list_of_documents: Documents list.
        :param number_of_results: Number of results to be kept in the resulting list.
        :return: Returns the sorted list of number_of_results top documents.
        """
        new_list = sorted(list_of_documents, key=itemgetter('count'), reverse=True)
        return new_list[:number_of_results]

    @staticmethod
    def get_translations(x_road_instance, member_class, member_code, subsystem_code, translations_list):
        """
        Gets translations for the specified parameters.
        :param x_road_instance: The xRoadInstance string.
        :param member_class: The memberClass string.
        :param member_code: The memberCode string.
        :param subsystem_code: The subsystemCode string.
        :param translations_list: The list of dictionaries with the data including translations.
        :return: Returns estonian and/or english translations if found.
        """
        translate_et = translate_en = '{0}/{1}/{2}/{3}'.format(x_road_instance, member_class, member_code, subsystem_code)

        for doc in translations_list:
            if doc['x_road_instance'] == x_road_instance \
                    and doc['member_class'] == member_class \
                    and doc['member_code'] == member_code \
                    and doc['subsystem_code'] == subsystem_code:
                if (doc['subsystem_name']['et']):
                    translate_et = doc['subsystem_name']['et']
                if (doc['subsystem_name']['en']):
                    translate_en = doc['subsystem_name']['en']
                return translate_et, translate_en

        return translate_et, translate_en

    @staticmethod
    def get_member_name_translations(x_road_instance, member_class, member_code, translations_list):
        """
        Gets translations for the specified parameters.
        :param x_road_instance: The xRoadInstance string.
        :param member_class: The memberClass string.
        :param member_code: The memberCode string.
        :param translations_list: The list of dictionaries with the data including translations.
        :return: Returns estonian and/or english translations if found.
        """
        translate_et = '{0}/{1}/{2}'.format(x_road_instance, member_class, member_code)

        for doc in translations_list:
            if doc['x_road_instance'] == x_road_instance \
                    and doc['member_class'] == member_class \
                    and doc['member_code'] == member_code:
                if (doc['member_name']):
                    translate_et = doc['member_name']
                return translate_et

        return translate_et

    def create_results_document(self):
        """
        Creates the resulting json document.
        :return: Returns the finished json document.
        """
        results_document = {
            "stats": {
                "{0}".format(time_date_tools.string_to_date(self.start_date).year): {
                    "months": {
                        "{0}".format(time_date_tools.string_to_date(self.start_date).month): {
                            "query_count": self.query_count, "service_count": self.service_count,
                            "producer_count": self.producer_count, "member_count": self.member_count,
                            "gov_member_count": self.gov_member_count, "subsystem_count": self.subsystem_count,
                            "secsrv_count": self.sec_srv_services, "producers_top": self.producers_top,
                            "consumers_top": self.consumers_top
                        }
                    }
                }
            }
        }
        return results_document

    def write_facts_to_file(self):
        """
        Writes the factsheet to a file that's path is defined in the settings file.
        :return:
        """
        if not os.path.isdir(self.file_path):
            os.makedirs(self.file_path)

        creation_time = time_date_tools.datetime_to_modified_string(datetime.datetime.now())

        with open(self.file_path + self.start_date + "_" + self.end_date + "_" + creation_time + ".txt",
                  'w') as outfile:
            json.dump(self.create_results_document(), outfile, indent=4)

    def format_top_producers(self, list_of_producers):
        """
        Formats the list of consumers to a nice readable format.
        :param list_of_producers: List of producers to be formatted.
        :return: Returns a formatted dictionary of the producers.
        """
        i = 0
        result_dict = {}
        for producer in list_of_producers:
            i += 1
            result_dict[str(i)] = {}
            name_est, name_eng = self.get_translations(producer["_id"]["serviceXRoadInstance"],
                                                       producer["_id"]["serviceMemberClass"],
                                                       producer["_id"]["serviceMemberCode"],
                                                       producer["_id"]["serviceSubsystemCode"],
                                                       self.member_subsystem_info)
            result_dict[str(i)]["code"] = '{0}/{1}/{2}/{3}'.format(producer["_id"]["serviceXRoadInstance"],
                                                                   producer["_id"]["serviceMemberClass"],
                                                                   producer["_id"]["serviceMemberCode"],
                                                                   producer["_id"]["serviceSubsystemCode"])
            result_dict[str(i)]["name_est"] = name_est
            result_dict[str(i)]["name_eng"] = name_eng
            result_dict[str(i)]["query_count"] = producer["count"]

        return result_dict

    def format_top_consumers(self, list_of_consumers):
        """
        Formats the list of consumers to a nice readable format.
        :param list_of_consumers: List of consumers to be formatted.
        :return: Returns a formatted dictionary of the consumers.
        """
        i = 0
        result_dict = {}
        for consumer in list_of_consumers:
            i += 1
            result_dict[str(i)] = {}
            name_est = self.get_member_name_translations(consumer["_id"]["clientXRoadInstance"],
                                                         consumer["_id"]["clientMemberClass"],
                                                         consumer["_id"]["clientMemberCode"],
                                                         self.member_subsystem_info)
            result_dict[str(i)]["code"] = '{0}/{1}/{2}'.format(consumer["_id"]["clientXRoadInstance"],
                                                               consumer["_id"]["clientMemberClass"],
                                                               consumer["_id"]["clientMemberCode"])
            result_dict[str(i)]["name_est"] = name_est
            result_dict[str(i)]["query_count"] = consumer["count"]

        return result_dict

    def get_query_count(self):
        """
        Get the overall number of queries and set the query_count value.
        :return:
        """
        start_processing_time = time.time()
        self.logger_manager.log_info('FactsheetManager', 'Start get_query_count')
        documents_within_time_frame = self.database_manager.get_documents_within_time_frame(self.start_date_timestamp,
                                                                                            self.end_date_timestamp)
        if len(documents_within_time_frame) > 0:
            self.query_count = documents_within_time_frame[0]["count"]
        else:
            self.query_count = 0
        print("Query count: {0}".format(self.query_count))
        self.logger_manager.log_info('FactsheetManager', 'End get_query_count')
        end_processing_time = time.time()
        processing_time = time.strftime("%H:%M:%S", time.gmtime(end_processing_time - start_processing_time))
        self.logger_manager.log_info('FactsheetManager', 'Duration get_query_count {0}'.format(processing_time))

    def get_service_count(self):
        """
        Get the overall number of services and set the service_count value.
        :return:
        """
        start_processing_time = time.time()
        self.logger_manager.log_info('FactsheetManager', 'Start get_service_count')
        self.service_count = len(self.database_manager.get_services(self.start_date_timestamp, self.end_date_timestamp))
        print("Service count: {0}".format(self.service_count))
        self.logger_manager.log_info('FactsheetManager', 'End get_service_count')
        end_processing_time = time.time()
        processing_time = time.strftime("%H:%M:%S", time.gmtime(end_processing_time - start_processing_time))
        self.logger_manager.log_info('FactsheetManager', 'Duration get_service_count {0}'.format(processing_time))

    def get_producer_count(self):
        """
        Get the overall number of producers and set the producer_count value.
        :return:
        """
        start_processing_time = time.time()
        self.logger_manager.log_info('FactsheetManager', 'Start get_producer_count')
        self.producer_count = len(
            self.database_manager.get_producers(self.start_date_timestamp, self.end_date_timestamp))
        print("Producer count: {0}".format(self.producer_count))
        self.logger_manager.log_info('FactsheetManager', 'End get_producer_count')
        end_processing_time = time.time()
        processing_time = time.strftime("%H:%M:%S", time.gmtime(end_processing_time - start_processing_time))
        self.logger_manager.log_info('FactsheetManager', 'Duration get_producer_count {0}'.format(processing_time))

    def get_member_count(self):
        """
        Get the overall number of members and set the member_count value.
        :return:
        """
        start_processing_time = time.time()
        self.logger_manager.log_info('FactsheetManager', 'Start get_member_count')
        service_member_count = self.database_manager.get_service_members(self.start_date_timestamp,
                                                                         self.end_date_timestamp)
        client_member_count = self.database_manager.get_client_members(self.start_date_timestamp,
                                                                       self.end_date_timestamp)

        unified_service_member_list = self.unify_service_members(service_member_count)
        unified_client_member_list = self.unify_client_members(client_member_count)

        self.member_count = len(self.get_unique_set(unified_service_member_list, unified_client_member_list))
        print("Member count: {0}".format(self.member_count))
        self.logger_manager.log_info('FactsheetManager', 'End get_member_count')
        end_processing_time = time.time()
        processing_time = time.strftime("%H:%M:%S", time.gmtime(end_processing_time - start_processing_time))
        self.logger_manager.log_info('FactsheetManager', 'Duration get_member_count {0}'.format(processing_time))

    def get_gov_member_count(self):
        """
        Get the overall number of GOV members and set the gov_member_count value.
        :return:
        """
        start_processing_time = time.time()
        self.logger_manager.log_info('FactsheetManager', 'Start get_gov_member_count')
        service_member_count = self.database_manager.get_service_members(self.start_date_timestamp,
                                                                         self.end_date_timestamp)
        client_member_count = self.database_manager.get_client_members(self.start_date_timestamp,
                                                                       self.end_date_timestamp)

        unified_service_member_list_gov = self.unify_service_members(service_member_count, True)
        unified_client_member_list_gov = self.unify_client_members(client_member_count, True)

        self.gov_member_count = len(
            self.get_unique_set(unified_service_member_list_gov, unified_client_member_list_gov))
        print("Gov member count: {0}".format(self.gov_member_count))
        self.logger_manager.log_info('FactsheetManager', 'End get_gov_member_count')
        end_processing_time = time.time()
        processing_time = time.strftime("%H:%M:%S", time.gmtime(end_processing_time - start_processing_time))
        self.logger_manager.log_info('FactsheetManager', 'Duration get_get_gov_member_count {0}'.format(processing_time))

    def get_subsystem_count(self):
        """
        Get the overall number of subsystems and set the subsystem_count value.
        :return:
        """
        start_processing_time = time.time()
        self.logger_manager.log_info('FactsheetManager', 'Start get_subsystem_count')
        service_subsystems = self.database_manager.get_service_subsystems(self.start_date_timestamp,
                                                                          self.end_date_timestamp)
        client_subsystems = self.database_manager.get_client_subsystems(self.start_date_timestamp,
                                                                        self.end_date_timestamp)

        unified_service_subsystems = self.unify_service_subsystems(service_subsystems)
        unified_client_subsystems = self.unify_client_subsystems(client_subsystems)

        self.subsystem_count = len(self.get_unique_set(unified_service_subsystems, unified_client_subsystems))
        print("Subsystem count: {0}".format(self.subsystem_count))
        self.logger_manager.log_info('FactsheetManager', 'End get_subsystem_count')
        end_processing_time = time.time()
        processing_time = time.strftime("%H:%M:%S", time.gmtime(end_processing_time - start_processing_time))
        self.logger_manager.log_info('FactsheetManager', 'Duration get_subsystem_count {0}'.format(processing_time))

    def get_sec_srv_services(self):
        """
        Get the overall number of security servers and set the sec_srv_values value.
        :return:
        """
        start_processing_time = time.time()
        self.logger_manager.log_info('FactsheetManager', 'Start get_sec_srv_services')
        sec_srv_services_list = self.database_manager.get_sec_srv_service_count(self.start_date_timestamp,
                                                                                self.end_date_timestamp)
        sec_srv_clients_list = self.database_manager.get_sec_srv_client_count(self.start_date_timestamp,
                                                                              self.end_date_timestamp)

        unified_sec_srv_services = self.unify_sec_srv(sec_srv_services_list, True)
        unified_sec_srv_clients = self.unify_sec_srv(sec_srv_clients_list)

        self.sec_srv_services = len(self.get_unique_set(unified_sec_srv_services, unified_sec_srv_clients))
        print("Secsrv_count: {0}".format(self.sec_srv_services))
        self.logger_manager.log_info('FactsheetManager', 'End get_sec_srv_services')
        end_processing_time = time.time()
        processing_time = time.strftime("%H:%M:%S", time.gmtime(end_processing_time - start_processing_time))
        self.logger_manager.log_info('FactsheetManager', 'Duration get_sec_srv_services {0}'.format(processing_time))

    def get_producers_top(self):
        """
        Get all the producers and their representative counts and set the producers_top value.
        :return:
        """
        start_processing_time = time.time()
        self.logger_manager.log_info('FactsheetManager', 'Start get_producers_top')
        producers_top_list = self.database_manager.get_service_subsystems(self.start_date_timestamp,
                                                                          self.end_date_timestamp)
        final_producers_top = self.generate_top(producers_top_list, self.number_of_top_producers)
        self.producers_top = self.format_top_producers(final_producers_top)
        print("Producers top: {0}".format(self.producers_top))
        self.logger_manager.log_info('FactsheetManager', 'End get_producers_top')
        end_processing_time = time.time()
        processing_time = time.strftime("%H:%M:%S", time.gmtime(end_processing_time - start_processing_time))
        self.logger_manager.log_info('FactsheetManager', 'Duration get_producers_top {0}'.format(processing_time))

    def get_consumers_top(self):
        """
        Get all the consumers and their representative counts and set the consumers_top value.
        :return:
        """
        start_processing_time = time.time()
        self.logger_manager.log_info('FactsheetManager', 'Start get_consumers_top')
        consumers_top_list = self.database_manager.get_client_members(self.start_date_timestamp,
                                                                      self.end_date_timestamp)
        consumers_top_list = self.remove_excluded(consumers_top_list, self.excluded_member_codes)
        final_consumers_top = self.generate_top(consumers_top_list, self.number_of_top_consumers)
        self.consumers_top = self.format_top_consumers(final_consumers_top)
        print("Consumers top: {0}".format(self.consumers_top))
        self.logger_manager.log_info('FactsheetManager', 'End get_consumers_top')
        end_processing_time = time.time()
        processing_time = time.strftime("%H:%M:%S", time.gmtime(end_processing_time - start_processing_time))
        self.logger_manager.log_info('FactsheetManager', 'Duration get_consumers_top {0}'.format(processing_time))

    def get_facts(self):
        """
        Do all the FactSheet processes and set all the values.
        :return:
        """
        self.get_query_count()
        self.get_service_count()
        self.get_producer_count()
        self.get_member_count()
        self.get_gov_member_count()
        self.get_subsystem_count()
        self.get_sec_srv_services()
        self.get_producers_top()
        self.get_consumers_top()
