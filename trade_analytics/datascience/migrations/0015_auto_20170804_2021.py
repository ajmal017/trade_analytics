# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-08-05 00:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datascience', '0014_mlmodels_modelcode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mlmodels',
            name='ModelCode',
        ),
        migrations.AddField(
            model_name='mlmodels',
            name='Userfilename',
            field=models.CharField(blank=True, help_text='User ID from database', max_length=150),
        ),
    ]