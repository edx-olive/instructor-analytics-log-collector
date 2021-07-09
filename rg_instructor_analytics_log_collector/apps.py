from django.apps import AppConfig
from edx_django_utils.plugins.constants import PluginSettings


class RgIALogCollectorAppConfig(AppConfig):
    name = 'rg_instructor_analytics_log_collector'
    verbose_name = 'RG Instructor Analytics Log Collector'

    plugin_app = {}  # Empty attribute is needed to add app into INSTALLED_APPS
