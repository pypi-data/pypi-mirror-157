import base64
import json

import requests


class ConfigDetector:
    @classmethod
    def detect(cls, email):
        headers = {'x-email': email}
        url = 'https://prod-autodetect.outlookmobile.com/detect?services=office365,google,outlook,yahoo,icloud&protocols=all&timeout=15'
        response = requests.get(url, headers=headers)
        if response is None or response.content is None or len(response.content) == 0:
            return None

        try:
            result = json.loads(response.content)
        except Exception as e:
            return None

        return result
