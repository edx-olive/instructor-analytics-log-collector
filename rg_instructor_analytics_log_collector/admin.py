"""
Admin site bindings for rg_instructor_analytics app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from rg_instructor_analytics_log_collector import models
from rg_instructor_analytics_log_collector.constants import Events


class EventTypeListFilter(admin.SimpleListFilter):
    """
    Django admin customizations for right admin sidebar.
    """

    title = _('Event Type')
    parameter_name = 'event_type'

    def lookups(self, request, model_admin):
        """
        Return a list of tuples.

        The first element in each tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            (Events.USER_ENROLLED, 'USER_ENROLLED'),
            (Events.USER_UNENROLLED, 'USER_UNENROLLED'),
            (Events.FORUM_COMMENT_CREATED, 'FORUM_COMMENT_CREATED'),
            (Events.FORUM_RESPONSE_CREATED, 'FORUM_RESPONSE_CREATED'),
            (Events.FORUM_RESPONSE_VOTED, 'FORUM_RESPONSE_VOTED'),
            (Events.FORUM_SEARCHED, 'FORUM_SEARCHED'),
            (Events.FORUM_THREAD_CREATED, 'FORUM_THREAD_CREATED'),
            (Events.FORUM_THREAD_VOTED, 'FORUM_THREAD_VOTED'),
            (Events.USER_STARTED_VIEW_VIDEO, 'USER_STARTED_VIEW_VIDEO'),
            (Events.USER_PAUSED_VIEW_VIDEO, 'USER_PAUSED_VIEW_VIDEO'),
            (Events.USER_FINISHED_WATCH_VIDEO, 'USER_FINISHED_WATCH_VIDEO'),
            (Events.SEQ_GOTO, 'SEQ_GOTO'),
            (Events.SEQ_NEXT, 'SEQ_NEXT'),
            (Events.SEQ_PREV, 'SEQ_PREV'),
            (Events.UI_SEQ_NEXT, 'UI_SEQ_NEXT'),
            (Events.UI_SEQ_PREV, 'UI_SEQ_PREV'),
        )

    def queryset(self, request, queryset):
        """
        Return the filtered queryset.

        Based on the value provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(message_type=self.value())


class LastProcessedLogAdmin(admin.ModelAdmin):
    """
    Django admin customizations for LastProcessedLog model.
    """

    list_display = ('processor', 'log_time',)
    raw_id_fields = ('log_table',)

    def log_time(self, obj):
        """
        Format for LastProcessedLog field.
        """
        return obj.log_table.log_time


class LogTableAdmin(admin.ModelAdmin):
    """
    Django admin customizations for LogTable model.
    """

    list_display = ('message_type', 'log_time', 'user_name')
    date_hierarchy = 'log_time'
    list_filter = (EventTypeListFilter,)
    search_fields = ['log_message']


class StudentStepCourseAdmin(admin.ModelAdmin):
    list_display = (
        'course', 'user_id', 'current_unit', 'target_unit', 'log_time'
    )


admin.site.register(models.ProcessedZipLog, admin.ModelAdmin)
admin.site.register(models.LogTable, LogTableAdmin)
admin.site.register(models.EnrollmentByDay, admin.ModelAdmin)
admin.site.register(models.LastProcessedLog, LastProcessedLogAdmin)
admin.site.register(models.VideoViewsByUser, admin.ModelAdmin)
admin.site.register(models.VideoViewsByBlock, admin.ModelAdmin)
admin.site.register(models.VideoViewsByDay, admin.ModelAdmin)
admin.site.register(models.DiscussionActivity, admin.ModelAdmin)
admin.site.register(models.DiscussionActivityByDay, admin.ModelAdmin)
admin.site.register(models.StudentStepCourse, StudentStepCourseAdmin)
admin.site.register(models.LastCourseVisitByUser, admin.ModelAdmin)
admin.site.register(models.CourseVisitsByDay, admin.ModelAdmin)
