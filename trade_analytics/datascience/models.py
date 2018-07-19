from __future__ import unicode_literals
import os
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
import utility.models as utymd
import h5py
import pandas as pd
import numpy as np
import joblib
import json

# Create your models here.

"""
Create Custom labels for the data
"""


class Label(models.Model):
    label = models.CharField(max_length=100)
    Symbol = models.CharField(max_length=100)
    T = models.DateField(null=True)
    window = models.IntegerField(null=True)
    User = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


"""
#########################################################################
####################  Machine learning Structure ########################
#########################################################################

|- ComputeFunc: Serializable Functions used for parallelization

|- Project
    |- Data: Datasets stored as shards
    |- MLmodels: Each Dataset has a model associated
    |- MLmetrics: Each model and each validation set has a metric


"""


class Project(models.Model):
    Name = models.CharField(max_length=200)
    Info = JSONField(default={})

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.Name

    def bigdatapath(self):
        return os.path.join(settings.BIGDATA_DIR, 'datascience',
                            'Projects', str(self.id) + '_' + self.Name)

    def initialize(self):
        # make the bigdata path, to store large data
        path = self.bigdatapath()
        if not os.path.isdir(path):
            os.makedirs(path)


class Data(models.Model):
    """
    In the description, please mention the way the data is to be read
    ProjectName--> Data --> Raw --> DataName --> files
    Datashards have infor such as shardname: sample_shape, #smaples, # samples in each class
    bigdata/datascience/Projects/$ProjectName/Data/$Datatype/$GroupName_$tag
    """
    Project = models.ForeignKey(Project, on_delete=models.CASCADE)

    ParentData = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    TransfomerFunc = models.TextField(null=True)

    GroupName = models.CharField(max_length=200)
    Info = JSONField(default={}, null=True)

    # tags that are same, are kind of pairs
    tag = models.CharField(max_length=200)

    model_types = [('Classification', 'Classification'),
                   ('Regression', 'Regression')]
    Modeltype = models.CharField(choices=model_types, max_length=20)

    data_structures = [('Channels', 'Channels'), ('Flattened', 'Flattened')]
    DataStructure = models.CharField(
        choices=data_structures,
        max_length=20,
        default='Channels')

    # Raw has all missing etc, Base is cleaned up
    data_choices = [('Raw', 'Raw'), ('Base', 'Base'), ('RawProcessed', 'RawProcessed'),
                    ('Train', 'Train'), ('Validation', 'Validation'), ('Test', 'Test')]
    Datatype = models.CharField(choices=data_choices, max_length=20)

    data_format = [('npz', 'npz'), ('h5', 'h5'), ('pkl', 'pkl'),
                   ('joblib', 'joblib'), ('json', 'json')]
    Dataformat = models.CharField(choices=data_format, max_length=30)

    # Binary is always 0/1, classes are labelled by integers 0,1,2,...
    # binary 1 is the important class i.e. like fraud==1 , nofraud==0
    ouput_choices = [('binary', 'binary'), ('multiclass',
                                            'multiclass'), ('continuous', 'continuous')]
    ouput_type = models.CharField(
        choices=data_format,
        max_length=30,
        default='binary')

    # Datashards=JSONField(default={})

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return " ".join(map(lambda x: str(x), [
                        self.Project, self.GroupName, self.tag, self.Modeltype, self.Datatype, self.Dataformat]))

    def datapath(self):
        return os.path.join(settings.BIGDATA_DIR, 'datascience', 'Projects', self.Project.Name,
                            "Data", self.Datatype, str(self.id) + '_' + self.GroupName + "_" + self.tag)

    def initialize(self):
        # make the data path
        path = self.datapath()
        if not os.path.isdir(path):
            os.makedirs(path)

    def getfulldatapath(self):
        return os.path.join(self.datapath(), 'fulldata' +
                            "." + self.Dataformat)

    def deletefulldata(self):
        filename = self.getfulldatapath()
        import os
        os.remove(filename)

    def getdata(self):

        filename = self.getfulldatapath()
        if not os.path.isfile(filename):
            import datascience.libs as dtsclibs
            dtsclibs.combineshards(self.id, filename, self.Dataformat)

        try:
            if self.Dataformat == 'npz':
                data = np.load(filename)

            return (data['X'], data['Y'], data['Meta'][()])
        except:

            import datascience.libs as dtsclibs
            dtsclibs.combineshards(self.id, filename, self.Dataformat)

            if self.Dataformat == 'npz':
                data = np.load(filename)

            return (data['X'], data['Y'], data['Meta'][()])


class MLmodels(models.Model):
    """
    In the description, please mention the way the data is to be read
    ProjectName--> Data --> Raw --> DataName --> files
    """

    Project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)
    Data = models.ForeignKey(Data, on_delete=models.SET_NULL, null=True)
    ModelCode = models.TextField(null=True)

    Metrics = JSONField(default={})

    Deploy = models.BooleanField(default=False)

    Name = models.CharField(max_length=200)
    Info = JSONField(default={})

    status_choices = [('Validated', 'Validated'), ('Trained', 'Trained'),
                      ('UnTrained', 'UnTrained'), ('Running', 'Running')]
    Status = models.CharField(choices=status_choices, max_length=30)

    save_format = [('npz', 'npz'), ('h5', 'h5'), ('pkl', 'pkl'),
                   ('joblib', 'joblib'), ('xgboost', 'xgboost'), ('keras', 'keras')]
    saveformat = models.CharField(choices=save_format, max_length=30)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def modeldir(self):
        return os.path.join(settings.BIGDATA_DIR, 'datascience',
                            'Projects', self.Project.Name, "Models")

    def modelpath(self):
        return os.path.join(settings.BIGDATA_DIR, 'datascience', 'Projects', self.Project.Name, "Models", str(
            self.id) + "_" + self.Name + "." + self.saveformat)

    def getmodelname(self):
        name = self.Name + '_' + self.id
        return name

    def initialize(self):
        # make the model path
        path = self.modeldir()
        if not os.path.isdir(path):
            os.makedirs(path)

    def getmodelclass(self):
        MC = ModelCode.objects.get(id=self.ModelCode.id)
        return MC.importobject(self.Name)
