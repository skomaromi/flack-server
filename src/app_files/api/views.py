import humanize

from django.utils.decorators import method_decorator

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from ..models import File
from .serializers import FileModelSerializer


class UploadAPIView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="token",
                in_=openapi.IN_FORM,
                description="Token. Used to associate the uploaded file with its owner.",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                name="file",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description='',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            description="Request status. The only value that is currently returned is 'success'.",
                            type=openapi.TYPE_STRING,
                            example='success'
                        ),
                        'file': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'name': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    example='examplefile.ext'
                                ),
                                'hash': openapi.Schema(
                                    description="IPFS multihash of the uploaded file.",
                                    type=openapi.TYPE_STRING,
                                    example='Qm1234567890abcdefghijklmnopqrstuvwxyzABCDEFGH'
                                ),
                                'size': openapi.Schema(
                                    description="Uploaded file size in a human-readable form.",
                                    type=openapi.TYPE_STRING,
                                    example='42.4 kB'
                                ),
                                'url': openapi.Schema(
                                    description="URL of the uploaded file on the public ipfs.io gateway.",
                                    type=openapi.TYPE_STRING,
                                    example='https://ipfs.io/ipfs/Qm1234567890abcdefghijklmnopqrstuvwxyzABCDEFGH/examplefile.ext'
                                ),
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER)
                            }
                        )
                    }
                )
            ),
            403: openapi.Response(
                description="Occurs when authentication token is not provided or valid.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(
                            description="Error message describing why file upload failed.",
                            type=openapi.TYPE_STRING,
                            example='token not provided'
                        )
                    }
                )
            )
        }
    )
    def put(self, request, format=None):
        file_obj = request.FILES.get('file')
        file_name = file_obj.name

        token = request.POST.get('token')

        if token is not None:
            token_objs = Token.objects.filter(key=token)

            if token_objs.exists():
                token_obj = token_objs.first()
                user = token_obj.user

                file = File.objects.create(file=file_obj, name=file_name, owner=user)

                content = {
                    'message': 'success',
                    'file': {
                        'name': file.name,
                        'hash': file.file.name,
                        'size': humanize.naturalsize(file.file.size),
                        'url': file.file.url,
                        'id': file.id
                    }
                }
                return Response(content)

            else:
                raise AuthenticationFailed(detail="token invalid")

        else:
            raise AuthenticationFailed(detail="token not provided")


@method_decorator(name='get', decorator=swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            name="token",
            in_=openapi.IN_QUERY,
            description="Token. Used to fetch only those files owned by the currently authenticated user "
                        "(and prevent seeing other people's files without permission).",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        403: openapi.Response(
            description="Occurs when authentication token is not provided or valid.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(
                        description="Error message describing why the file lookup failed.",
                        type=openapi.TYPE_STRING,
                        example='token not provided'
                    )
                }
            )
        )
    }
))
class FileListAPIView(generics.ListAPIView):
    queryset = File.objects.all()
    serializer_class = FileModelSerializer

    def get_queryset(self, *args, **kwargs):
        qs = self.queryset.none()
        token = self.request.GET.get("token")

        if token is not None:
            token_objs = Token.objects.filter(key=token)

            if token_objs.exists():
                qs = self.queryset.all()
                token_obj = token_objs.first()
                user = token_obj.user

                qs = qs.filter(owner=user)

            else:
                raise AuthenticationFailed(detail="token invalid")
        else:
            raise AuthenticationFailed(detail="token not provided")

        return qs
