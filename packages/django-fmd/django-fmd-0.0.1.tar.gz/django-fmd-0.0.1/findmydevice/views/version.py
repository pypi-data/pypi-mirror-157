from django.http import HttpResponse
from django.views import View

import findmydevice


class VersionView(View):
    def get(self, request):
        return HttpResponse(f' | Django Find My Device v{findmydevice.__version__} | ')
