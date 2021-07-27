"""
Defines the backend class to work with the tracking logs stored un the Azure Blob storage
"""
import gzip
from io import BytesIO
import logging
from typing import Generator, Tuple

from azure.storage.blob import BlobClient, ContainerClient, StorageStreamDownloader

from rg_instructor_analytics_log_collector.backends.base_backend import BaseLogCollectorBackend


logger = logging.getLogger(__name__)


class BlobBackend(BaseLogCollectorBackend):

    def __init__(self, conn_str, container_name, **kwargs):
        super().__init__(**kwargs)
        self.conn_str = conn_str
        self.container_name = container_name
        self.blob = ContainerClient.from_connection_string(
            conn_str=self.conn_str,
            container_name=self.container_name,
        )

    def _file_filter(self, file) -> bool:
        """
        Utility method to filter file objects from blob container.
        """
        is_tracking_log_file = file.name.split('.')[-1] in ('gz', 'log')
        if not self.reload_logs:
            return is_tracking_log_file and file.name not in self.repository.get_processed_zip_files()
        return is_tracking_log_file

    def _get_sorted_files_for_processing(self) -> Generator[Tuple[str, StorageStreamDownloader], None, None]:
        """
        Generator for tracking log files from Azure Blob.

        return: Generator of tuples: (file_name, <file StorageStreamDownloader from blob service>)
        """
        file_names = (
            file.name for file in sorted(self.blob.list_blobs(), key=lambda file: file.last_modified)
            if self._file_filter(file)
        )

        return (
            (f_name, BlobClient.from_connection_string(
                conn_str=self.conn_str,
                container_name=self.container_name,
                blob_name=f_name
            ).download_blob()) for f_name in file_names
        )

    def load_and_process(self):
        """
        Load and Process logs collected from the tracking log files.
        """
        files_for_processing = self._get_sorted_files_for_processing()

        for file_name, file in files_for_processing:
            is_archived = file_name.endswith('.gz')

            # Load part:
            logger.info(f'Started work with the next log file: {file_name}')

            file_descriptor = file.readall()
            if is_archived:
                with gzip.open(BytesIO(file_descriptor)) as log_file:
                    self.repository.add_new_log_records(log_file)
                self.repository.mark_as_processed_source(file_name)
            else:
                self.repository.add_new_log_records(file_descriptor.splitlines())

            self.processor.process()
            if self.delete_logs and is_archived:
                self.processor.delete_logs()
            logger.info(f'Finished work with log file: {file_name}')
