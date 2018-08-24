from datetime import datetime

from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ParseError, AuthenticationFailed

from ..models import Message
from .serializers import MessageModelSerializer


class MessageListAPIView(generics.ListAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageModelSerializer

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

                qs = qs.filter(room__participants=user)

                if time_since is not None:
                    try:
                        time_since_parsed = datetime.strptime(time_since, "%Y%m%d-%H%M")
                    except:
                        raise ParseError(detail="invalid time_since")
                    qs = qs.filter(time__gte=time_since_parsed)

            else:
                raise AuthenticationFailed(detail="token invalid")

        else:
            raise AuthenticationFailed(detail="token not provided")

        return qs
