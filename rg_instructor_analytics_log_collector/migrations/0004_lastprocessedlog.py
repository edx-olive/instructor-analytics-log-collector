# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rg_instructor_analytics_log_collector', '0003_auto_20180921_0525'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastProcessedLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('processor', models.CharField(unique=True, max_length=2, choices=[(b'EN', b'Enrollment'), (b'VI', b'VideoViews')])),
                ('log_table', models.ForeignKey(to='rg_instructor_analytics_log_collector.LogTable',
                                                on_delete=models.deletion.CASCADE)),
            ],
        ),
    ]
