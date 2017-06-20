from __future__ import unicode_literals

from django.apps import AppConfig


class StockappConfig(AppConfig):
    name = 'stockapp'
    def ready(self):
        import stockapp.signals