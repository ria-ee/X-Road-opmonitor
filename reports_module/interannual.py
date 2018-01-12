from . import settings
from .reportslib.interannual_manager import InterAnnualManager
from .reportslib.logger_manager import LoggerManager


def main(logger_manager):
    """
    The main method.
    :param logger_manager: LoggerManager object.
    :return:
    """
    logger_m.log_heartbeat(
        "in_progress", settings.HEARTBEAT_LOGGER_PATH, settings.INTERANNUAL_HEARTBEAT_NAME, "SUCCEEDED")
    interannual_factsheet_manager = InterAnnualManager(logger_manager)
    interannual_factsheet_manager.get_interannual_factsheet()
    logger_m.log_heartbeat("finished", settings.HEARTBEAT_LOGGER_PATH, settings.INTERANNUAL_HEARTBEAT_NAME, "SUCCEEDED")


if __name__ == '__main__':

    logger_m = LoggerManager(settings.LOGGER_NAME, 'interannual_factsheet_module')
    try:
        main(logger_m)
    except Exception as e:
        logger_m.log_error('running_interannual_factsheet_main', '{0}'.format(repr(e)))
        logger_m.log_heartbeat("error", settings.HEARTBEAT_LOGGER_PATH, settings.INTERANNUAL_HEARTBEAT_NAME, "FAILED")
        raise e
