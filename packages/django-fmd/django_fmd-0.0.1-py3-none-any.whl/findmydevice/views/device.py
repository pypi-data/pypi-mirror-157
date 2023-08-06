import logging

from django.http import JsonResponse
from django.views import View

from findmydevice.json_utils import parse_json
from findmydevice.models import DeviceUser
from findmydevice.models.device_user import get_device_user_by_token


logger = logging.getLogger(__name__)


class DeviceView(View):
    """
    /device
    """

    def put(self, request):
        data = parse_json(request)
        hashed_password = data['hashedPassword']

        # App sends hex digest in uppercase, the web page in lower case ;)
        hashed_password = hashed_password.lower()

        device_user = DeviceUser.objects.create(
            hashed_password=hashed_password,
            privkey=data['privkey'],
            pubkey=data['pubkey'],
        )
        access_token = {'DeviceId': device_user.uuid, 'AccessToken': ''}
        return JsonResponse(access_token)

    def post(self, request, *args, **kwargs):
        """
        Delete a device
        """
        post_data = parse_json(request)

        access_token = post_data['IDT']
        device_user = get_device_user_by_token(token=access_token)
        logger.info('Delete device: %s', device_user)
        info = device_user.delete()
        logger.info('Delete info: %s', info)
        return JsonResponse(data={})
