# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rg_instructor_analytics_log_collector', '0008_auto_20181106_0925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lastprocessedlog',
            name='processor',
            field=models.CharField(unique=True, max_length=2, choices=[(b'EN', b'Enrollment'), (b'VI', b'VideoViews'), (b'DA', b'Discussion activity'), (b'ST', b'Student step')]),
        ),
        migrations.AlterField(
            model_name='logtable',
            name='message_type',
            field=models.CharField(max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='logtable',
            name='user_name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
