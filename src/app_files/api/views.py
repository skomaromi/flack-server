from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

from ..models import File
from .serializers import FileModelSerializer


class UploadAPIView(APIView):
    serializer_class = FileModelSerializer

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
                        'url': file.file.url,
                        'name': file.name,
                        'id': file.id
                    }
                }
                return Response(content)

            else:
                raise AuthenticationFailed(detail="token invalid")

        else:
            raise AuthenticationFailed(detail="token not provided")
