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
        room_since = int(self.scope['url_route']['kwargs']['room'])
        message_since = int(self.scope['url_route']['kwargs']['message'])

        if await self.check_token_exists(token):
            self.token = token
            self.user = await self.get_user_from_token()

            await self.channel_layer.group_add(
                self.name,
                self.channel_name
            )

            await self.send({
                'type': 'websocket.accept'
            })

            await self.send_room_updates_to_client(room_since, message_since)
            await self.send_message_updates_to_client(room_since, message_since)

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
                #          sender_unique: "<username>_aH4x",
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
                            'hash': message_obj.file.file.name,
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

                    response_time = self.dt_to_long(message_obj.time)
                    response_id = message_obj.id
                    response_room_name = room_obj.name
                    response_room_participants = self.pk_array_from_queryset(room_obj.participants.all())
                    response_sender_unique = attr.get("sender_unique")

                    response_attr = {
                        'object': 'message',
                        'content': content,
                        'file': response_file,
                        'room': room,
                        'room_name': response_room_name,
                        'room_participants': response_room_participants,
                        'sender': self.user.username,
                        'sender_id': self.user.pk,
                        'sender_unique': response_sender_unique,
                        'location': response_location,
                        'message_id': response_id,
                        'time': response_time,
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
                #          sender_unique: "<username>_aH4x",
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
                    response_time = self.dt_to_long(room_obj.time_created)

                    response_attr = {
                        'object': 'room',
                        'name': name,
                        'id': response_id,
                        'time': response_time
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
                    notification_id = response_id
                    notification_sender = self.user.username
                    notification_sender_id = self.user.pk
                    notification_participants = participants
                    notification_sender_unique = attr.get("sender_unique")
                    notification_time = response_time

                    notification_attr = {
                        'object': 'room',
                        'name': name,
                        'id': notification_id,
                        'sender': notification_sender,
                        'sender_id': notification_sender_id,
                        'sender_unique': notification_sender_unique,
                        'participants': notification_participants,
                        'time': notification_time,
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

    def pk_array_from_queryset(self, qs):
        return [item.pk for item in qs]

    def dt_to_long(self, dt):
        return dt.timestamp() * 1000

    async def send_room_updates_to_client(self, room_since, message_since):
        if room_since != -1:
            rooms = await self.get_rooms_since_room(room_since)
        elif message_since != -1:
            rooms = await self.get_rooms_since_message(message_since)
        else:
            rooms = await self.get_rooms()

        for room in rooms:
            print("SENDING ROOM {id} TO CLIENT".format(id=room.pk))
            notification_attr = {
                'object': 'room',
                'name': room.name,
                'id': room.pk,
                'time': self.dt_to_long(room.time_created),
                'sender': room.creator.username,
                'sender_id': room.creator.pk,
                'sender_unique': "server-notification-repeat",
                'participants': self.pk_array_from_queryset(room.participants.all())
            }

            notification = {
                'type': 'notification',
                'attr': notification_attr
            }

            await self.send({
                'type': 'websocket.send',
                'text': json.dumps(notification)
            })

    async def send_message_updates_to_client(self, room_since, message_since):
        if room_since != -1:
            messages = await self.get_messages_since_room(room_since)
        elif message_since != -1:
            messages = await self.get_messages_since_message(message_since)
        else:
            messages = await self.get_messages()

        for message in messages:
            print("SENDING MESSAGE {id} TO CLIENT".format(id=message.pk))
            notification_location = None
            if message.location is not None:
                notification_location = {
                    'latitude': message.location.lat,
                    'longitude': message.location.lon
                }

            notification_file = None
            if message.file is not None:
                notification_file = {
                    'hash': message.file.file.name,
                    'name': message.file.name
                }

            notification_attr = {
                'object': 'message',
                'content': message.content,
                'message_id': message.pk,
                'time': self.dt_to_long(message.time),
                'sender': message.sender.username,
                'sender_id': message.sender.pk,
                'sender_unique': "server-notification-repeat",
                'room_participants': self.pk_array_from_queryset(message.room.participants.all()),
                'room': message.room.pk,
                'room_name': message.room.name,
                'location': notification_location,
                'file': notification_file
            }

            notification = {
                'type': 'notification',
                'attr': notification_attr
            }

            await self.send({
                'type': 'websocket.send',
                'text': json.dumps(notification)
            })

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
        room_obj = Room.objects.create(creator=self.user, name=name)
        room_obj.participants.add(*participants)
        return room_obj

    @database_sync_to_async
    def get_rooms_since_room(self, room):
        rooms = Room.objects.filter(participants=self.user)

        room_since_obj = Room.objects.filter(pk=room).first()

        time_since = room_since_obj.time_created

        return rooms.filter(time_created__gt=time_since)

    @database_sync_to_async
    def get_rooms_since_message(self, message):
        rooms = Room.objects.filter(participants=self.user)

        message_since_obj = Message.objects.filter(pk=message).first()

        time_since = message_since_obj.time

        return rooms.filter(time_created__gt=time_since)

    @database_sync_to_async
    def get_rooms(self):
        rooms = Room.objects.filter(participants=self.user)

        return rooms

    @database_sync_to_async
    def get_messages_since_room(self, room):
        messages = Message.objects.filter(room__participants=self.user)

        room_since_obj = Room.objects.filter(pk=room).first()

        time_since = room_since_obj.time_created

        return messages.filter(time__gt=time_since)

    @database_sync_to_async
    def get_messages_since_message(self, message):
        messages = Message.objects.filter(room__participants=self.user)

        message_since_obj = Message.objects.filter(pk=message).first()

        time_since = message_since_obj.time

        return messages.filter(time__gt=time_since)

    @database_sync_to_async
    def get_messages(self):
        messages = Message.objects.filter(room__participants=self.user)

        return messages