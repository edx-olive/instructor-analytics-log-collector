# -*- coding: utf-8 -*-


from django.db import migrations, models
import openedx.core.djangoapps.xmodule_django.models


class Migration(migrations.Migration):

    dependencies = [
        ('rg_instructor_analytics_log_collector', '0007_auto_20181031_1042'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentStepCourse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_type', models.CharField(max_length=255)),
                ('user_id', models.IntegerField(db_index=True)),
                ('course', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255, db_index=True)),
                ('subsection_id', models.CharField(max_length=255)),
                ('current_unit', models.CharField(max_length=255)),
                ('target_unit', models.CharField(max_length=255)),
                ('log_time', models.DateTimeField()),
            ],
        ),
        migrations.AlterField(
            model_name='lastprocessedlog',
            name='processor',
            field=models.CharField(unique=True, max_length=2, choices=[(b'EN', b'Enrollment'), (b'VI', b'VideoViews'), ((b'DA',), b'Discussion activity'), (b'ST', b'Student step')]),
        ),
    ]
