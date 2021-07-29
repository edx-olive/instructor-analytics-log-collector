"""
Defines the abstract base class that all backends should be based on
"""
from abc import ABCMeta, abstractmethod
import gzip
import logging
from typing import Generator, Tuple

from rg_instructor_analytics_log_collector.processors.processor import Processor
from rg_instructor_analytics_log_collector.repository import MySQlRepository

logger = logging.getLogger(__name__)


class BaseLogCollectorBackend(metaclass=ABCMeta):
    """
    The base abstract class for all file storage backends.
    """
    repository = MySQlRepository()
    processor = Processor(["enrollment", "video_views", "discussion", "student_step", "course_activity"])

    def __init__(
        self,
        delete_logs: bool = False,
        reload_logs: bool = False,
        **kwargs
    ):
        self.delete_logs = delete_logs
        self.reload_logs = reload_logs
        # NOTE: streaming_read argument clarifying the process of reading tracking log files from the storage.
        #  If True the additional StreamReader class will be required to be setup from the codec library.
        #  Look at the `repository.IRepository.add_new_log_records` method for more details.
        self.streaming_read = False

    @abstractmethod
    def _get_sorted_files_for_processing(self) -> Generator[Tuple[str, ...], None, None]:
        """
        Abstract method for preparing a generator of sorted files to load and process.

        Depends on chosen backend storage.
        return: tuple[file_name, file_obj]
        """
        raise NotImplementedError

    def load_and_process(self):
        """
        Load and Process logs collected from the tracking log files.
        """
        files_for_processing = self._get_sorted_files_for_processing()

        for file_name, file in files_for_processing:
            is_archived = file_name.endswith('.gz')

            # Load part:
            open_func = gzip.open if is_archived else open
            logger.info(f'Started work with the next log file: {file_name}')

            # NOTE: gzip.open works fine with the streaming archived files and we need handle separately only unpacked
            #  files from file-storage services (for ex: s3)
            if self.streaming_read and not is_archived:
                self.repository.add_new_log_records(file, streaming_read=self.streaming_read)
            else:
                with open_func(file) as log_file:
                    self.repository.add_new_log_records(log_file)

            # Process part:
            if is_archived:
                self.repository.mark_as_processed_source(file_name)
            self.processor.process()
            if self.delete_logs and is_archived:
                self.processor.delete_logs()
            logger.info(f'Finished work with log file: {file_name}')
