from django.conf import settings

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions


class CustomAuthentication(JWTAuthentication):
    """Customer middleware for authenticating via HTTP only cookie JWT token"""

    def authenticate(self, request):
        header = self.get_header(request)

        if header is None:
            raw_token = request.COOKIES.get('access_token') or None
            if raw_token:
                raw_token = raw_token.encode('utf-8')
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except Exception as ex:
            print(ex)
            return None

        return self.get_user(validated_token), validated_token
