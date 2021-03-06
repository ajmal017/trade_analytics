# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-11 19:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Stockmeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Company', models.CharField(blank=True, max_length=100, null=True)),
                ('Marketcap', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ('Competitors', models.CharField(blank=True, max_length=1100, null=True)),
                ('Symbol', models.CharField(blank=True, max_length=6, null=True)),
                ('Sector', models.CharField(blank=True, max_length=100, null=True)),
                ('Industry', models.CharField(blank=True, max_length=100, null=True)),
                ('Status', models.CharField(blank=True, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], max_length=25, null=True)),
                ('LastPriceUpdate', models.DateField(null=True)),
                ('Labels', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('ETF', 'ETF'), ('Stock', 'Stock'), ('Gold', 'Gold'), ('Silver', 'Silver'), ('Oil', 'Oil'), ('Inverse', 'Inverse'), ('Copper', 'Copper'), ('Entertainment', 'Entertainment'), ('Uranium', 'Uranium'), ('Coal', 'Coal'), ('Index', 'Index')], max_length=73)),
            ],
        ),
        migrations.CreateModel(
            name='Watchlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Watchlist_name', models.CharField(max_length=50, null=True)),
                ('Watchlist_description', models.CharField(blank=True, max_length=1000, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('Symbol', models.ManyToManyField(to='stockapp.Stockmeta')),
                ('User', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
