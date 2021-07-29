"""
Defines the backend class to work with the tracking logs stored un the S3 storage
"""
import logging
from typing import Generator, Tuple

import boto3 as boto3
from botocore.response import StreamingBody

from rg_instructor_analytics_log_collector.backends.base_backend import BaseLogCollectorBackend


logger = logging.getLogger(__name__)


class S3Backend(BaseLogCollectorBackend):

    def __init__(self, aws_access_key_id, aws_secret_access_key, bucket_name, **kwargs):
        super().__init__(**kwargs)
        self.s3 = boto3.resource(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.bucket = self.s3.Bucket(bucket_name)
        self.streaming_read = True

    def _file_filter(self, obj) -> bool:
        """
        Utility method to filter file objects from s3 bucket.
        """
        is_tracking_log_file = obj.key.split('.')[-1] in ('gz', 'log')
        if not self.reload_logs:
            return is_tracking_log_file and obj.key not in self.repository.get_processed_zip_files()
        return is_tracking_log_file

    def _get_sorted_files_for_processing(self) -> Generator[Tuple[str, StreamingBody], None, None]:
        """
        Generator for tracking log files from S3.

        return: Generator of tuples: (file_name, <file StreamingBody from s3 service>)
        """
        if self.bucket not in self.s3.buckets.all():
            raise Exception(f"Can not find required bucket: {self.bucket} in s3 service, please check access params.")
        objs = (
            obj for obj in sorted(self.bucket.objects.all(), key=lambda obj: obj.last_modified)
            if self._file_filter(obj)
        )

        return ((obj.key, obj.Object().get()['Body']) for obj in objs)
