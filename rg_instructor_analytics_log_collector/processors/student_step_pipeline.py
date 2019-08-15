"""
Collection of the discussion pipeline.
"""

import json
import logging

try:
    from openedx.core.release import RELEASE_LINE
except ImportError:
    RELEASE_LINE = 'ficus'

if RELEASE_LINE == 'hawthorn':
    from django.urls import resolve
    from django.urls.resolvers import Resolver404
else:
    from django.core.urlresolvers import resolve, Resolver404

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey, UsageKey
from six.moves.urllib.parse import urlparse

from rg_instructor_analytics_log_collector.constants import Events
from rg_instructor_analytics_log_collector.models import LastProcessedLog, StudentStepCourse
from rg_instructor_analytics_log_collector.processors.base_pipeline import BasePipeline
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError

log = logging.getLogger(__name__)


class StudentStepPipeline(BasePipeline):
    """
    StudentStep stats Processor.
    """

    alias = 'student_step'
    supported_types = Events.NAVIGATIONAL_EVENTS
    processor_name = LastProcessedLog.STUDENT_STEP

    def get_units(self, event_body, event_type, body_context):
        """
        Get info of student path by units.
        """
        current_unit = None
        target_unit = None
        subsection_id = event_body.get('id')

        if event_type == Events.UI_LINK_CLICKED:
            relative_url = urlparse(event_body.get('target_url', '')).path
            try:
                url = resolve(relative_url)
            except Resolver404:
                logging.info('Target URL "{}" not found.'.format(relative_url))
                return current_unit, target_unit, subsection_id
            else:
                if url.url_name != 'jump_to' or 'location' not in url.kwargs:
                    logging.info('Target URL "{}" is not "jump_to".'.format(relative_url))
                    return current_unit, target_unit, subsection_id

            target_location = UsageKey.from_string(url.kwargs['location'])
            target_unit = target_location.block_id

            try:
                last_step = StudentStepCourse.objects.filter(
                    user_id=body_context['user_id'],
                    course=target_location.course_key
                ).order_by('-log_time').first()
            except TypeError as err:
                logging.info('Course key type error: {}'.format(err))
                return None, None, subsection_id

            current_unit = last_step and last_step.target_unit

            if current_unit == target_unit:
                logging.info('Student has not moved anywhere.')
                return None, None, subsection_id

            if not last_step or last_step.event_type not in Events.INTERNAL_NAVIGATION_EVENTS:
                try:
                    course = modulestore().get_course(target_location.course_key, depth=1)
                except ItemNotFoundError as err:
                    logging.info('Course {} not found.'.format(err))
                    return None, None, subsection_id
                else:
                    if not course:
                        logging.info('Course {} not found.'.format(target_location.course_key))
                        return None, None, subsection_id

                for section in course.get_children():
                    if subsection_id:
                        break

                    for subsection in section.get_children():
                        if current_unit in [c.location.block_id for c in subsection.get_children()]:
                            subsection_id = subsection.location.__str__()
                            break
            else:
                subsection_id = last_step.subsection_id

            return current_unit, target_unit, subsection_id
        else:
            try:
                sequential_locator = UsageKey.from_string(subsection_id)
            except InvalidKeyError as err:
                logging.info('InvalidKeyError (subsection_id - "{}") {}'.format(subsection_id, err))
                return current_unit, target_unit, subsection_id

            try:
                subsection_block = modulestore().get_item(sequential_locator, depth=1)
            except ItemNotFoundError as err:
                logging.info('Item {} not found.'.format(err))
                return current_unit, target_unit, subsection_id
            else:
                if not subsection_block:
                    logging.info('Item {} not found.'.format(subsection_id))
                    return current_unit, target_unit, subsection_id

        if event_type in Events.INTERNAL_NAVIGATION_EVENTS:
            current_tab = event_body['old']
            target_tab = event_body['new']
            unit_children = subsection_block.get_children()

            try:
                current_unit = unit_children[current_tab - 1].location.block_id
                target_unit = unit_children[target_tab - 1].location.block_id
            except IndexError:
                pass

        elif event_type == Events.UI_SEQ_NEXT:
            try:
                # last unit in subsection
                current_unit = subsection_block.get_children()[-1].location.block_id
            except IndexError:
                pass

            is_next_subsection = False
            section_block = subsection_block.get_parent()
            for subsection in section_block.get_children():
                if subsection.location.block_id == subsection_block.location.block_id:
                    is_next_subsection = True
                    continue

                if is_next_subsection:
                    try:
                        # first unit in next subsection
                        target_unit = subsection.get_children()[0].location.block_id
                    except IndexError:
                        target_unit = ''
                        pass

                    break

            if target_unit is None:
                is_next_section = False
                for section in section_block.get_parent().get_children():
                    if section.location.block_id == section_block.location.block_id:
                        is_next_section = True
                        continue

                    if is_next_section:
                        try:
                            # first unit in next section -> first subsection
                            target_unit = section.get_children()[0].get_children()[0].location.block_id
                        except IndexError:
                            pass

                        break

        elif event_type == Events.UI_SEQ_PREV:
            try:
                # first unit in subsection
                current_unit = subsection_block.get_children()[0].location.block_id
            except IndexError:
                pass

            prev_subsection = None
            section_block = subsection_block.get_parent()

            for subsection in section_block.get_children():

                if subsection.location.block_id == subsection_block.location.block_id:
                    if prev_subsection:
                        try:
                            # last unit in prev_subsection
                            target_unit = prev_subsection.get_children()[-1].location.block_id
                        except IndexError:
                            pass
                    break

                prev_subsection = subsection

            if prev_subsection is None:
                prev_section = None

                for section in section_block.get_parent().get_children():
                    if section.location.block_id == section_block.location.block_id:
                        if prev_section:
                            try:
                                # last unit in prev_section -> last subsection
                                target_unit = prev_section.get_children()[-1].get_children()[-1].location.block_id
                            except IndexError:
                                pass
                        break

                    prev_section = section

        return current_unit, target_unit, subsection_id

    def format(self, record):
        """
        Format raw log to the internal format.
        """
        event_body = json.loads(record.log_message)

        try:
            course = CourseKey.from_string(event_body['context']['course_id'])
        except InvalidKeyError:
            return None

        current_unit, target_unit, subsection_id = self.get_units(
            json.loads(event_body['event']),
            record.message_type,
            event_body['context']
        )
        data = {
            'event_type': record.message_type,
            'user_id': event_body['context']['user_id'],
            'course': course,
            'subsection_id': subsection_id,
            'current_unit': current_unit,
            'target_unit': target_unit,
            'log_time': record.log_time
        }
        return data if self.is_valid(data) else None

    def is_valid(self, data):
        """
        Validate a log record.

        Returns:
            results of validation (bool)
        """
        return True if (
            data.get('user_id') and
            data.get('current_unit') and
            data.get('target_unit') and
            data.get('subsection_id') and
            data.get('log_time') and
            data.get('course') and
            data.get('event_type')
        ) else False

    def push_to_database(self, record):
        """
        Get or create StudentStepCourse.
        """
        StudentStepCourse.objects.get_or_create(**record)
