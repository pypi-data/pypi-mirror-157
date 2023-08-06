import logging
from uuid import UUID

from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.views import View

from findmydevice.json_utils import parse_json
from findmydevice.models import DeviceUser
from findmydevice.models.device_user import new_access_token


logger = logging.getLogger(__name__)


class RequestAccessView(View):
    """
    /requestAccess
    """

    def put(self, request):
        access_data = parse_json(request)
        hashed_password = access_data['Data']

        # App sends hex digest in uppercase, the web page in lower case ;)
        hashed_password = hashed_password.lower()

        device_user_id = access_data['IDT']
        try:
            device_user_id = UUID(device_user_id)
        except ValueError as err:
            logger.error('IDT %r is no UUID: %s', device_user_id, err)
            return HttpResponseForbidden()

        device_user = DeviceUser.objects.filter(uuid=device_user_id).first()
        if not device_user:
            logger.error('DeviceUser entry not found for: %r', device_user_id)
            return HttpResponseBadRequest()

        if hashed_password != device_user.hashed_password:
            logger.error(
                'Wrong password %r is not %r for %s',
                hashed_password,
                device_user.hashed_password,
                device_user,
            )
            return HttpResponseForbidden()

        access_token = new_access_token(device_user=device_user)
        accesstoken_reply = {'IDT': device_user.uuid, 'Data': access_token}
        return JsonResponse(accesstoken_reply)
