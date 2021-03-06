from datetime import datetime

from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ParseError, AuthenticationFailed

from app_messages.models import Message

from ..models import Room
from .serializers import RoomModelSerializer


class RoomListAPIView(generics.ListAPIView):
    """
    **DEPRECATED**

    Room list API endpoint. Updates are delivered via WS, so this endpoint should **not** be used.
    """
    queryset = Room.objects.all()
    serializer_class = RoomModelSerializer

    def get_queryset(self, *args, **kwargs):
        qs = self.queryset.none()
        token = self.request.GET.get("token")
        room_since = self.request.GET.get("room")
        message_since = self.request.GET.get("message")

        if token is not None:
            token_objs = Token.objects.filter(key=token)

            if token_objs.exists():
                qs = self.queryset.all()
                token_obj = token_objs.first()
                user = token_obj.user

                qs = qs.filter(participants=user)

                if room_since is not None:
                    room_objs = Room.objects.filter(pk=room_since)

                    if room_objs.exists():
                        room_obj = room_objs.first()
                        time_since = room_obj.time_created

                        qs = qs.filter(time_created__gt=time_since)

                    else:
                        raise ParseError(detail="invalid room id provided")

                elif message_since is not None:
                    message_objs = Message.objects.filter(pk=message_since)

                    if message_objs.exists():
                        message_obj = message_objs.first()
                        time_since = message_obj.time

                        qs = qs.filter(time_created__gt=time_since)

                    else:
                        raise ParseError(detail="invalid message id provided")

            else:
                raise AuthenticationFailed(detail="token invalid")

        else:
            raise AuthenticationFailed(detail="token not provided")

        return qs
