"""
Collection of the base pipelines.
"""

from abc import ABCMeta, abstractmethod

from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.course_groups.models import CourseCohort

from rg_instructor_analytics_log_collector.models import LastProcessedLog, LogTable


class BasePipeline(object):
    """
    Base Pipeline.

    NOTE: After implementing new pipeline, add it to the Processor.
    """

    __metaclass__ = ABCMeta

    """
    Readable name of the pipeline.
    """
    alias = None

    """
    Supported log types list.
    See:
    https://edx.readthedocs.io/projects/devdata/en/stable/internal_data_formats/event_list.html#event-list
    """
    supported_types = None
    """
    Processor name for the last processed LogTable.
    """
    processor_name = None

    def retrieve_last_date(self):
        """
        Fetch the moment of time daily enrollments were lastly updated.

        :return: DateTime or None
        """
        last_processed_log_table = LastProcessedLog.objects.filter(
            processor=self.processor_name
        ).first()

        return last_processed_log_table and last_processed_log_table.log_table.log_time

    def get_query(self):
        """
        Return list of the raw logs with type, that suitable for the given pipeline.
        """
        query = LogTable.objects.filter(message_type__in=self.supported_types)
        last_processed_log_date = self.retrieve_last_date()

        if last_processed_log_date:
            query = query.filter(log_time__gt=last_processed_log_date)

        return query.order_by('log_time')

    def add_cohort_id(self, formatted_record):
        """
        Add the cohort_id to the formatted record if there's correspondend user and course in it.
        """
        course = formatted_record.get('course')
        user_id = formatted_record.get('user_id')
        cohort = None

        if not course or not isinstance(course, CourseKey) :
            course_id = course if course else formatted_record.get('course_id')
            course = CourseKey.from_string(course_id) if course_id else None

        if course and user_id:
            cohort = CourseCohort.objects.filter(
                course_user_group__users=user_id,
                course_user_group__course_id=course
            ).first()

        formatted_record['cohort_id'] = cohort.id if cohort else 0

    @abstractmethod
    def format(self, record):
        """
        Process raw message with different format to the single format.

        Note, if there no needs to change format set it as property, that equal to None.

        In case, when given record dosent relate to the given pipeline - return None.
        :param record:  raw log record.
        :return: dictionary with consistent structure.
        """
        pass

    @abstractmethod
    def push_to_database(self, formatted_record):
        """
        Push to db final result.
        """
        pass

    def update_last_processed_log(self, last_record):
        """
        Create or update last processed LogTable by Processor.
        """
        if last_record:
            LastProcessedLog.objects.update_or_create(processor=self.processor_name,
                                                      defaults={'log_table': last_record})
