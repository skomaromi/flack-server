from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

from .serializers import LoginModelSerializer

User = get_user_model()


class LoginAPIView(APIView):
    serializer_class = LoginModelSerializer

    def post(self, request, format=None):
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        if all([username, password]):
            user = User.objects.filter(username=username)

            if user.exists():
                user = user.first()
            else:
                raise AuthenticationFailed(detail='user does not exist')

            if user.check_password(password):
                token, created = Token.objects.get_or_create(user=user)

                content = {
                    'message': 'success',
                    'user': username,
                    'token': token.key
                }
                return Response(content)
            else:
                raise AuthenticationFailed(detail='invalid username or password')
        else:
            raise AuthenticationFailed(detail='username or password not provided')
