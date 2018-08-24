from datetime import datetime

from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ParseError, AuthenticationFailed

from ..models import Room
from .serializers import RoomModelSerializer


class RoomListAPIView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomModelSerializer

    def get_queryset(self, *args, **kwargs):
        qs = self.queryset.none()
        token = self.request.GET.get("token")
        time_since = self.request.GET.get("time_since")

        if token is not None:
            token_objs = Token.objects.filter(key=token)

            if token_objs.exists():
                qs = self.queryset.all()
                token_obj = token_objs.first()
                user = token_obj.user

                qs = qs.filter(participants=user)

                if time_since is not None:
                    try:
                        time_since_parsed = datetime.strptime(time_since, "%Y%m%d-%H%M")
                    except:
                        raise ParseError(detail="invalid time_since")
                    qs = qs.filter(time_created__gte=time_since_parsed)

            else:
                raise AuthenticationFailed(detail="token invalid")

        else:
            raise AuthenticationFailed(detail="token not provided")

        return qs
