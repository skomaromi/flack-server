from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

from .serializers import LoginModelSerializer, UserModelSerializer

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
                    'user': {
                        'name': user.username,
                        'id': user.id
                    },
                    'token': token.key
                }
                return Response(content)
            else:
                raise AuthenticationFailed(detail='invalid username or password')
        else:
            raise AuthenticationFailed(detail='username or password not provided')


class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserModelSerializer

    def get_queryset(self, *args, **kwargs):
        qs = self.queryset.none()
        token = self.request.GET.get("token")
        query = self.request.GET.get("q")

        if token is not None:
            token_objs = Token.objects.filter(key=token)

            if token_objs.exists():
                qs = self.queryset.all()
                token_obj = token_objs.first()
                user_id = token_obj.user.id

                qs = qs.exclude(id=user_id)

                if query is not None:
                    qs = qs.filter(username__icontains=query)

            else:
                raise AuthenticationFailed(detail="token invalid")
        else:
            raise AuthenticationFailed(detail="token not provided")

        return qs