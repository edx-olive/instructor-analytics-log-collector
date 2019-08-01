"""
Collection of the enrollment pipeline.
"""

import json
import logging

from django.db.models import F
from opaque_keys.edx.keys import CourseKey

from rg_instructor_analytics_log_collector.constants import Events
from rg_instructor_analytics_log_collector.models import EnrollmentByDay, LastProcessedLog
from rg_instructor_analytics_log_collector.processors.base_pipeline import BasePipeline

log = logging.getLogger(__name__)


class EnrollmentPipeline(BasePipeline):
    """
    Enrollment stats Processor.
    """

    alias = 'enrollment'
    supported_types = Events.ENROLLMENT_EVENTS
    processor_name = LastProcessedLog.ENROLLMENT

    def format(self, record):
        """
        Format raw log to the internal format.
        """
        event_body = json.loads(record.log_message)

        data = {
            'is_enrolled': record.message_type == Events.USER_ENROLLED,
            'user_id': event_body['event']['user_id'],
            'course': event_body['event']['course_id'],
            'log_time': record.log_time
        }
        self.add_cohort_id(data)
        return data if data and self.is_valid(data) else None

    def is_valid(self, data):
        """
        Validate a log record.

        Returns:
            results of validation (bool)
        """
        return True if (data.get('log_time') and data.get('course')) else False

    def push_to_database(self, record):
        """
        Save formatted message to the database.
        """
        course = CourseKey.from_string(record['course'])
        user_is_enrolled = record['is_enrolled']

        day_state, created = EnrollmentByDay.objects.get_or_create(
            course=course,
            cohort_id=record['cohort_id'],
            day=record['log_time'].date(),
        )

        enrollment_for_the_last_day = EnrollmentByDay.objects.filter(
            course=course,
            cohort_id=record['cohort_id'],
            day__lt=day_state.day
        ).order_by('day').last()

        enrollment_for_the_following_days = EnrollmentByDay.objects.filter(
            course=course,
            cohort_id=record['cohort_id'],
            day__gt=day_state.day
        )

        if user_is_enrolled:
            day_state.enrolled += 1
        else:
            day_state.unenrolled += 1

        if enrollment_for_the_last_day:
            day_state.total = enrollment_for_the_last_day.total + day_state.enrolled - day_state.unenrolled
        else:
            day_state.total = day_state.enrolled - day_state.unenrolled
        day_state.save()

        if enrollment_for_the_following_days:
            total_delta = 1 if user_is_enrolled else -1
            enrollment_for_the_following_days.update(total=F('total') + total_delta)
