from django.db.models.signals import pre_delete
from django.dispatch import receiver
import datascience.models as dtscmd
import shutil

import os
