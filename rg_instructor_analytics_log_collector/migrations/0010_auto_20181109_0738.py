# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rg_instructor_analytics_log_collector', '0009_auto_20181106_0531'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EnrollmentByUser',
        ),
        migrations.AlterField(
            model_name='enrollmentbyday',
            name='enrolled',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='enrollmentbyday',
            name='total',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='enrollmentbyday',
            name='unenrolled',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='logtable',
            name='log_time',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='logtable',
            name='message_type',
            field=models.CharField(max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='logtable',
            name='user_name',
            field=models.CharField(db_index=True, max_length=255, null=True, blank=True),
        ),
    ]
