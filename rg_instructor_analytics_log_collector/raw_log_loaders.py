"""
Module with loaders of the raw log files.
"""
import gzip
import logging
from os import listdir
from os.path import exists, getctime, isdir, join

log = logging.getLogger(__name__)


def _get_sorted_files_for_processing(dir_name, repository, reload_logs):
    if not exists(dir_name) or not isdir(dir_name):
        raise Exception("Can not find log directory by nex path: {}".format(dir_name))

    if reload_logs:
        files = [f for f in listdir(dir_name) if f.endswith('.gz') or f.endswith('.log')]
    else:
        processed_files = repository.get_processed_zip_files()
        files = [f for f in listdir(dir_name)
                 if (f.endswith('.gz') or f.endswith('.log')) and f not in processed_files]

    return sorted(files, key=lambda f: getctime(join(dir_name, f)))


def load_and_process(dir_name, repository, processor, delete_logs, reload_logs=False):
    """
    Process log files.

    :param dir_name: parent directory for the logs.
    :param repository: object that provide suitable storage for the processed logs.
    :param processor: object for read raw logs and push into pipelines.
    :param delete_logs: bool, True for deleting logs after archived file is parsed.
    :param reload_logs: bool, True for processing archived logs even if they are already processed.
    """
    files_for_processing = _get_sorted_files_for_processing(dir_name, repository, reload_logs)

    for f in files_for_processing:
        is_archived = f.endswith('.gz')
        open_func = gzip.open if is_archived else open

        with open_func(join(dir_name, f), 'rb') as log_file:
            logging.info('Started process next log file: {}'.format(f))
            repository.add_new_log_records(log_file)
        if is_archived:
            repository.mark_as_processed_source(f)
        processor.process()
        if delete_logs and is_archived:
            processor.delete_logs()
        logging.info('Finished process next log file: {}'.format(f))
