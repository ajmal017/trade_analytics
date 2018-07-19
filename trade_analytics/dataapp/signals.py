from django.db.models.signals import pre_delete
from django.dispatch import receiver
import stockapp.models as stkmd
import dataapp.models as dtamd


@receiver(pre_delete, sender=stkmd.Stockmeta,
          dispatch_uid='stockmeta_delete_signal')
def log_deleted_question(sender, instance, using, **kwargs):
    print "Signal recieived to delete stockprice data for ", instance.Symbol
    dtamd.Stockprice.objects.filter(Symbol_id=instance.id).delete()
