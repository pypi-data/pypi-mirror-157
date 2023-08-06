import requests
from enum import Enum
from typing import Dict

from racetrack_client.utils.request import parse_response


RT_AUTH_HEADER = 'X-Racetrack-Auth'


class RacetrackAuthMethod(Enum):
    TOKEN = 'racetrackAuth'


class AuthError(RuntimeError):
    def __init__(self, cause: str):
        super().__init__()
        self.cause = cause

    def __str__(self):
        return f'authentication error: {self.cause}'


def get_auth_request_headers(user_auth: str) -> Dict:
    return {
        RT_AUTH_HEADER: user_auth if user_auth != "" else None
    }


def is_auth_required(lifecycle_url: str) -> bool:
    r = requests.get(
        f'{lifecycle_url}/api/v1/info',
        verify=False,
    )
    response = parse_response(r, 'Lifecycle response error')
    return response["auth_required"]


def validate_user_auth(lifecycle_url: str, user_auth: str) -> str:
    r = requests.get(
        f'{lifecycle_url}/api/v1/users/validate_user_auth',
        headers=get_auth_request_headers(user_auth),
        verify=False,
    )
    if r.status_code == 401:
        raise AuthError('Invalid Auth Token')

    response = parse_response(r, 'Lifecycle response error')
    return response['username']
