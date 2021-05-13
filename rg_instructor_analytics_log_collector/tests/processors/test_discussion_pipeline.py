"""Test discussion pipeline logic."""
import logging
from unittest import TestCase

from ddt import ddt, file_data, unpack
from mock import patch

from rg_instructor_analytics_log_collector.processors.discussion_pipeline import CourseKey
from rg_instructor_analytics_log_collector.processors.discussion_pipeline import DiscussionPipeline
from rg_instructor_analytics_log_collector.tests.processors.pipeline_test_utils import TestRecord


@ddt
class TestDiscussionPipeline(TestCase):
    """Test `DiscussionPipeline` logic."""

    def setUp(self):
        """Prepare a test pipeline."""
        logging.disable(logging.DEBUG)
        self.pipeline = DiscussionPipeline()

    @file_data("test_resources/test_discussion_pipeline_records.json")
    @unpack
    def test_is_valid(self, entry):
        """Test a validator."""
        self.assertEqual(self.pipeline.is_valid(entry.get("data")), entry.get("is_valid"))

    @patch.object(CourseKey, "from_string")
    def test_format(self, mock_course_key):
        """Test data preparation (formatting) method."""
        mock_course_key.return_value = "course_key"
        self.assertEqual(self.pipeline.format(TestRecord(record_type="discussion")),
                         {'event_type': TestRecord.EVENT_TYPE,
                          'user_id': TestRecord.USER_ID,
                          'course': "course_key",
                          'category_id': "test_category_id",
                          'commentable_id': "test_commentable_id",
                          'discussion_id': "test_discussion_id",
                          'thread_type': 'test_thread_type',
                          'log_time': TestRecord.LOG_TIME})

    def tearDown(self):
        """Re-enable logging."""
        logging.disable(logging.NOTSET)
