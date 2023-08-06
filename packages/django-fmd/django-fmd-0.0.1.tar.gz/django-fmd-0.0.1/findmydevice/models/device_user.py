import logging
import uuid

from bx_django_utils.models.timetracking import TimetrackingBaseModel
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.http import Http404
from django.utils.crypto import get_random_string


logger = logging.getLogger(__name__)


class DeviceUser(TimetrackingBaseModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    hashed_password = models.CharField(max_length=64)
    privkey = models.CharField(max_length=2048, unique=True)
    pubkey = models.CharField(max_length=512, unique=True)
    # command2user=
    # push_url=
    # location_data=
    # pictures=


def _make_cache_key(token):
    cache_key = f'access_token_{token}'
    logger.debug('Cache key: %r', cache_key)
    return cache_key


def new_access_token(device_user: DeviceUser):
    token = get_random_string(length=12)
    timeout = settings.FMD_ACCESS_TOKEN_TIMEOUT_SEC
    cache.set(key=_make_cache_key(token), value=device_user.uuid, timeout=timeout)
    logger.info('Store access token %r for %s (timeout: %i sec)', token, device_user.uuid, timeout)
    return token


def get_device_user_by_token(token):
    if device_user_uuid := cache.get(key=_make_cache_key(token)):
        logger.debug('Token %r == %r', token, device_user_uuid)
        device_user = DeviceUser.objects.filter(uuid=device_user_uuid).first()
        if device_user:
            logger.debug('Found device %s for token %r', device_user, token)
            return device_user
        else:
            logger.error('DeviceUser not found for token: %r', token)
    else:
        logger.error('Token %r not valid or expired', token)

    raise Http404
