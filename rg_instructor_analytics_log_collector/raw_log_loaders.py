"""
Module with loaders of the raw log files.
"""
import gzip
import logging
from os import listdir
from os.path import exists, isdir, join

log = logging.getLogger(__name__)


def run_ziped_file_loader(dir_name, repository, reload_logs=False):
    """
    Process zipped log files.

    :param dir_name: parent directory for the logs.
    :param repository: object that provide suitable storage for the processed logs.
    """
    if not exists(dir_name) or not isdir(dir_name):
        raise Exception("Can not find log directory by nex path: {}".format(dir_name))
    processed_files = repository.get_processed_zip_files()
    for f in sorted(listdir(dir_name), key=lambda f: (f == 'tracking.log', f)):
        if f == 'tracking.log':
            with open(join(dir_name, f), 'rb') as log_file:
                logging.info('Started process next log file: {}'.format(f))
                repository.add_new_log_records(log_file.readlines())
                logging.info('Finished process next log file: {}'.format(f))

        if not f.endswith('.gz') or not reload_logs and f in processed_files:
            continue

        with gzip.open(join(dir_name, f), 'rb') as log_file:
            logging.info('Started process next log file: {}'.format(f))
            repository.add_new_log_records(log_file.readlines())
            repository.mark_as_processed_source(f)
            logging.info('Finished process next log file: {}'.format(f))
