from django.db.models.signals import pre_delete
from django.dispatch import receiver
import datascience.models as dtscmd
import shutil

import os

@receiver(pre_delete, sender=dtscmd.Project, dispatch_uid='project_delete_signal')
def delete_project_files(sender, instance, using, **kwargs):
    # print "Signal recieived to delete all project data for Project: ",instance.Name
    dtscmd.DataShard.objects.filter(Data__Project__id=instance.id).delete()
    dtscmd.Data.objects.filter(Project__id=instance.id).delete()
    # dtscmd.MLmodels.objects.filter(Project__id=instance.id).delete()
    dtscmd.ModelMetrics.objects.filter(Data__Project__id=instance.id).delete()

    path=instance.bigdatapath()
    try:
	    shutil.rmtree(path)
    except Exception as e:
    	print e

@receiver(pre_delete, sender=dtscmd.Data, dispatch_uid='data_delete_signal')
def delete_data_files(sender, instance, using, **kwargs):
    # print "Signal recieived to delete all data for : ", str(instance)
    dtscmd.DataShard.objects.filter(Data__id=instance.id).delete()
    # dtscmd.MLmodels.objects.filter(Project__id=instance.id).delete()
    dtscmd.ModelMetrics.objects.filter(Data__id=instance.id).delete()

    path=instance.datapath()
    
    try:
	    shutil.rmtree(path)
    except Exception as e:
    	print e

@receiver(pre_delete, sender=dtscmd.DataShard, dispatch_uid='datashard_delete_signal')
def delete_datashard_files(sender, instance, using, **kwargs):
    # print "Signal recieived to delete datashard for : ", str(instance.id)

    name,path=instance.shardpath()
    try:
	    os.remove(path)
    except Exception as e:
    	print e

@receiver(pre_delete, sender=dtscmd.MLmodels, dispatch_uid='MLmodels_delete_signal')
def delete_MLmodels_files(sender, instance, using, **kwargs):
    # print "Signal recieived to delete all MLmodels for : ", str(instance.NAME)
    # dtscmd.DataShard.objects.filter(Data__id=instance.id).delete()
    # dtscmd.MLmodels.objects.filter(Project__id=instance.id).delete()
    dtscmd.ModelMetrics.objects.filter(MLmodel__id=instance.id).delete()

    path=instance.modelpath()
    
    try:
	    shutil.rmtree(path)
    except Exception as e:
    	print e

