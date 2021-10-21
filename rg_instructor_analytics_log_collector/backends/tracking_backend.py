"""
Module with the backend for handling Live Event Tracking
"""
from logging import getLogger

from rg_instructor_analytics_log_collector.processors.processor import Processor

log = getLogger(__name__)


class RGAnalyticsBackend:
    """
    Event tracker backend that handle live events and store data into RG IA database.
    """
    processor = Processor(["enrollment", "video_views", "discussion", "student_step", "course_activity"])

    def send(self, event):
        """
        Handle and store event's data into the database.
        """
        try:
            event_data = {
                'message_type': 'event_type' in event and event['event_type'] or event['name'],
                'log_time': 'time' in event and event['time'] or event['timestamp'],
                'log_message': event,
            }
        except KeyError:
            log.exception(f'The structure of the event does not contain expected fields: {event}')
            return
        log.debug(f'RG LC processing following event: {event_data["message_type"]}')
        self.processor.process(event_data)
