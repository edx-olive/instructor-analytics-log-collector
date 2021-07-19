"""
Enterpoint.
"""

import argparse
import sys
import time

import django
django.setup()

from rg_instructor_analytics_log_collector.backends.file_backend import FileBackend
from rg_instructor_analytics_log_collector.backends.s3_backend import S3Backend

BACKENDS = {
    'file-system': FileBackend,
    's3': S3Backend,
}


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
        help="The path to the directory with the tracking log files (required if backend file-system is chosen)",
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
    parser.add_argument(
        '--backend',
        action="store",
        dest="backend_name",
        help=f"Choose backend storage to parse tracking logs from. LogCollector supports: {BACKENDS.keys()} "
             f"(file-system is default)",
        type=str,
        default='file-system'
    )
    parser.add_argument('--reload-logs', action="store_true", help='Reload all logs from files into database')
    parser.add_argument(
        '--delete-logs', action="store_true",
        help='Delete unused log records from database (after archived files processing only)'
    )
    parser.add_argument(
        '--bucket-name',
        action="store",
        dest="bucket_name",
        help="The name of the s3 bucket with the tracking logs (required if backend S3 is chosen)",
        type=str,
        default=''
    )
    parser.add_argument(
        '--aws-access-key-id',
        action="store",
        dest="aws_access_key_id",
        help="AWS access key ID - to get access to S3 bucket (required if backend S3 is chosen)",
        type=str,
        default=''
    )
    parser.add_argument(
        '--aws-secret-access-key',
        action="store",
        dest="aws_secret_access_key",
        help="AWS access secret key - to get access to S3 bucket (required if backend S3 is chosen)",
        type=str,
        default=''
    )

    args = parser.parse_args()

    backend_name = args.backend_name.lower()

    if backend_name not in BACKENDS:
        print(
            f'Provided backend {backend_name} cannot be used, choose one of the {BACKENDS.keys()} ...'
        )
        sys.exit(1)

    if backend_name == 's3' and (not args.aws_access_key_id or not args.aws_secret_access_key):
        print(
            f"For chosen backend {backend_name} params: --aws-access-key-id and --aws-secret-access-key can't be empty."
        )
        sys.exit(1)

    log_collector_backend = BACKENDS[backend_name](**vars(args))

    log_collector_backend.load_and_process()
    time.sleep(args.sleep_time)

    while True:
        log_collector_backend.load_and_process()
        time.sleep(args.sleep_time)


if __name__ == "__main__":
    main()
