import json

from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer
from channels.db import database_sync_to_async

from rest_framework.authtoken.models import Token

from app_files.models import File
from app_rooms.models import Room
from app_messages.models import Location, Message


class GlobalConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        self.token = None
        self.user = None
        self.name = 'flack_notifications'

        token = self.scope['url_route']['kwargs']['token']

        if await self.check_token_exists(token):
            self.token = token

            await self.channel_layer.group_add(
                self.name,
                self.channel_name
            )

            await self.send({
                'type': 'websocket.accept'
            })

        else:
            await self.send({
                'type': 'websocket.close'
            })

    async def websocket_receive(self, event):
        print("message received", event)
        request_json = event.get('text')

        if request_json is not None:
            request = json.loads(request_json)

            #
            # check if request properly structured
            #
            if request.get("type") == "create":
                attr = request.get("attr")

                # a proper message creation request has the following structure:
                #
                #  {
                #      type: "create",
                #      attr: {
                #          object: "message",
                #          content: "lorem ipsum dolor sit amet",
                #          file: <null or [1-9][0-9]*>
                #          room: <any valid room pk/id>,
                #          location: {
                #              latitude: <some float>,
                #              longitude: <some float>
                #          } <or null>
                #      }
                #  }

                if attr.get("object") == "message":
                    #
                    # create message in database
                    #
                    content = attr.get("content")

                    file = attr.get("file")
                    if file is not None:
                        file_obj = await self.get_file(file)
                    else:
                        file_obj = None

                    room = attr.get("room")
                    room_obj = await self.get_room(room)

                    if self.user is None:
                        self.user = await self.get_user_from_token()

                    sender = self.user

                    loc_dict = attr.get("location")

                    if loc_dict is not None:
                        lat = loc_dict.get("latitude")
                        lon = loc_dict.get("longitude")
                        location = await self.create_location(lat, lon)
                    else:
                        location = None

                    message_obj = await self.create_message(content, file_obj, room_obj, sender, location)

                    #
                    # respond to sender
                    #
                    if file is not None:
                        response_file = {
                            'name': message_obj.file.name,
                            'url': message_obj.file.file.url
                        }
                    else:
                        response_file = None

                    if loc_dict is not None:
                        response_location = {
                            'latitude': lat,
                            'longitude': lon
                        }
                    else:
                        response_location = None

                    response_time = message_obj.time
                    response_id = message_obj.id

                    response_attr = {
                        'object': 'message',
                        'content': content,
                        'file': response_file,
                        'room': room,
                        'sender': self.user.username,
                        'location': response_location,
                        'message_id': response_id,
                        'time': str(response_time),
                    }

                    response = {
                        'type': 'response',
                        'attr': response_attr
                    }
                    await self.send({
                        'type': 'websocket.send',
                        'text': json.dumps(response)
                    })

                    #
                    # broadcast message creation
                    #
                    notification_attr = response_attr

                    notification = {
                        'type': 'notification',
                        'attr': notification_attr
                    }
                    await self.channel_layer.group_send(
                        self.name,
                        {
                            'type': 'broadcast',
                            'text': json.dumps(notification)
                        }
                    )

                # a proper room creation request looks like this:
                #
                #  {
                #      type: "create",
                #      attr: {
                #          object: "room",
                #          name: name,
                #          participants: participants
                #      }
                #  }

                elif attr.get("object") == "room":
                    #
                    # create room in database
                    #
                    name = attr.get("name")
                    participants = attr.get("participants")

                    room_obj = await self.create_room(name, participants)

                    #
                    # respond to sender
                    #
                    response_id = room_obj.id
                    response_attr = {
                        'object': 'room',
                        'name': name,
                        'room_id': response_id
                    }

                    response = {
                        'type': 'response',
                        'attr': response_attr
                    }

                    await self.send({
                        'type': 'websocket.send',
                        'text': json.dumps(response)
                    })

                    #
                    # broadcast room creation
                    #
                    if self.user is None:
                        self.user = await self.get_user_from_token()

                    notification_id = response_id
                    notification_sender = self.user.username
                    notification_participants = participants

                    notification_attr = {
                        'object': 'room',
                        'name': name,
                        'room_id': notification_id,
                        'sender': notification_sender,
                        'participants': notification_participants
                    }

                    notification = {
                        'type': 'notification',
                        'attr': notification_attr
                    }
                    await self.channel_layer.group_send(
                        self.name,
                        {
                            'type': 'broadcast',
                            'text': json.dumps(notification)
                        }
                    )

    async def broadcast(self, event):
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    async def websocket_disconnect(self, event):
        print("disconnected", event)
        raise StopConsumer()

    @database_sync_to_async
    def check_token_exists(self, token):
        return Token.objects.filter(key=token).exists()

    @database_sync_to_async
    def get_user_from_token(self):
        return Token.objects.filter(key=self.token).first().user

    @database_sync_to_async
    def get_file(self, file_id):
        return File.objects.filter(pk=file_id).first()

    @database_sync_to_async
    def get_room(self, room_id):
        return Room.objects.filter(pk=room_id).first()

    @database_sync_to_async
    def create_location(self, latitude, longitude):
        return Location.objects.create(lat=latitude, lon=longitude)

    @database_sync_to_async
    def create_message(self, content, file, room, sender, location):
        return Message.objects.create(content=content, file=file, room=room, sender=sender, location=location)

    @database_sync_to_async
    def create_room(self, name, participants):
        room_obj = Room.objects.create(name=name)
        room_obj.participants.add(*participants)
        return room_obj
