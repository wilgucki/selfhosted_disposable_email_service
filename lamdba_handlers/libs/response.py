import json
from typing import Dict


def response(status_code=200, body=None, headers=None) -> Dict:
    if headers is not None and not isinstance(headers, Dict):
        raise TypeError('Invalid type: headers')

    if body is not None and not isinstance(body, Dict):
        raise TypeError('Invalid type: body')

    r = {'statusCode': status_code}
    if headers is not None:
        r['headers'] = headers
    if body is not None:
        r['body'] = json.dumps(body)

    return r
