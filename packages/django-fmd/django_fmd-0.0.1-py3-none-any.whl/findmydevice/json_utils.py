import json


def parse_json(request):
    content_type = request.content_type
    assert content_type == 'application/json'
    encoding = request.encoding or 'utf-8'
    json_data = request.body.decode(encoding)
    data = json.loads(json_data)
    return data
