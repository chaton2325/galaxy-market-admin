import requests
from flask import session, redirect, url_for, flash

class APIClient:
    BASE_URL = "https://galaxy.mirhosty.com/api/admin"

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
        headers = cls.get_headers()
        
        # Merge headers if provided in kwargs
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
        
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            if response.status_code == 401:
                # Handle unauthorized access (e.g., redirect to login)
                # Note: This is a utility class, actual redirect should happen in the view
                pass
            return response
        except requests.exceptions.RequestException as e:
            print(f"API Request Error: {e}")
            return None

    @classmethod
    def get(cls, endpoint, params=None):
        return cls.request('GET', endpoint, params=params)

    @classmethod
    def post(cls, endpoint, json=None):
        return cls.request('POST', endpoint, json=json)

    @classmethod
    def patch(cls, endpoint, json=None, params=None):
        return cls.request('PATCH', endpoint, json=json, params=params)

    @classmethod
    def delete(cls, endpoint, params=None):
        return cls.request('DELETE', endpoint, params=params)
