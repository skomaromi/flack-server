from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed, ParseError
from rest_framework.parsers import FormParser

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .serializers import UserModelSerializer

User = get_user_model()


class LoginAPIView(APIView):
    parser_classes = (FormParser,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="username",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                name="password",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Occurs only when both username and password are provided, the username exists in the "
                            "database and the password is right.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            description="Request status. The only value that is currently returned is 'success'.",
                            type=openapi.TYPE_STRING,
                            example='success'
                        ),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'name': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    example='exampleuser'
                                ),
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER)
                            }
                        ),
                        'token': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example='1234567890abcdefghijklmnopqrstuvwxyz1234'
                        )
                    }
                )
            ),
            403: openapi.Response(
                description="Occurs when either or both username or password are absent or wrong.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(
                            description="Error message describing why the authentication failed.",
                            type=openapi.TYPE_STRING,
                            example='user does not exist'
                        )
                    }
                )
            )
        }
    )
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
    parser_classes = (FormParser,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="username",
                in_=openapi.IN_FORM,
                description="Username. Has to be unique.",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                name="password",
                in_=openapi.IN_FORM,
                description="Password. Has to be at least 6 characters long.",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Occurs only when both username and password are provided, the password is at least six "
                            "(6) characters long and the username is unique.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            description="Request status. The only value that is currently returned is 'success'.",
                            type=openapi.TYPE_STRING,
                            example='success'
                        ),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'name': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    example='exampleuser'
                                ),
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER)
                            }
                        ),
                        'token': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example='1234567890abcdefghijklmnopqrstuvwxyz1234'
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="Occurs when conditions for the HTTP 200 (OK) response are not met.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(
                            description="Error message describing why the registration failed.",
                            type=openapi.TYPE_STRING,
                            example="user 'exampleuser' already exists"
                        )
                    }
                )
            )
        }
    )
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
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="username",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description='',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'username': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example='exampleuser'
                        ),
                        'exists': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: openapi.Response(
                description="Occurs when username is not provided",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(
                            description="Error message which says that the username is not provided.",
                            type=openapi.TYPE_STRING,
                            example="username not provided"
                        )
                    }
                )
            )
        }
    )
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
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Specially structured to discern a Flack server from any other server to which a client "
                            "might test connectivity.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'text': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example='flack-pong'
                        )
                    }
                )
            )
        }
    )
    def get(self, request):
        content = {
            'text': 'flack-pong'
        }
        return Response(content)


@method_decorator(name='get', decorator=swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            name="token",
            in_=openapi.IN_QUERY,
            description="Token. Used to authenticate request provider and exclude them from results.",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            name="q",
            in_=openapi.IN_QUERY,
            description="Query. If not empty, returns only users which contain given string.",
            type=openapi.TYPE_STRING,
        )
    ],
    responses={
        403: openapi.Response(
            description="Occurs when authentication token is not provided or valid.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(
                        description="Error message describing why the user lookup failed.",
                        type=openapi.TYPE_STRING,
                        example='token not provided'
                    )
                }
            )
        )
    }
))
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

                qs = qs.order_by('username')

            else:
                raise AuthenticationFailed(detail="token invalid")
        else:
            raise AuthenticationFailed(detail="token not provided")

        return qs
