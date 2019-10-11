"""
Collection of the video views pipeline.
"""
import json
import logging

from opaque_keys.edx.keys import CourseKey

from rg_instructor_analytics_log_collector.constants import Events
from rg_instructor_analytics_log_collector.models import LastProcessedLog, VideoViewsByBlock, VideoViewsByDay, \
    VideoViewsByUser
from rg_instructor_analytics_log_collector.processors.base_pipeline import BasePipeline

log = logging.getLogger(__name__)


class VideoViewsPipeline(BasePipeline):
    """VideoViews stats Processor."""

    alias = 'video_views'
    supported_types = Events.VIDEO_VIEW_EVENTS
    processor_name = LastProcessedLog.VIDEO_VIEWS

    def format(self, record):
        """Format raw log to the internal format."""
        event_body = json.loads(record.log_message)
        event_body_detail = json.loads(event_body['event'])
        try:
            data = {
                'course_id': event_body['context']['course_id'],
                'user_id': event_body['context']['user_id'],
                'block_id': event_body_detail['id'],
                'viewed_time': event_body_detail['currentTime'],
                'is_video_completed': True if record.message_type == Events.USER_FINISHED_WATCH_VIDEO else False,
                'log_time': record.log_time,
                'event_type': record.message_type
            }
        except KeyError:
            data = {}

        return data if self.is_valid(data) else None

    def is_valid(self, data):
        """
        Validate a log record.

        Returns:
            results of validation (bool)
        """
        return True if (
            data.get('user_id') and
            data.get('course_id') and
            data.get('block_id') and
            data.get('log_time') and
            data.get('event_type')
        ) else False

    def push_to_database(self, record):
        """Save Video Views info to the database."""
        course = CourseKey.from_string(record['course_id'])
        user_id = record['user_id']

        video_views_by_day, created_video_day = VideoViewsByDay.objects.get_or_create(
            course=course,
            video_block_id=record['block_id'],
            day=record['log_time'].date(),
        )
        list_users_ids = video_views_by_day.users_ids.split(',') if video_views_by_day.users_ids else []

        if created_video_day:
            video_views_by_day.users_ids = user_id
            video_views_by_day.total = 1
            video_views_by_day.save()

        elif str(user_id) not in list_users_ids:
            video_views_by_day.users_ids += ',{}'.format(user_id)
            video_views_by_day.total += 1
            video_views_by_day.save()

        video_views_by_user, created_video_views_by_user = VideoViewsByUser.objects.get_or_create(
            course=course,
            user_id=user_id,
            video_block_id=record['block_id'],
        )

        if not video_views_by_user.is_completed:
            try:
                viewed_time = int(record['viewed_time'])
            except ValueError:
                viewed_time = 0

            if viewed_time >= int(video_views_by_user.viewed_time):
                video_views_by_user.viewed_time = viewed_time
                video_views_by_user.is_completed = record['is_video_completed']
                video_views_by_user.save()

            video_views_by_block, _ = VideoViewsByBlock.objects.get_or_create(
                course=course,
                video_block_id=record['block_id'],
            )

            if created_video_views_by_user:
                video_views_by_block.count_part_viewed += 1
                video_views_by_block.save()

            if video_views_by_user.is_completed:
                video_views_by_block.count_full_viewed += 1
                video_views_by_block.count_part_viewed -= 1
                video_views_by_block.video_duration = video_views_by_user.viewed_time
                video_views_by_block.save()
