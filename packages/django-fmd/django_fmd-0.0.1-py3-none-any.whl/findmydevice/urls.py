from pathlib import Path

from django.conf import settings
from django.urls import path
from django.views.static import serve

import findmydevice
from findmydevice.views.base_views import CommandView, PictureView, PostPushLinkView
from findmydevice.views.device import DeviceView
from findmydevice.views.key import KeyView
from findmydevice.views.location import LocationView
from findmydevice.views.location_data_size import LocationDataSizeView
from findmydevice.views.request_access import RequestAccessView
from findmydevice.views.version import VersionView


WEB_PATH = Path(findmydevice.__file__).parent / 'web'
assert WEB_PATH.is_dir(), f'Directory not found here: {WEB_PATH}'

urlpatterns = [
    path('command', CommandView.as_view(), name='command'),
    path('location', LocationView.as_view(), name='location'),
    path('locationDataSize', LocationDataSizeView.as_view(), name='location_data_size'),
    path('picture', PictureView.as_view(), name='picture'),
    path('key', KeyView.as_view(), name='key'),
    path('device', DeviceView.as_view(), name='device'),
    path('push', PostPushLinkView.as_view(), name='push'),
    path('requestAccess', RequestAccessView.as_view(), name='request_access'),
    path('version', VersionView.as_view(), name='version'),
]
if settings.DEBUG:
    # TODO: Serve from real Web server ;)
    urlpatterns.append(path('<path:path>', serve, {'document_root': WEB_PATH}))
