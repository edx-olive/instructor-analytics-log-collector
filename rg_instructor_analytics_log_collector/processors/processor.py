"""
Processor module.
"""
from datetime import datetime
import logging
import time

from rg_instructor_analytics_log_collector.models import LastProcessedLog, LogTable
from rg_instructor_analytics_log_collector.processors.course_activity_pipeline import CourseActivityPipeline
from rg_instructor_analytics_log_collector.processors.discussion_pipeline import DiscussionPipeline
from rg_instructor_analytics_log_collector.processors.enrollment_pipeline import EnrollmentPipeline
from rg_instructor_analytics_log_collector.processors.student_step_pipeline import StudentStepPipeline
from rg_instructor_analytics_log_collector.processors.video_views_pipeline import VideoViewsPipeline

log = logging.getLogger(__name__)


class Processor(object):
    """
    Processor for read raw logs and push into pipelines.
    """

    available_pipelines = [
        EnrollmentPipeline(),
        VideoViewsPipeline(),
        DiscussionPipeline(),
        StudentStepPipeline(),
        CourseActivityPipeline(),
    ]

    def __init__(self, alias_list, sleep_time):
        """
        Construct Processor.

        :param alias_list: list of the pipelines that will be loaded to the current worker.
        :param sleep_time: size of the pause between read new portion of the raw logs.
        """
        super(Processor, self).__init__()
        self.sleep_time = sleep_time
        self.pipelinies = filter(lambda x: x.alias in alias_list, self.available_pipelines)

    def process(self):
        """
        Process records data.

        Fetch data records from pipelines and
        store them in a database.
        """
        for pipeline in self.pipelinies:
            logging.info('{} processor started at {}'.format(pipeline.alias, datetime.now()))
            records = pipeline.get_query()

            if not records.exists():
                logging.info('{} processor stopped at {} (no records)'.format(pipeline.alias, datetime.now()))
                continue

            for record in records:
                # Format raw log to the internal format.
                data_record = pipeline.format(record)

                if data_record:
                    pipeline.push_to_database(data_record)
                pipeline.update_last_processed_log(record)
            logging.info('{} processor stopped at {}'.format(pipeline.alias, datetime.now()))

    def delete_logs(self):
        """Delete all unused log records."""
        last_date = LastProcessedLog.get_last_date()
        if last_date:
            logging.info('Deleting old log records...')
            LogTable.objects.filter(log_time__lt=last_date).delete()

    def run(self, delete_logs=False):
        """Run loop of the processor."""
        while True:
            self.process()
            if delete_logs:
                self.delete_logs()
            time.sleep(self.sleep_time)
