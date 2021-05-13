# -*- coding: utf-8 -*-


from django.db import migrations, models
import openedx.core.djangoapps.xmodule_django.models


class Migration(migrations.Migration):

    dependencies = [
        ('rg_instructor_analytics_log_collector', '0008_auto_20181102_1015'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscussionActivityByDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255, db_index=True)),
                ('day', models.DateField(db_index=True)),
                ('total', models.IntegerField(default=0)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='discussionactivitybyday',
            unique_together=set([('course', 'day')]),
        ),
    ]
