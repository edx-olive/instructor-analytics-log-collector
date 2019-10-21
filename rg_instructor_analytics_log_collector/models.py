"""
Models of the RG analytics.
"""
from django.core.validators import validate_comma_separated_integer_list
from django.db import connection, models
from django.urls import reverse
from opaque_keys.edx.keys import CourseKey

from openedx.core.djangoapps.xmodule_django.models import CourseKeyField
from openedx.features.course_experience import course_home_url_name


class GeneralAnalyticsManager(models.Manager):
    """
    EnrollmentByDay model Manager.

    Manage requests to the EnrollmentByDay model for fetching data which is needed to the General Metrics tab.
    """

    @staticmethod
    def _get_course_org_filter(courses_filter):
        """
        Helper method, that generates SQL filter condition.

        :param courses_filter: Filter courses for selected microsite
                                by org or display_name_with_default
        :return: (string) with SQL code or an empty string if the courses_filter is None.
        """

        if courses_filter:
            courses_filter = (
                "WHERE course_overview.org IN {courses_filter} "
                "OR course_overview.display_org_with_default IN {courses_filter}"
            ).format(courses_filter=tuple(courses_filter))
        else:
            courses_filter = ''

        # To achieve correct SQL we should do this ('Canada',) -> ('Canada')
        return courses_filter.replace(',)', ')')

    def extract_analytics_data(self, limit, offset, sort_key, ordering, courses_filter=None):
        """
        Method that generates SQL query and executes it on the database.

        :param courses_filter: (tuple) Filter courses for selected microsite
                                        by org or display_name_with_default
        :param limit: (int) Query limit
        :param offset: (int) Query offset
        :param sort_key: (str) field by which query will be sorted
        :param ordering: (str) sort order
        :return: list with data for General Metrics tab

        example output: [
            {
                'certificates': 0,
                'enrolled_max': 17,
                'name': 'course-v1:edX+DemoX+Demo_Course',
                'end_date': '-',
                'week_change': 0,
                'total': 20,
                'start_date': '02/05/2013',
                'count_graded': 0,
                'course_url': u'/courses/course-v1:edX+DemoX+Demo_Course/course/'
            },
            ...
        ]
        """

        courses_filter = self._get_course_org_filter(courses_filter)

        result_list = []

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                enrollment_by_day.id,
                enrollment_by_day.course                                            AS course,
                MAX(enrollment_by_day.enrolled)                                     AS diff_enr_max,
                MAX(enrollment_by_day.enrolled) - MIN(enrollment_by_day.enrolled)   AS diff,
                MAX(enrollment_by_day.total)                                        AS total,
                MAX(enrollment_by_day.enrolled)                                     AS enrolled_max,
                course_overview.start                                               AS start,
                course_overview.end                                                 AS end,
                course_overview.lowest_passing_grade                                AS lowest_passing_grade,
                generated_certificates.certificates_count                           AS cert_count,
                SUM(
                    CASE WHEN 
                        grade_statistic.total > course_overview.lowest_passing_grade 
                    THEN 1 
                    ELSE 0 END
                    ) AS total_passing
                FROM rg_instructor_analytics_log_collector_enrollmentbyday AS enrollment_by_day
                    LEFT JOIN course_overviews_courseoverview AS course_overview
                        ON enrollment_by_day.course = course_overview.id
                    LEFT JOIN (
                        SELECT generated_certificates.course_id,
                            COUNT(generated_certificates.id) AS certificates_count
                        FROM certificates_generatedcertificate AS generated_certificates
                        GROUP BY generated_certificates.id
                        ) generated_certificates
                        ON enrollment_by_day.course =  generated_certificates.course_id
                    LEFT JOIN rg_instructor_analytics_gradestatistic AS grade_statistic
                        ON enrollment_by_day.course = grade_statistic.course_id
                {filter}
                GROUP BY enrollment_by_day.course
                ORDER BY {sort_key} {ordering}
                LIMIT {limit} OFFSET {offset};
            """.format(limit=limit, offset=offset, sort_key=sort_key, ordering=ordering, filter=courses_filter))

            for row in cursor.fetchall():
                result_list.append(
                    {
                        "name": str(row[1]),
                        "course_url": reverse(course_home_url_name(CourseKey.from_string(row[1])), args=[row[1]]),
                        "total": int(row[4]),
                        "enrolled_max": int(row[5]),
                        "week_change": row[3],
                        "start_date": row[6].strftime("%m/%d/%Y") if row[6] is not None else '-',
                        "end_date": row[7].strftime("%m/%d/%Y") if row[7] is not None else '-',
                        "certificates": int(row[9]) if row[9] is not None else 0,
                        "count_graded": int(row[10]),
                    }
                )

        return result_list

    def get_courses_count_by_site(self, courses_filter):
        """
        Method that returns count courses for selected site or count of all courses.

        :return: (int) Count courses.
        """

        courses_filter = self._get_course_org_filter(courses_filter)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT enrollment_by_day.id
                    FROM rg_instructor_analytics_log_collector_enrollmentbyday AS enrollment_by_day
                        LEFT JOIN course_overviews_courseoverview AS course_overview
                            ON enrollment_by_day.course = course_overview.id
                    {filter}
                    GROUP BY enrollment_by_day.course
                """.format(filter=courses_filter)
            )

            return len(cursor.fetchall())


