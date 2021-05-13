# -*- coding: utf-8 -*-


from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('rg_instructor_analytics_log_collector', '0004_lastprocessedlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='logtable',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 10, 31, 12, 8, 10, 255604, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
