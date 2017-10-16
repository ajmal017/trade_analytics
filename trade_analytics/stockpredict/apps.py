# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class StockpredictConfig(AppConfig):
    name = 'stockpredict'
    def ready(self):
        import stockpredict.signals



