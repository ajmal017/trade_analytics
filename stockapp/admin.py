from django.contrib import admin

# Register your models here.

from . import models as mds

admin.site.register(mds.Stockmeta)
admin.site.register(mds.Watchlist)

