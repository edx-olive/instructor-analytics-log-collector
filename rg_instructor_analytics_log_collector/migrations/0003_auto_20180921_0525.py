# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rg_instructor_analytics_log_collector', '0002_enrollmentbyday_enrollmentbyuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollmentbyday',
            name='last_updated',
            field=models.DateField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='enrollmentbyday',
            name='day',
            field=models.DateField(db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='enrollmentbyday',
            unique_together=set([('course', 'day')]),
        ),
    ]