class ProcessedZipLog(models.Model):
    """
    Already processed tracking log files.
    """

    file_name = models.TextField(max_length=256)


class LogTable(models.Model):
    """
    Log Records parsed from tracking gzipped log file.
    """

    message_type_hash = models.CharField(max_length=255, db_index=True)
    message_type = models.TextField()
    log_time = models.DateTimeField(db_index=True)
    user_name = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    log_message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:  # NOQA
        unique_together = ('message_type_hash', 'log_time', 'user_name')
        ordering = ['-log_time']

    def __unicode__(self):  # NOQA
        return u'{} {}'.format(self.message_type, self.log_time)


class EnrollmentByDay(models.Model):
    """
    Cumulative per-day Enrollment stats.
    """

    day = models.DateField()
    total = models.IntegerField(default=0)
    enrolled = models.IntegerField(default=0)
    unenrolled = models.IntegerField(default=0)
    course = CourseKeyField(max_length=255)
    last_updated = models.DateField(auto_now=True, null=True)

    objects = GeneralAnalyticsManager()

    class Meta:  # NOQA
        # NOTE(okopylova): empirically discovered that multi-column indexes are
        # created for fields from unique_together. There is no documentation
        # for the feature, so it might be related to database configuration and
        # not working for all installation. Option index_together is not used
        # here, because it creates index even in case if the same index
        # already exists (and failed on rollback in such case).
        # For quick index creations in case of missed indexes, use management
        # command update_db_indexes.
        unique_together = ('course', 'day',)
        ordering = ['-day']

    def __unicode__(self):  # NOQA
        return u'{} {}'.format(self.day, self.course)


class LastProcessedLog(models.Model):
    """
    Last processed LogTable by Processor.
    """

    ENROLLMENT = 'EN'
    VIDEO_VIEWS = 'VI'
    DISCUSSION_ACTIVITY = 'DA'
    STUDENT_STEP = 'ST'
    COURSE_ACTIVITY = 'CA'

    PROCESSOR_CHOICES = (
        (ENROLLMENT, 'Enrollment'),
        (VIDEO_VIEWS, 'VideoViews'),
        (DISCUSSION_ACTIVITY, 'Discussion activity'),
        (STUDENT_STEP, 'Student step'),
        (COURSE_ACTIVITY, 'Course activity'),
    )

    log_table = models.ForeignKey(LogTable)
    processor = models.CharField(max_length=2, choices=PROCESSOR_CHOICES, unique=True)

    @classmethod
    def get_last_date(cls):
        """Return the last log date."""
        return cls.objects.all().aggregate(models.Min('log_table__log_time')).get('log_table__log_time__min')


