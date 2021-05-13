# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LogTable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message_type', models.CharField(max_length=128, db_index=True)),
                ('log_time', models.DateTimeField()),
                ('log_message', models.TextField()),
                ('user_name', models.CharField(max_length=128, null=True, blank=True)),
            ],
            options={
                'ordering': ['-log_time'],
            },
        ),
        migrations.CreateModel(
            name='ProcessedZipLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file_name', models.TextField(max_length=256)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='logtable',
            unique_together=set([('message_type', 'log_time', 'user_name')]),
        ),
    ]
