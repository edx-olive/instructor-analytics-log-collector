"""
Module for the provide general access to the storage for the logs (i.e. mySql).
"""

from abc import ABCMeta, abstractmethod
import hashlib
import json
import logging

from django.db import OperationalError

from rg_instructor_analytics_log_collector.models import LogTable, ProcessedZipLog

log = logging.getLogger(__name__)


class IRepository(metaclass=ABCMeta):
    """
    Base repository class.
    """

    def _get_logs_batch_size(self):
        """
        Provide batch size for the bulk operation.
        """
        return 1024

    @abstractmethod
    def get_processed_zip_files(self):
        """
        Return list of the files, that already processed.
        """
        pass

    def add_new_log_records(self, log_file_descriptor):
        """
        Parse the list of raw string into records inside a database.
        """
        for log_string in log_file_descriptor:
            try:
                if type(log_string) is not str:
                    # it is bytes in python 3
                    log_string = log_string.decode('utf-8')
                json_log = json.loads(log_string)
                data = {
                    'message_type': 'event_type' in json_log and json_log['event_type'] or json_log['name'],
                    'log_time': 'time' in json_log and json_log['time'] or json_log['timestamp'],
                    'log_message': log_string,
                    'user_name': json_log.get('username', json_log.get('context', {}).get('username'))
                }
                try:
                    m_hash = hashlib.sha256(data['message_type']).hexdigest()
                except TypeError:
                    m_hash = hashlib.sha256(data['message_type'].encode('utf-8')).hexdigest()
                data['message_type_hash'] = m_hash
            except ValueError as e:
                log.error('can not parse json from the log string ({})\n\t{}'.format(log_string, repr(e)))
            except (IndexError, KeyError) as e:
                log.exception('corrupted structure of the log json ({})\n\t{}'.format(log_string, repr(e)))
            else:
                self.store_new_log_message(data)

    @abstractmethod
    def store_new_log_message(self, data):
        """
        Store list of the parsed log record into the database.
        """
        pass

    @abstractmethod
    def mark_as_processed_source(self, source_name):
        """
        Mark zip file as processed.
        """
        pass


class MySQlRepository(IRepository):
    """
    Implementation of the repository for the mySql.
    """

    def get_processed_zip_files(self):
        """
        Return list of the file names, that already was processed.
        """
        return ProcessedZipLog.objects.values_list('file_name', flat=True)

    def store_new_log_message(self, data):
        """
        Store parsed logs into the database.
        """
        # FIXME: try - except block was added to prevent unnecessary error related to the MySQL inability to support
        #  UTF-8 (MySQL has a 3 byte limit on utf-8 characters while 4 byte support is needed). Since events with the
        #  event_type in unicode are not looked as mandatory for our analytics reports we could stay with the current
        #  solution. The proper fix proposal is discussed in the YT issue, please fide it by the link
        #  https://youtrack.raccoongang.com/issue/RGA-242?p=RGA2-424
        try:
            LogTable.objects.get_or_create(
                message_type_hash=data['message_type_hash'],
                log_time=data['log_time'],
                user_name=data['user_name'],
                defaults={'log_message': data['log_message'], 'message_type': data['message_type']}
            )
        except OperationalError:
            log.exception(f"Cannot store the record into database ({data['log_message']})")

    def mark_as_processed_source(self, source_name):
        """
        Mark given file name as processed.
        """
        ProcessedZipLog.objects.get_or_create(file_name=source_name)
