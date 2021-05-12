# -*- coding: utf-8 -*-


from django.db import migrations, models
import re
import django.core.validators
import openedx.core.djangoapps.xmodule_django.models


class Migration(migrations.Migration):

    dependencies = [
        ('rg_instructor_analytics_log_collector', '0007_auto_20181031_1042'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoViewsByDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255, db_index=True)),
                ('video_block_id', models.CharField(max_length=255, db_index=True)),
                ('day', models.DateField(db_index=True)),
                ('total', models.IntegerField(default=0)),
                ('users_ids', models.TextField(blank=True, null=True, validators=[django.core.validators.RegexValidator(re.compile('^[\\d,]+\\Z'), 'Enter only digits separated by commas.', 'invalid')])),
            ],
        ),
        migrations.AlterField(
            model_name='discussionactivity',
            name='commentable_id',
            field=models.CharField(max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='discussionactivity',
            name='user_id',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='videoviewsbyblock',
            name='course',
            field=openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='videoviewsbyblock',
            name='video_block_id',
            field=models.CharField(max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='videoviewsbyuser',
            name='course',
            field=openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='videoviewsbyuser',
            name='user_id',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='videoviewsbyuser',
            name='video_block_id',
            field=models.CharField(max_length=255, db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='videoviewsbyday',
            unique_together=set([('course', 'video_block_id', 'day')]),
        ),
    ]
