import time
from multiprocessing import Manager, Process

from correctorlib.corrector_batch import CorrectorBatch
from correctorlib.logger_manager import LoggerManager
from settings import Settings

if __name__ == '__main__':
    """
    The main method.
    """
    settings = Settings()
    logger_m = LoggerManager(settings.LOGGER_NAME, settings.MODULE)
    corrector_version = logger_m.__version__

    # Runs Corrector in infinite Loop
    while True:
        try:
            c_batch = CorrectorBatch(settings)
            manager = Manager()
            process_dict = manager.dict()
            process_dict['doc_len'] = -1

            print('Corrector Service [{0}] - Batch timestamp: {1}'.format(corrector_version, int(time.time())))
            p = Process(target=c_batch.run, args=(process_dict,))
            p.start()
            p.join()

            if process_dict['doc_len'] == -1:
                logger_m.log_error('corrector_main',
                                   'batch_corrector finished with error code. Restart in {0} seconds'.format(
                                       settings.WAIT_FROM_ERROR))
                logger_m.log_heartbeat("error", settings.HEARTBEAT_LOGGER_PATH, settings.HEARTBEAT_FILE, "FAILED")
                # After process error, waits WAIT_FROM_ERROR to restart batch
                time.sleep(settings.WAIT_FROM_ERROR)
            elif process_dict['doc_len'] < settings.CORRECTOR_DOCUMENTS_MIN:
                # If number of processed docs is smaller than CORRECTOR_DOCUMENTS_MIN,
                # waits WAIT_FROM_DONE to restart batch
                time.sleep(settings.WAIT_FROM_DONE)
        except Exception as e:
            logger_m.log_error('corrector_main', 'Internal error: {0}'.format(repr(e)))
            logger_m.log_heartbeat("error", settings.HEARTBEAT_LOGGER_PATH, settings.HEARTBEAT_FILE, "FAILED")
            # If here, it is not possible to restart the processing batch. Raise exception again
            raise e
