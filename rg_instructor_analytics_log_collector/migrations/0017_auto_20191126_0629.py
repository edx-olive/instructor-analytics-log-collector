# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import re
import django.core.validators
import openedx.core.djangoapps.xmodule_django.models


class Migration(migrations.Migration):

    dependencies = [
        ('rg_instructor_analytics_log_collector', '0016_auto_20190325_1007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursevisitsbyday',
            name='course',
            field=openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255),
        ),
        migrations.AlterField(
            model_name='coursevisitsbyday',
            name='users_ids',
            field=models.TextField(default=b'', validators=[django.core.validators.RegexValidator(re.compile('^[\\d,]+\\Z'), 'Enter only digits separated by commas.', 'invalid')]),
        ),
        migrations.AlterField(
            model_name='discussionactivity',
            name='commentable_id',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='discussionactivity',
            name='course',
            field=openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255),
        ),
        migrations.AlterField(
            model_name='discussionactivity',
            name='user_id',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='discussionactivitybyday',
            name='course',
            field=openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255),
        ),
        migrations.AlterField(
            model_name='discussionactivitybyday',
            name='day',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='enrollmentbyday',
            name='course',
            field=openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255),
        ),
        migrations.AlterField(
            model_name='enrollmentbyday',
            name='day',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='lastcoursevisitbyuser',
            name='user_id',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='studentstepcourse',
            name='course',
            field=openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255),
        ),
        migrations.AlterField(
            model_name='studentstepcourse',
            name='user_id',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='videoviewsbyday',
            name='course',
            field=openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255),
        ),
        migrations.AlterField(
            model_name='videoviewsbyday',
            name='day',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='videoviewsbyday',
            name='users_ids',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.RegexValidator(re.compile('^[\\d,]+\\Z'), 'Enter only digits separated by commas.', 'invalid')]),
        ),
        migrations.AlterField(
            model_name='videoviewsbyday',
            name='video_block_id',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='videoviewsbyuser',
            name='course',
            field=openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255),
        ),
        migrations.AlterField(
            model_name='videoviewsbyuser',
            name='user_id',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='videoviewsbyuser',
            name='video_block_id',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterUniqueTogether(
            name='videoviewsbyday',
            unique_together=set([('course', 'day', 'video_block_id')]),
        ),
        migrations.AlterIndexTogether(
            name='discussionactivity',
            index_together=set([('user_id', 'course')]),
        ),
        migrations.AlterIndexTogether(
            name='studentstepcourse',
            index_together=set([('course', 'log_time'), ('course', 'user_id')]),
        ),
    ]
