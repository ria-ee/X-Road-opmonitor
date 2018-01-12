import sys

import ../settings
from ../collectorlib.logger_manager import LoggerManager

if __name__ == '__main__':
    """
    The error handler for handling bash script errors and to log into heartbeat & log.
    """
    args = sys.argv

    logger_m = LoggerManager(settings.LOGGER_NAME, 'collector_module')
    logger_m.log_error('running_make_riha', args[1])
    logger_m.log_heartbeat('running_make_riha: {0}'.format(args[1]), settings.HEARTBEAT_LOGGER_PATH,
                           settings.FACTSHEET_HEARTBEAT_NAME, "FAILED")
