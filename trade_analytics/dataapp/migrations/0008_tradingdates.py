# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-09-09 00:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataapp', '0007_auto_20170720_1636'),
    ]

    operations = [
        migrations.CreateModel(
            name='TradingDates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Date', models.DateField(db_index=True)),
                ('SymbolUsed', models.CharField(blank=True, db_index=True, max_length=20, null=True)),
            ],
        ),
    ]
