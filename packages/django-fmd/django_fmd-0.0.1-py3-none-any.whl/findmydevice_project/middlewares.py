import json
import logging

from bx_django_utils.humanize.pformat import pformat
from debug_toolbar.middleware import show_toolbar
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse

from findmydevice.json_utils import parse_json


logger = logging.getLogger(__name__)


def djdt_show(request):
    """
    Determining whether the Django Debug Toolbar should show or not.
    """
    if not settings.DEBUG:
        return False

    content_type = request.content_type
    if content_type == 'application/json':
        return False

    return show_toolbar(request)


class TracingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if settings.DEBUG:
            logger.debug('_' * 100)
            logger.debug(f' {request.method} {request.path}')
            content_type = request.content_type
            logger.debug(f'Content Type: {content_type}')
            logger.debug(f'Headers: {pformat(request.headers)}')
            if content_type == 'application/json':
                data = parse_json(request)
                logger.debug(pformat(data))
            else:
                logger.debug(f'Body: {request.body!r}')
            logger.debug(' -' * 50)

        response: HttpResponse = self.get_response(request)
        if settings.DEBUG:
            logger.debug(' -' * 50)
            logger.debug(repr(response))
            if 200 <= response.status_code <= 299 and hasattr(response, 'content'):
                content = response.content
                if isinstance(response, JsonResponse):
                    data = json.loads(content)
                    logger.debug(pformat(data))
                else:
                    logger.debug(f'Content: {content!r}')

            logger.debug('-' * 100)

        return response
