from django.http import JsonResponse
from django.views import View

from findmydevice.json_utils import parse_json
from findmydevice.models import Location
from findmydevice.models.device_user import get_device_user_by_token


class LocationDataSizeView(View):
    """
    /locationDataSize
    b'{"IDT":"6rGVbbtnpcfD","Data":"-1"}'
    """

    def put(self, request):
        put_data = parse_json(request)
        print(self, 'put', put_data)
        access_token = put_data['IDT']
        index = int(put_data['Data'])  # TODO

        device_user = get_device_user_by_token(token=access_token)
        location_count = Location.objects.filter(device_user=device_user).count()
        response_data = {
            'DataLength': location_count,  # newestLocationDataIndex
            'DataBeginningIndex': 0,  # smallestLocationDataIndex
        }
        return JsonResponse(response_data)
