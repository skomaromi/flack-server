from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed, ParseError

from .serializers import UserModelSerializer

User = get_user_model()


class LoginAPIView(APIView):
    def post(self, request, format=None):
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        if not all([username, password]):
            raise AuthenticationFailed(detail='username or password not provided')

        user = User.objects.filter(username=username)

        if not user.exists():
            raise AuthenticationFailed(detail='user does not exist')

        user = user.first()

        if not user.check_password(password):
            raise AuthenticationFailed(detail='invalid username or password')

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


class RegisterAPIView(APIView):
    def post(self, request, format=None):
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        if not all([username, password]):
            raise ParseError(detail='username or password not provided')

        if len(password) < 6:
            raise ParseError(detail='password should be at least 6 characters long')

        user = User.objects.filter(username=username)

        if user.exists():
            raise ParseError(detail="user '{username}' already exists".format(username=username))

        new_user = User.objects.create(username=username)
        new_user.set_password(password)
        new_user.save()

        new_user_token, created = Token.objects.get_or_create(user=new_user)

        content = {
            'message': 'success',
            'user': {
                'name': new_user.username,
                'id': new_user.id
            },
            'token': new_user_token.key
        }
        return Response(content)


class UserExistsAPIView(APIView):
    def get(self, request):
        username = request.GET.get('username', None)

        if username is None:
            raise ParseError(detail='username not provided')

        user = User.objects.filter(username=username)

        content = {
            'username': username,
            'exists': user.exists()
        }
        return Response(content)


class PingAPIView(APIView):
    def get(self, request):
        content = {
            'text': 'flack-pong'
        }
        return Response(content)


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
