# -*- coding: utf-8 -*-


from django.db import migrations, models
import openedx.core.djangoapps.xmodule_django.models


class Migration(migrations.Migration):

    dependencies = [
        ('rg_instructor_analytics_log_collector', '0006_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoViewsByBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255)),
                ('video_block_id', models.CharField(max_length=255)),
                ('count_full_viewed', models.IntegerField(default=0)),
                ('count_part_viewed', models.IntegerField(default=0)),
                ('video_duration', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='VideoViewsByUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255)),
                ('user_id', models.IntegerField()),
                ('video_block_id', models.CharField(max_length=255)),
                ('is_completed', models.BooleanField(default=False)),
                ('viewed_time', models.IntegerField(default=0)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='videoviewsbyuser',
            unique_together=set([('course', 'user_id', 'video_block_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='videoviewsbyblock',
            unique_together=set([('course', 'video_block_id')]),
        ),
    ]
