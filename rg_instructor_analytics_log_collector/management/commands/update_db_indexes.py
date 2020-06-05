from django.db import connection
from django.core.management.base import BaseCommand, CommandError

from rg_instructor_analytics_log_collector.models import CourseVisitsByDay, DiscussionActivityByDay, EnrollmentByDay, \
    LastCourseVisitByUser, VideoViewsByDay, VideoViewsByUser

INDEX_NAME_POSITION = 2
SEQ_IN_INDEX_POSITION = 3
COLUMN_NAME_POSITION = 4


def _get_indexes(table_cls):
    """
    :param table_cls: model class to get table name
    :return: dict in format {<index_name>: list[<column1>, ..., <columnN>}
    """
    with connection.cursor() as cursor:
        cursor.execute("SHOW INDEX FROM `{}`".format(table_cls._meta.db_table))
        rows = cursor.fetchall()

    indexes = {}
    for row in rows:
        index_name = row[INDEX_NAME_POSITION]
        column_name = row[COLUMN_NAME_POSITION]
        seq_in_index = row[SEQ_IN_INDEX_POSITION]
        # column position matters, but we can't be sure that we'll get entries
        # for an index consequently, that's why store column position in index
        # for further sorting
        if index_name not in indexes:
            indexes[index_name] = [(seq_in_index, column_name), ]
        else:
            indexes[index_name].append((seq_in_index, column_name), )

    for name, columns in indexes.items():
        indexes[name] = [n[1] for n in sorted(columns)]

    return indexes


def _create_index(table_cls, fields):
    rowsmark = '_'.join(fields)
    fields = ', '.join('`{}`'.format(f) for f in fields)
    table = table_cls._meta.db_table
    request = (
        'CREATE INDEX `rga2_log_collector_{tablemark}_{rowsmark}_idx` '
        'ON `{table}` ({fields})'
    ).format(
        tablemark=table.split('_')[-1],
        table=table,
        rowsmark=rowsmark, fields=fields
    )
    with connection.cursor() as cursor:
        cursor.execute(request)


def _create_index_if_missed(table_cls, fields):
    indexes = _get_indexes(table_cls)
    cnt = len(fields)
    if fields not in [v[:cnt] for v in indexes.values()]:
        # if index contains more columns than required, it's ok if
        # columns placed in right order
        print('Create index for model {} and columns {}'.format(table_cls, fields))
        _create_index(table_cls, fields)
    else:
        print('Index for {} and columns {} already exists'.format(table_cls, fields))


class Command(BaseCommand):
    help = 'Add missed multi-column indexes if absent'

    def handle(self, *args, **options):
        data = [
            (CourseVisitsByDay, ['course', 'day']),
            (DiscussionActivityByDay, ['course', 'day']),
            (EnrollmentByDay, ['course', 'day']),
            (VideoViewsByDay, ['course', 'day']),
            (VideoViewsByUser, ['course', 'user_id']),
        ]
        for table_cls, fields in data:
            _create_index_if_missed(table_cls, fields)
