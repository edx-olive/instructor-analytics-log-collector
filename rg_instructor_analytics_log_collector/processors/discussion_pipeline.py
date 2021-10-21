"""
Collection of the discussion pipeline.
"""

import json
import logging

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey

from rg_instructor_analytics_log_collector.constants import Events
from rg_instructor_analytics_log_collector.models import DiscussionActivity, DiscussionActivityByDay, \
    LastProcessedLog
from rg_instructor_analytics_log_collector.processors.base_pipeline import BasePipeline

log = logging.getLogger(__name__)


class DiscussionPipeline(BasePipeline):
    """
    Discussion stats Processor.
    """

    alias = 'discussion'
    supported_types = Events.DISCUSSION_EVENTS
    processor_name = LastProcessedLog.DISCUSSION_ACTIVITY

    def format(self, record, live_event=False):
        """
        Format raw log to the internal format.

        record: could be QuerySet (or json object if live_event == True)
        """
        data = None
        event_body = record.get('log_message') if live_event else json.loads(record.log_message)

        try:
            course = CourseKey.from_string(event_body['context']['course_id'])
        except InvalidKeyError:
            pass
        else:
            data = {
                'event_type': record.get('message_type') if live_event else record.message_type,
                'user_id': event_body['context']['user_id'],
                'course': course,
                'category_id': event_body['event'].get('category_id'),
                'commentable_id': event_body['event']['commentable_id'],
                'discussion_id': event_body['event']['id'],
                'thread_type': event_body['event'].get('thread_type'),
                'log_time': record.get('log_time') if live_event else record.log_time
            }

        return data if data and self.is_valid(data) else None

    @staticmethod
    def is_valid(data):
        """
        Validate a log record.

        Returns:
            results of validation (bool)
        """
        return all((
            data.get('user_id'),
            data.get('commentable_id'),
            data.get('course'),
            data.get('event_type'),
            data.get('discussion_id'),
            data.get('log_time')
        ))

    def push_to_database(self, record):
        """
        Get or create Discussion Activities of User and by day.
        """
        disc_user_activity, disc_user_created = DiscussionActivity.objects.get_or_create(**record)
        if disc_user_created:
            disc_day_activity, disc_day_created = DiscussionActivityByDay.objects.get_or_create(
                course=disc_user_activity.course,
                day=disc_user_activity.log_time.date()
            )
            disc_day_activity.total = 1 if disc_day_created else (disc_day_activity.total + 1)
            disc_day_activity.save()
