# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-03-25 14:07


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rg_instructor_analytics_log_collector', '0015_auto_20190325_1004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logtable',
            name='message_type',
            field=models.TextField(),
        ),
    ]
