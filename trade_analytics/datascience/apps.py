from __future__ import unicode_literals

from django.apps import AppConfig


class datascienceConfig(AppConfig):
    name = 'datascience'
    def ready(self):
        import datascience.signals