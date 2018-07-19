from __future__ import unicode_literals

from django.apps import AppConfig


class DataappConfig(AppConfig):
    name = 'dataapp'

    def ready(self):
        import dataapp.signals