class VideoViewsByUser(models.Model):
    """
    User's Video Views info.
    """

    course = CourseKeyField(max_length=255)
    user_id = models.IntegerField()
    video_block_id = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    viewed_time = models.IntegerField(default=0)

    class Meta:  # NOQA
        unique_together = ('course', 'user_id', 'video_block_id')

    def __unicode__(self):  # NOQA
        return u'{} {} {}'.format(self.user_id, self.course, self.video_block_id)


class VideoViewsByBlock(models.Model):
    """
    Block's Video Views info.
    """

    course = CourseKeyField(max_length=255, db_index=True)
    video_block_id = models.CharField(max_length=255, db_index=True)
    count_full_viewed = models.IntegerField(default=0)
    count_part_viewed = models.IntegerField(default=0)
    video_duration = models.IntegerField(default=0)

    class Meta:  # NOQA
        unique_together = ('course', 'video_block_id')

    def __unicode__(self):  # NOQA
        return u'{} {}'.format(self.course, self.video_block_id)


class VideoViewsByDay(models.Model):
    """
    Day's Video Views info.
    """

    course = CourseKeyField(max_length=255)
    video_block_id = models.CharField(max_length=255)
    day = models.DateField()
    total = models.IntegerField(default=0)
    users_ids = models.TextField(blank=True, null=True, validators=[validate_comma_separated_integer_list])

    class Meta:  # NOQA
        unique_together = ('course', 'day', 'video_block_id')
        ordering = ['-day']

    def __unicode__(self):  # NOQA
        return u'{}, {}, day - {}'.format(self.course, self.video_block_id, self.day)


class DiscussionActivity(models.Model):
    """
    Track specific user activities.
    """

    event_type = models.CharField(max_length=255)
    user_id = models.IntegerField()
    course = CourseKeyField(max_length=255)
    category_id = models.CharField(max_length=255, blank=True, null=True)
    commentable_id = models.CharField(max_length=255)
    discussion_id = models.CharField(max_length=255)
    thread_type = models.CharField(max_length=255, blank=True, null=True)
    log_time = models.DateTimeField()

    class Meta:  # NOQA
        index_together = ('user_id', 'course')

    def __unicode__(self):  # NOQA
        return u'{},  {},  user_id - {}'.format(self.event_type, self.course, self.user_id)


class DiscussionActivityByDay(models.Model):
    """
    Day's Discussion Activities info.
    """

    course = CourseKeyField(max_length=255)
    day = models.DateField()
    total = models.IntegerField(default=0)

    class Meta:  # NOQA
        unique_together = ('course', 'day')
        ordering = ['-day']

    def __unicode__(self):  # NOQA
        return u'{},  day - {}'.format(self.course, self.day)


class StudentStepCourse(models.Model):
    """
    Track student's path through the course.
    """

    event_type = models.CharField(max_length=255)
    user_id = models.IntegerField()
    course = CourseKeyField(max_length=255)
    subsection_id = models.CharField(max_length=255)
    current_unit = models.CharField(max_length=255)
    target_unit = models.CharField(max_length=255)
    log_time = models.DateTimeField()

    class Meta:  # NOQA
        index_together = (
            ('course', 'log_time'),
            ('course', 'user_id')
        )

    def __unicode__(self):  # NOQA
        return u'{},  {},  user_id - {}'.format(self.event_type, self.course, self.user_id)


class LastCourseVisitByUser(models.Model):
    """
    Track the date of the last visit the course by user.
    """

    user_id = models.IntegerField()
    course = CourseKeyField(max_length=255, db_index=True)
    log_time = models.DateTimeField()

    class Meta:  # NOQA
        unique_together = ('user_id', 'course')

    def __unicode__(self):  # NOQA
        return u'{}, user_id - {}'.format(self.course, self.user_id)


class CourseVisitsByDay(models.Model):
    """
    Track the intensity of visits the course by the day.
    """

    course = CourseKeyField(max_length=255)
    users_ids = models.TextField(default='', validators=[validate_comma_separated_integer_list])
    day = models.DateField(db_index=True)
    total = models.IntegerField(default=0)

    class Meta:  # NOQA
        unique_together = ('course', 'day')
        ordering = ['-day']

    def __unicode__(self):  # NOQA
        return u'{},  day - {}'.format(self.course, self.day)
