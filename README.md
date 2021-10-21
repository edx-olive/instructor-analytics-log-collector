https://travis-ci.org/raccoongang/rg_instructor_analytics_log_collector.svg?branch=master

# Util for the tracking log parsing and storing it into mySql databse 

> Relies on [Edx Event Tracking](https://github.com/edx/event-tracking) system's `logger` backend
> - https://event-tracking.readthedocs.io/en/latest/

## Glossary

Event (Edx Event)
> context-aware semi-structured data items with nested data structures;

Tracker
>

Processor
>

Pipeline
>

Record
>

## Setup

* Add RG IA log collector to the edxapp venv
* Set next environment variables: DJANGO_SETTINGS_MODULE and SERVICE_VARIANT
  (if needed)
```
# Example:
DJANGO_SETTINGS_MODULE = lms.envs.devstack
SERVICE_VARIANT = lms
```
* Run migrations
* Ensure app has an access to the log directory
* Run in the console:
```bash
sudo -sHu edxapp
cd ~
. edxapp_env
pip install git+https://github.com/raccoongang/instructor-analytics-log-collector@v3.x.x#egg=instructor-analytics-log-collector
cd edx-platform
paver update_db
exit
sudo /edx/bin/supervisorctl restart edxapp:lms
```

## Live Events Support

`rg_instaructor_analytics_log_collector` works with the live event directly by adding `RGAnalyticsBackend` to the
`EVENT_TRACKING_BACKENDS['tracking_logs']`.  Backend handle events one by one and add required data to the 
Log Collector tables. `tracking.log` files still could be used for "cold" RG analytics start or in case one need
to reload data from the sored log files.

## Log Watcher running

Could be used to gather statistics data from the tracking log files on the "cold" start for the data that was
collected before RG IA is started.

**IMPORTANT (DevOps)** *Log Watcher* should not be added to the supervisor services or as a chron job to the 
instance anymore.

```
# bash
python run_log_watcher.py [--tracking_log_dir] [--sleep_time] [--backend] [--reload-logs] [--delete-logs] [--c] [--aws-secret-access-key] [--blob-conn-str] [--container-name]
```
- `tracking_log_dir` - (str) points to the log directory (default: `/edx/var/log/tracking`)
- `sleep_time` - (int) log directory rescan period (seconds, default: 5 minutes).
- `backend` - (str) backend to work with. Available parameters: `file-system`, `s3`, and `blob` (default: `file-system`)
- `reload-logs` - (bool) Reload all logs from files into database
- `delete-logs` - (bool) Delete unused log records from database (after archived files processing only)
- `aws-access-key-id` - (str) AWS access key ID - to get access to S3 bucket (required if backend S3 is chosen)
- `aws-secret-access-key` - (str) AWS access secret key - to get access to S3 bucket (required if backend S3 is chosen)
- `blob-conn-str` - (str) Azure Blob connection string - to get access to Azure Blob (required if backend blob is chosen)
- `container-name` - (str) The name of the Blob container with the tracking logs (required if backend blob is chosen)

## New processor
If you add new processor to *rg_instructor_analytics_log_collector* and **run_log_watcher.py** worker has run with **--delete-logs** parameter, you need stop **run_log_watcher.py**,
and run manually:
```
python run_log_watcher.py --reload-logs
```

## Tests

##### To run tests manually, follow the next steps:
* Ensure to place the source code in the edx-platform root:
```
├── cms
├── common
├── lms
├── openedx
├── ...
├── rg_instructor_analytics_log_collector
```

* Being located in the edx-platform dir, execute the next commands: 
```
# bash

python -m pytest rg_instructor_analytics_log_collector/rg_instructor_analytics_log_collector/tests/processors
```
