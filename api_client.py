import requests
from flask import session, redirect, url_for, flash

class APIClient:
    BASE_URL = "http://localhost:3000/api/admin"

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
