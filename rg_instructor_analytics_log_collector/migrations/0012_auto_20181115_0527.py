# -*- coding: utf-8 -*-


from django.db import migrations, models
import re
import openedx.core.djangoapps.xmodule_django.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('rg_instructor_analytics_log_collector', '0011_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseVisitsByDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255, db_index=True)),
                ('users_ids', models.TextField(default=b'', validators=[django.core.validators.RegexValidator(re.compile('^[\\d,]+\\Z'), 'Enter only digits separated by commas.', 'invalid')])),
                ('day', models.DateField(db_index=True)),
                ('total', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['-day'],
            },
        ),
        migrations.CreateModel(
            name='LastCourseVisitByUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField(db_index=True)),
                ('course', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255, db_index=True)),
                ('log_time', models.DateTimeField()),
            ],
        ),
        migrations.AlterModelOptions(
            name='discussionactivitybyday',
            options={'ordering': ['-day']},
        ),
        migrations.AlterModelOptions(
            name='videoviewsbyday',
            options={'ordering': ['-day']},
        ),
        migrations.AlterField(
            model_name='lastprocessedlog',
            name='processor',
            field=models.CharField(unique=True, max_length=2, choices=[(b'EN', b'Enrollment'), (b'VI', b'VideoViews'), (b'DA', b'Discussion activity'), (b'ST', b'Student step'), (b'CA', b'Course activity')]),
        ),
        migrations.AlterField(
            model_name='logtable',
            name='user_name',
            field=models.CharField(db_index=True, max_length=255, null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='lastcoursevisitbyuser',
            unique_together=set([('user_id', 'course')]),
        ),
        migrations.AlterUniqueTogether(
            name='coursevisitsbyday',
            unique_together=set([('course', 'day')]),
        ),
    ]
