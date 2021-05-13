"""Test the `Processor` module."""
import logging
from unittest import TestCase

from ddt import data, ddt, unpack
from mock import patch

from rg_instructor_analytics_log_collector.processors.base_pipeline import BasePipeline
from rg_instructor_analytics_log_collector.processors.processor import Processor
from rg_instructor_analytics_log_collector.processors.student_step_pipeline import StudentStepPipeline


class TestRecords:
    """
    Dummy iterator class.

    Also, certain business logic is overridden
    for testing purposes.
    """

    def __init__(self, records):
        """
        Init an object.

        Arguments:
            records: an iterable object.
        """
        self.records = records

    def __iter__(self):
        """
        Allow for iterating over test records.

        Returns:
            iterator object to iterate over test records.
        """
        try:
            return iter(self.records)
        except TypeError:
            print(self.records, " not iterable.")

    @staticmethod
    def exists():
        """Allow for overriding a namesake method."""
        return True


@ddt
class TestProcessor(TestCase):
    """Test `Processor` logic."""

    def setUp(self):
        """Prepare a test pipeline."""
        logging.disable(logging.DEBUG)
        # Doesn't matter which one to pick
        Processor.available_pipelines = [StudentStepPipeline()]
        self.processor = Processor(alias_list=["student_step"], sleep_time=1)

    @data(({"test_key": "test_value"}, [1, 2, 3], 3),
          ({"test_key": "test_value"}, [1, 2], 2),
          (None, [1, 2, 3], 0))
    @unpack
    @patch.object(BasePipeline, "get_query")
    @patch.object(StudentStepPipeline, "get_units")
    @patch.object(StudentStepPipeline, "format")
    @patch.object(StudentStepPipeline, "push_to_database")
    @patch.object(StudentStepPipeline, "update_last_processed_log")
    def test_process_push_to_database(self,
                                      format_data,
                                      records,
                                      times_called,
                                      mock_update_last_processed_log,
                                      mock_push_to_database,
                                      mock_format,
                                      mock_get_units,
                                      mock_get_query):
        """Ensure only significant data is pushed to a db."""
        mock_update_last_processed_log.return_value = None
        mock_push_to_database.return_value = None
        mock_get_units.return_value = (None, None, None)
        mock_get_query.return_value = TestRecords(records)

        mock_format.return_value = format_data

        self.processor.process()
        self.assertEqual(mock_push_to_database.call_count, times_called)

    def tearDown(self):
        """Re-enable logging."""
        logging.disable(logging.NOTSET)
