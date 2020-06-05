"""
Enterpoint.
"""
import argparse
import time

import django
django.setup()

from rg_instructor_analytics_log_collector.processors.processor import Processor
from rg_instructor_analytics_log_collector.raw_log_loaders import load_and_process
from rg_instructor_analytics_log_collector.repository import MySQlRepository


def main():
    """
    Start app.
    """
    parser = argparse.ArgumentParser(
        description='App for load logs records in to mysql'
    )
    parser.add_argument(
        '--tracking_log_dir',
        action="store",
        dest="tracking_log_dir",
        type=str,
        default='/edx/var/log/tracking'
    )
    parser.add_argument(
        '--sleep_time',
        action="store",
        dest="sleep_time",
        help="Time between refreshing statistic(in seconds)",
        type=int,
        default=300
    )
    parser.add_argument('--reload-logs', action="store_true", help='Reload all logs from files into database')
    parser.add_argument(
        '--delete-logs', action="store_true",
        help='Delete unused log records from database (after archived files processing only)'
    )

    arg = parser.parse_args()

    repository = MySQlRepository()
    processor = Processor(
        ["enrollment", "video_views", "discussion", "student_step", "course_activity"],
        arg.sleep_time
    )

    # separate first run to apply reload_logs if passed
    load_and_process(
        arg.tracking_log_dir, repository, processor,
        reload_logs=arg.reload_logs, delete_logs=arg.delete_logs
    )
    time.sleep(arg.sleep_time)

    while True:
        load_and_process(arg.tracking_log_dir, repository, processor, delete_logs=arg.delete_logs)
        time.sleep(arg.sleep_time)


if __name__ == "__main__":
    main()
