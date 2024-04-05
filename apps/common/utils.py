from django.utils import timezone
from rest_framework.permissions import BasePermission
from apps.accounts.auth import Authentication
from apps.accounts.models import User, AuthTransaction as Jwt
from apps.common.exceptions import RequestError
from datetime import timedelta
from uuid import UUID
from django.http import HttpRequest
from typing import Optional
import datetime
import pytz








class IsAuthenticatedCustom(BasePermission):
    def has_permission(self, request, view):
        http_auth = request.META.get("HTTP_AUTHORIZATION")
        if not http_auth:
            raise RequestError(err_msg="Auth Bearer not provided!", status_code=401)
        user = Authentication.decodeAuthorization(http_auth)
        if not user:
            raise RequestError(
                err_msg="Auth Token is Invalid or Expired!", status_code=401
            )
        request.user = user
        if request.user and request.user.is_authenticated:
            return True
        return False

def get_client_ip(request: HttpRequest) -> Optional[str]:
    """
    Fetches the IP address of a client from Request and
    return in proper format.

    Parameters
    ----------
    request: django.http.HttpRequest

    Returns
    -------
    ip: str or None
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    else:
        return request.META.get("REMOTE_ADDR")


def datetime_passed_now(source: datetime.datetime) -> bool:
    """
    Compares provided datetime with current time on the basis of Django
    settings. Checks source is in future or in past. False if it's in future.
    Parameters
    ----------
    source: datetime object than may or may not be naive

    Returns
    -------
    bool

    Author: Himanshu Shankar (https://himanshus.com)
    """
    if source.tzinfo is not None and source.tzinfo.utcoffset(source) is not None:
        return source <= datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    else:
        return source <= datetime.datetime.now()
    

def check_unique(prop: str, value: str) -> bool:
    """
    This function checks if the value provided is present in Database
    or can be created in DBMS as unique data.
    Parameters
    ----------
    prop: str
        The model property to check for. Can be::
            email
            mobile
            username
    value: str
        The value of the property specified

    Returns
    -------
    bool
        True if the data sent is doesn't exist, False otherwise.
    Examples
    --------
    To check if test@testing.com email address is already present in
    Database
    >>> print(check_unique('email', 'test@testing.com'))
    True
    """
    user = User.objects.extra(where=[prop + " = '" + value + "'"])
    return user.count() == 0

def is_uuid(value):
    try:
        return str(UUID(value))
    except:
        return None


def is_int(value):
    if not value:
        return None
    try:
        return int(value)
    except:
        raise RequestError(err_msg="Invalid Quantity params", status_code=422)


# Test Utils
class TestUtil:
    def new_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Name",
            "email": "test@example.com",
        }
        user = User(**user_dict)
        user.set_password("testpassword")
        user.save()
        return user

    def verified_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Verified",
            "email": "testverifieduser@example.com",
            "is_email_verified": True,
        }
        user = User(**user_dict)
        user.set_password("testpassword")
        user.save()
        return user

    def another_verified_user():
        create_user_dict = {
            "first_name": "AnotherTest",
            "last_name": "UserVerified",
            "email": "anothertestverifieduser@example.com",
            "is_email_verified": True,
        }
        user = User(**create_user_dict)
        user.set_password("anothertestverifieduser123")
        user.save()
        return user

    def auth_token(verified_user):
        access = Authentication.create_access_token({"user_id": str(verified_user.id)})
        refresh = Authentication.create_refresh_token()
        Jwt.objects.create(user_id=verified_user.id, access=access, refresh=refresh)
        return access
