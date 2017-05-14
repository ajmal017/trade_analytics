# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-14 05:42
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StdCharts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Chartname', models.CharField(blank=True, max_length=50, null=True)),
                ('Chartdescription', models.CharField(blank=True, max_length=200, null=True)),
                ('Template', models.CharField(blank=True, max_length=50, null=True)),
                ('TempBlocs', django.contrib.postgres.fields.jsonb.JSONField()),
                ('inputtype', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
    ]
