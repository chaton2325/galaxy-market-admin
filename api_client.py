import requests
from flask import session, redirect, url_for, flash

class APIClient:
    BASE_URL = "https://galaxy.mirhosty.com/api/admin"
    FINANCE_BASE_URL = "https://galaxy.mirhosty.com/api/finance"
    CARROUSEL_BASE_URL = "https://galaxy.mirhosty.com/api/carrousel"

    @staticmethod
    def get_headers():
        token = session.get('access_token')
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        return headers

    @classmethod
    def request(cls, method, endpoint, **kwargs):
        url = f"{cls.BASE_URL}{endpoint}"
        return cls.request_url(method, url, **kwargs)

    @classmethod
    def request_url(cls, method, url, **kwargs):
        headers = cls.get_headers()
        
        # Merge headers if provided in kwargs
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
        
        try:
            # If files are present, requests will automatically set the correct Content-Type for multipart/form-data
            # We don't want to set Content-Type manually if there's a file.
            response = requests.request(method, url, headers=headers, **kwargs)
            if response.status_code == 401:
                # Handle unauthorized access (e.g., redirect to login)
                pass
            return response
        except requests.exceptions.RequestException as e:
            print(f"API Request Error: {e}")
            return None

    @classmethod
    def finance_request(cls, method, endpoint, **kwargs):
        url = f"{cls.FINANCE_BASE_URL}{endpoint}"
        return cls.request_url(method, url, **kwargs)

    @classmethod
    def carrousel_request(cls, method, endpoint='', **kwargs):
        url = f"{cls.CARROUSEL_BASE_URL}{endpoint}"
        return cls.request_url(method, url, **kwargs)

    @classmethod
    def get(cls, endpoint, params=None):
        return cls.request('GET', endpoint, params=params)

    @classmethod
    def post(cls, endpoint, json=None, data=None, files=None):
        return cls.request('POST', endpoint, json=json, data=data, files=files)

    @classmethod
    def patch(cls, endpoint, json=None, data=None, files=None, params=None):
        return cls.request('PATCH', endpoint, json=json, data=data, files=files, params=params)

    @classmethod
    def delete(cls, endpoint, params=None):
        return cls.request('DELETE', endpoint, params=params)

    @classmethod
    def finance_get(cls, endpoint, params=None):
        return cls.finance_request('GET', endpoint, params=params)

    @classmethod
    def carrousel_get(cls, endpoint='', params=None):
        return cls.carrousel_request('GET', endpoint, params=params)

    @classmethod
    def carrousel_post(cls, endpoint='', json=None, data=None, files=None):
        return cls.carrousel_request('POST', endpoint, json=json, data=data, files=files)

    @classmethod
    def carrousel_patch(cls, endpoint='', json=None, data=None, files=None):
        return cls.carrousel_request('PATCH', endpoint, json=json, data=data, files=files)

    @classmethod
    def carrousel_delete(cls, endpoint=''):
        return cls.carrousel_request('DELETE', endpoint)
