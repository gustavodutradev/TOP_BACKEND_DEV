import requests
from dotenv import load_dotenv
import uuid
import time
import json
import os

class TokenService:

    def __init__(self) -> None:
        self.__auth_url = 'https://api.btgpactual.com/iaas-auth/api/v1/authorization/oauth2/accesstoken'
        load_dotenv()
        self.__auth_base64 = os.getenv('AUTH_BASE64')
        self.__uuid = uuid.uuid4()
        self.__headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': '*/*',
            'Authorization': f'Basic {self.__auth_base64}',
            'x-id-partner-request': str(self.__uuid)
        }
        self.__body = {
            'grant_type': 'client_credentials'
        }
        self.__cache_file = 'token_cache.json'

    def __get_access_token(self):
        cached_token = self.__load_cached_token()
        if cached_token and not self.__is_token_expired(cached_token):
            print("Using cached token")
            return cached_token['access_token']

        response = requests.post(self.__auth_url, headers=self.__headers, data=self.__body)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            expires_in = token_data['expires']
            token_expires_at = time.time() + expires_in

            self.__save_token_to_cache(access_token, token_expires_at)

            print("Fetched new token", access_token)
            print(f"Token expires at: {token_expires_at}")
            return access_token
        else:
            raise Exception(f"Failed to fetch access token: {response.status_code} - {response.text}")

    def __is_token_expired(self, cached_token) -> bool:
        return time.time() > cached_token['expires_at']

    def __save_token_to_cache(self, access_token, expires_at):
        token_data = {
            'access_token': access_token,
            'expires_at': expires_at
        }
        with open(self.__cache_file, 'w') as cache_file:
            json.dump(token_data, cache_file)

    def __load_cached_token(self):
        if os.path.exists(self.__cache_file):
            with open(self.__cache_file, 'r') as cache_file:
                return json.load(cache_file)
        return None

    def get_token(self):
        return self.__get_access_token()

