from django.apps import AppConfig
from edx_django_utils.plugins.constants import PluginSettings


class RgIALogCollectorAppConfig(AppConfig):
    name = 'rg_instructor_analytics_log_collector'
    verbose_name = 'RG Instructor Analytics Log Collector'

    plugin_app = {
        PluginSettings.CONFIG: {
            'lms.djangoapp': {
                'production': {},  # NOTE: 'relative_path' is omitted, the default_relative_path is 'settings'
            }
        },
    }
