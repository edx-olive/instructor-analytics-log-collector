# -*- coding: utf-8 -*-


from django.db import migrations, models
import openedx.core.djangoapps.xmodule_django.models


class Migration(migrations.Migration):

    dependencies = [
        ('rg_instructor_analytics_log_collector', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnrollmentByDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.DateTimeField(db_index=True)),
                ('total', models.IntegerField()),
                ('enrolled', models.IntegerField()),
                ('unenrolled', models.IntegerField()),
                ('course', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255, db_index=True)),
            ],
            options={
                'ordering': ['-day'],
            },
        ),
        migrations.CreateModel(
            name='EnrollmentByUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255, db_index=True)),
                ('student', models.IntegerField(db_index=True)),
                ('is_enrolled', models.BooleanField()),
            ],
        ),
    ]
