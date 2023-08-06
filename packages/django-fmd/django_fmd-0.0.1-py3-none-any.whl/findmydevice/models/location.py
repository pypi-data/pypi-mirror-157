import logging
import uuid

from bx_django_utils.models.timetracking import TimetrackingBaseModel
from django.db import models

from findmydevice.models import DeviceUser


logger = logging.getLogger(__name__)


class Location(TimetrackingBaseModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    device_user = models.ForeignKey(DeviceUser, on_delete=models.CASCADE)
    bat = models.CharField(max_length=256, unique=True)
    raw_date = models.PositiveIntegerField()
    lat = models.CharField(max_length=256, unique=True)
    lon = models.CharField(max_length=256, unique=True)
    provider = models.CharField(max_length=256, unique=True)

    class Meta:
        get_latest_by = ['create_dt']
