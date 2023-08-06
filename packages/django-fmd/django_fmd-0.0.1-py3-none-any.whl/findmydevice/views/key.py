from django.http import HttpResponse
from django.views import View

from findmydevice.json_utils import parse_json
from findmydevice.models import DeviceUser
from findmydevice.models.device_user import get_device_user_by_token


class KeyView(View):
    """
    /key
    """

    def put(self, request):
        """
        e.g:
            {'Data': '1', 'IDT': 'LPYzPAFwLa8u'}
        """
        put_data = parse_json(request)
        access_token = put_data['IDT']
        index = int(put_data['Data'])  # TODO

        device_user: DeviceUser = get_device_user_by_token(token=access_token)
        privkey = device_user.privkey
        return HttpResponse(content_type='application/text', content=privkey)
