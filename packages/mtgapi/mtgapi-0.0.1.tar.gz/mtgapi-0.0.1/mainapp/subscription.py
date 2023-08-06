import pathlib
from collections import defaultdict
from typing import DefaultDict, List

import asgiref
import channels
import channels.auth
import django
import django.contrib.admin
import django.contrib.auth
import django.core.asgi
import graphene
import graphene_django.types

import channels_graphql_ws

class Message(  # type: ignore
    graphene.ObjectType, default_resolver=graphene.types.resolver.dict_resolver):
    """Message GraphQL type."""

    chatroom = graphene.String()
    text = graphene.String()
    sender = graphene.String()



class OnNewChatMessage(channels_graphql_ws.Subscription):
    """Subscription triggers on a new chat message."""

    sender = graphene.String()
    chatroom = graphene.String()
    text = graphene.String()

    class Arguments:
        """Subscription arguments."""
        chatroom = graphene.String()

    def subscribe(self, info, chatroom=None):
        """Client subscription handler."""
        del info
        # Specify the subscription group client subscribes to.
        return [chatroom] if chatroom is not None else None

    def publish(self, info, chatroom=None):
        """Called to prepare the subscription notification message."""

        # The `self` contains payload delivered from the `broadcast()`.
        new_msg_chatroom = self["chatroom"]
        new_msg_text = self["text"]
        new_msg_sender = self["sender"]

        # # Method is called only for events on which client explicitly
        # # subscribed, by returning proper subscription groups from the
        # # `subscribe` method. So he either subscribed for all events or
        # # to particular chatroom.
        # assert chatroom is None or chatroom == new_msg_chatroom

        # # Avoid self-notifications.
        # if (
        #     info.context.user.is_authenticated
        #     and new_msg_sender == info.context.user.username
        # ):
        #     return OnNewChatMessage.SKIP

        return OnNewChatMessage(
            chatroom=chatroom, text=new_msg_text, sender=new_msg_sender
        )

    @classmethod
    def new_chat_message(cls, chatroom, text, sender):
        """Auxiliary function to send subscription notifications.
        It is generally a good idea to encapsulate broadcast invocation
        inside auxiliary class methods inside the subscription class.
        That allows to consider a structure of the `payload` as an
        implementation details.
        """
        cls.broadcast(
            group=chatroom,
            payload={"chatroom": chatroom, "text": text, "sender": sender},
        )

