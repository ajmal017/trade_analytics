from __future__ import absolute_import
from celery import shared_task


@shared_task
def process_stock_update():
	from . import models as md
	L=md.Stock.objects.all().count()
	for stk in md.Stock.objects.all().order_by('LastPriceUpdate'):
		L=L-1
		print [stk.Symbol,L]
		stk.UpdateData()

