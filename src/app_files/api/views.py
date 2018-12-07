import coreapi
import coreschema
import humanize

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.schemas import AutoSchema

from ..models import File
from .serializers import FileModelSerializer


class UploadAPIView(APIView):
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(
                name="token",
                required=True,
                location="form",
                schema=coreschema.String(
                    description="Token. Used to associate the uploaded file with its owner."
                )
            ),
            coreapi.Field(
                name="file",
                required=True,
                location="form",
                schema=coreschema.String(
                    # TODO: try switching to OpenAPI?
                    # CoreAPI was last updated in 2017, so coreschema.File might not happen sometime soon...
                    description="File. Uploading from Swagger **not implemented yet**."
                )

            )
        ]
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


class FileListAPIView(generics.ListAPIView):
    queryset = File.objects.all()
    serializer_class = FileModelSerializer

    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(
                name="token",
                required=True,
                schema=coreschema.String(
                    description="Token. Used to fetch only those files owned by the currently authenticated user "
                                "(and prevent seeing other people's files without permission)."
                )
            )
        ]
    )

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
