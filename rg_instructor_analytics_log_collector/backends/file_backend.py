"""
Defines the backend class to work with the tracking logs stored un the file system.
"""
import logging
from os import listdir
from os.path import exists, getctime, isdir, join
from typing import Generator, Tuple

from rg_instructor_analytics_log_collector.backends.base_backend import BaseLogCollectorBackend


logger = logging.getLogger(__name__)


class FileBackend(BaseLogCollectorBackend):

    def __init__(self, tracking_log_dir, **kwargs):
        super().__init__(**kwargs)
        self.tracking_log_dir = tracking_log_dir

    def _file_filter(self, file: str) -> bool:
        """
        Utility method to filter file objects from file system.

        return: (bool) is log file need to be processed.
        """
        is_tracking_log_file = file.split('.')[-1] in ('gz', 'log')
        if not self.reload_logs:
            return is_tracking_log_file and file not in self.repository.get_processed_zip_files()
        return is_tracking_log_file

    def _get_sorted_files_for_processing(self) -> Generator[Tuple[str, str], None, None]:
        """
        Generator for tracking log files from file system.

        return: Generator of tuples: (file_name, path_to_file)
        """
        if not exists(self.tracking_log_dir) or not isdir(self.tracking_log_dir):
            raise Exception(f"Can not find log directory by nex path: {self.tracking_log_dir}")

        files = (
            f for f in sorted(
                listdir(self.tracking_log_dir), key=lambda f: getctime(join(self.tracking_log_dir, f))
            ) if self._file_filter(f)
        )
        return ((file, join(self.tracking_log_dir, file)) for file in files)
