from django.contrib import admin
from .models import Stock,Watchlist,Price
from django.contrib.auth.models import User


admin.site.register(Stock)
# admin.site.register(User)
admin.site.register(Watchlist)
admin.site.register(Price)