"""
Production settings variables are required by the rg_instructor_analytics_log_collector.
"""


def plugin_settings(settings):
    """
    Settings for rg_instructor_analytics_log_collector
    """
    settings.EVENT_TRACKING_BACKENDS['tracking_logs']['OPTIONS']['backends'].update(
        {
            'rg_analytics': {
                'ENGINE': 'rg_instructor_analytics_log_collector.backends.tracking_backend.RGAnalyticsBackend'
            }
        }
    )
