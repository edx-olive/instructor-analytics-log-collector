"""
Collection of the course activity pipeline.
"""
import json
import logging

from opaque_keys.edx.keys import CourseKey

from rg_instructor_analytics_log_collector.models import CourseVisitsByDay, LastCourseVisitByUser, LastProcessedLog, \
    LogTable
from rg_instructor_analytics_log_collector.processors.base_pipeline import BasePipeline

log = logging.getLogger(__name__)


class CourseActivityPipeline(BasePipeline):
    """
    Course Activity stats Processor.
    """

    alias = 'course_activity'
    processor_name = LastProcessedLog.COURSE_ACTIVITY

    def get_query(self):
        """
        Return list of the raw logs with type, that suitable for the given pipeline.
        """
        query = LogTable.objects.all()
        last_processed_log_date = self.retrieve_last_date()

        if last_processed_log_date:
            query = query.filter(log_time__gt=last_processed_log_date)

        return query.order_by('created')

    def format(self, record):
        """
        Format raw log to the internal format.
        """
        data = None
        event_body = json.loads(record.log_message)
        try:
            course_id = event_body['context']['course_id']
            user_id = event_body['context']['user_id']
        except KeyError:
            return data
        else:
            if course_id and user_id:
                data = {'course_id': course_id, 'user_id': user_id, 'log_time': record.log_time}

        return data if data and self.is_valid(data) else None

    def is_valid(self, data):
        """
        Validate a log record.

        Returns:
            results of validation (bool)
        """
        return True if (
            data.get('user_id') and
            data.get('course_id') and
            data.get('log_time')
        ) else False

    def push_to_database(self, record):
        """
        Save Course Activity info to the database.
        """
        course = CourseKey.from_string(record['course_id'])
        user_id = str(record['user_id'])
        log_time = record['log_time']

        last_visit_by_user, created_last_visit = LastCourseVisitByUser.objects.get_or_create(
            course=course,
            user_id=user_id,
            defaults={'log_time': log_time}
        )

        if not created_last_visit and last_visit_by_user.log_time < log_time:
            last_visit_by_user.log_time = log_time
            last_visit_by_user.save()

        course_visits_by_day, created_course_visits = CourseVisitsByDay.objects.get_or_create(
            course=course,
            day=log_time.date(),
        )

        list_users_ids = course_visits_by_day.users_ids.split(',') if course_visits_by_day.users_ids else []

        if user_id not in list_users_ids:
            course_visits_by_day.users_ids += ',{}'.format(user_id) if list_users_ids else user_id
            course_visits_by_day.total += 1
            course_visits_by_day.save()
