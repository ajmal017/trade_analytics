"""
WSGI config for trademaster project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""
#!/usr/bin/python
import os,sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trademaster.settings")
sys.path.append('/root/sites/CompTechAnalysis/')
sys.path.append('/root/sites/CompTechAnalysis/trademaster')

application = get_wsgi_application()
