# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-07-15 21:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datascience', '0016_auto_20170908_2020'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DataCode',
        ),
        migrations.RemoveField(
            model_name='modelcode',
            name='Code',
        ),
        migrations.RemoveField(
            model_name='modelcode',
            name='File',
        ),
        migrations.RemoveField(
            model_name='modelcode',
            name='Username',
        ),
        migrations.RemoveField(
            model_name='modelcode',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='modelcode',
            name='updated_at',
        ),
    ]
