#  Hydrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-2023 Dan <https://github.com/delivrance>
#  Copyright (C) 2023-present Hydrogram <https://hydrogram.org>
#
#  This file is part of Hydrogram.
#
#  Hydrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Hydrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Hydrogram.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import logging
from functools import partial
from typing import TYPE_CHECKING, BinaryIO, Callable

import hydrogram
from hydrogram import enums, filters, raw, types, utils
from hydrogram.errors import MessageIdsEmpty, PeerIdInvalid
from hydrogram.parser import Parser
from hydrogram.parser import utils as parser_utils
from hydrogram.types.object import Object
from hydrogram.types.pyromod import ListenerTypes
from hydrogram.types.update import Update

if TYPE_CHECKING:
    from datetime import datetime
    from re import Match

log = logging.getLogger(__name__)


class Str(str):
    __slots__ = ("entities",)

    def __init__(self, *args):
        super().__init__()

        self.entities = None

    def init(self, entities):
        self.entities = entities

        return self

    @property
    def markdown(self):
        return Parser.unparse(self, self.entities, False)

    @property
    def html(self):
        return Parser.unparse(self, self.entities, True)

    def __getitem__(self, item):
        return parser_utils.remove_surrogates(parser_utils.add_surrogates(self)[item])


class Message(Object, Update):
    """A message.

    Parameters:
        id (``int``):
            Unique message identifier inside this chat.

        message_thread_id (``int``, *optional*):
            Unique identifier of a message thread to which the message belongs.
            for supergroups only

        from_user (:obj:`~hydrogram.types.User`, *optional*):
            Sender, empty for messages sent to channels.

        sender_chat (:obj:`~hydrogram.types.Chat`, *optional*):
            Sender of the message, sent on behalf of a chat.
            The channel itself for channel messages.
            The supergroup itself for messages from anonymous group administrators.
            The linked channel for messages automatically forwarded to the discussion group.

        date (:py:obj:`~datetime.datetime`, *optional*):
            Date the message was sent.

        chat (:obj:`~hydrogram.types.Chat`, *optional*):
            Conversation the message belongs to.

        topics (:obj:`~hydrogram.types.ForumTopic`, *optional*):
            Topic the message belongs to.

        forward_from (:obj:`~hydrogram.types.User`, *optional*):
            For forwarded messages, sender of the original message.

        forward_sender_name (``str``, *optional*):
            For messages forwarded from users who have hidden their accounts, name of the user.

        forward_from_chat (:obj:`~hydrogram.types.Chat`, *optional*):
            For messages forwarded from channels, information about the original channel. For messages forwarded from anonymous group administrators, information about the original supergroup.

        forward_from_message_id (``int``, *optional*):
            For messages forwarded from channels, identifier of the original message in the channel.

        forward_signature (``str``, *optional*):
            For messages forwarded from channels, signature of the post author if present.

        forward_date (:py:obj:`~datetime.datetime`, *optional*):
            For forwarded messages, date the original message was sent.

        is_topic_message (``bool``, *optional*):
            True, if the message is sent to a forum topic

        reply_to_message_id (``int``, *optional*):
            The id of the message which this message directly replied to.

        reply_to_top_message_id (``int``, *optional*):
            The id of the first message which started this message thread.

        reply_to_message (:obj:`~hydrogram.types.Message`, *optional*):
            For replies, the original message. Note that the Message object in this field will not contain
            further reply_to_message fields even if it itself is a reply.

        mentioned (``bool``, *optional*):
            The message contains a mention.

        empty (``bool``, *optional*):
            The message is empty.
            A message can be empty in case it was deleted or you tried to retrieve a message that doesn't exist yet.

        service (:obj:`~hydrogram.enums.MessageServiceType`, *optional*):
            The message is a service message.
            This field will contain the enumeration type of the service message.
            You can use ``service = getattr(message, message.service.value)`` to access the service message.

        media (:obj:`~hydrogram.enums.MessageMediaType`, *optional*):
            The message is a media message.
            This field will contain the enumeration type of the media message.
            You can use ``media = getattr(message, message.media.value)`` to access the media message.

        edit_date (:py:obj:`~datetime.datetime`, *optional*):
            Date the message was last edited.

        media_group_id (``str``, *optional*):
            The unique identifier of a media message group this message belongs to.

        author_signature (``str``, *optional*):
            Signature of the post author for messages in channels, or the custom title of an anonymous group
            administrator.

        has_protected_content (``bool``, *optional*):
            True, if the message can't be forwarded.

        has_media_spoiler (``bool``, *optional*):
            True, if the message media is covered by a spoiler animation.

        text (``str``, *optional*):
            For text messages, the actual UTF-8 text of the message, 0-4096 characters.
            If the message contains entities (bold, italic, ...) you can access *text.markdown* or
            *text.html* to get the marked up message text. In case there is no entity, the fields
            will contain the same text as *text*.

        entities (List of :obj:`~hydrogram.types.MessageEntity`, *optional*):
            For text messages, special entities like usernames, URLs, bot commands, etc. that appear in the text.

        caption_entities (List of :obj:`~hydrogram.types.MessageEntity`, *optional*):
            For messages with a caption, special entities like usernames, URLs, bot commands, etc. that appear
            in the caption.

        show_caption_above_media (``bool``, *optional*):
            Message's caption should be shown above the media.

        audio (:obj:`~hydrogram.types.Audio`, *optional*):
            Message is an audio file, information about the file.

        document (:obj:`~hydrogram.types.Document`, *optional*):
            Message is a general file, information about the file.

        photo (:obj:`~hydrogram.types.Photo`, *optional*):
            Message is a photo, information about the photo.

        sticker (:obj:`~hydrogram.types.Sticker`, *optional*):
            Message is a sticker, information about the sticker.

        animation (:obj:`~hydrogram.types.Animation`, *optional*):
            Message is an animation, information about the animation.

        game (:obj:`~hydrogram.types.Game`, *optional*):
            Message is a game, information about the game.

        video (:obj:`~hydrogram.types.Video`, *optional*):
            Message is a video, information about the video.

        voice (:obj:`~hydrogram.types.Voice`, *optional*):
            Message is a voice message, information about the file.

        video_note (:obj:`~hydrogram.types.VideoNote`, *optional*):
            Message is a video note, information about the video message.

        caption (``str``, *optional*):
            Caption for the audio, document, photo, video or voice, 0-1024 characters.
            If the message contains caption entities (bold, italic, ...) you can access *caption.markdown* or
            *caption.html* to get the marked up caption text. In case there is no caption entity, the fields
            will contain the same text as *caption*.

        contact (:obj:`~hydrogram.types.Contact`, *optional*):
            Message is a shared contact, information about the contact.

        location (:obj:`~hydrogram.types.Location`, *optional*):
            Message is a shared location, information about the location.

        venue (:obj:`~hydrogram.types.Venue`, *optional*):
            Message is a venue, information about the venue.

        web_page (:obj:`~hydrogram.types.WebPage`, *optional*):
            Message was sent with a webpage preview.

        poll (:obj:`~hydrogram.types.Poll`, *optional*):
            Message is a native poll, information about the poll.

        dice (:obj:`~hydrogram.types.Dice`, *optional*):
            A dice containing a value that is randomly generated by Telegram.

        new_chat_members (List of :obj:`~hydrogram.types.User`, *optional*):
            New members that were added to the group or supergroup and information about them
            (the bot itself may be one of these members).

        left_chat_member (:obj:`~hydrogram.types.User`, *optional*):
            A member was removed from the group, information about them (this member may be the bot itself).

        new_chat_title (``str``, *optional*):
            A chat title was changed to this value.

        new_chat_photo (:obj:`~hydrogram.types.Photo`, *optional*):
            A chat photo was change to this value.

        delete_chat_photo (``bool``, *optional*):
            Service message: the chat photo was deleted.

        group_chat_created (``bool``, *optional*):
            Service message: the group has been created.

        supergroup_chat_created (``bool``, *optional*):
            Service message: the supergroup has been created.
            This field can't be received in a message coming through updates, because bot can't be a member of a
            supergroup when it is created. It can only be found in reply_to_message if someone replies to a very
            first message in a directly created supergroup.

        channel_chat_created (``bool``, *optional*):
            Service message: the channel has been created.
            This field can't be received in a message coming through updates, because bot can't be a member of a
            channel when it is created. It can only be found in reply_to_message if someone replies to a very
            first message in a channel.

        migrate_to_chat_id (``int``, *optional*):
            The group has been migrated to a supergroup with the specified identifier.
            This number may be greater than 32 bits and some programming languages may have difficulty/silent defects
            in interpreting it. But it is smaller than 52 bits, so a signed 64 bit integer or double-precision float
            type are safe for storing this identifier.

        migrate_from_chat_id (``int``, *optional*):
            The supergroup has been migrated from a group with the specified identifier.
            This number may be greater than 32 bits and some programming languages may have difficulty/silent defects
            in interpreting it. But it is smaller than 52 bits, so a signed 64 bit integer or double-precision float
            type are safe for storing this identifier.

        pinned_message (:obj:`~hydrogram.types.Message`, *optional*):
            Specified message was pinned.
            Note that the Message object in this field will not contain further reply_to_message fields even if it
            is itself a reply.

        game_high_score (:obj:`~hydrogram.types.GameHighScore`, *optional*):
            The game score for a user.
            The reply_to_message field will contain the game Message.

        views (``int``, *optional*):
            Channel post views.

        forwards (``int``, *optional*):
            Channel post forwards.

        via_bot (:obj:`~hydrogram.types.User`):
            The information of the bot that generated the message from an inline query of a user.

        outgoing (``bool``, *optional*):
            Whether the message is incoming or outgoing.
            Messages received from other chats are incoming (*outgoing* is False).
            Messages sent from yourself to other chats are outgoing (*outgoing* is True).
            An exception is made for your own personal chat; messages sent there will be incoming.

        matches (List of regex Matches, *optional*):
            A list containing all `Match Objects <https://docs.python.org/3/library/re.html#match-objects>`_ that match
            the text of this message. Only applicable when using :obj:`Filters.regex <hydrogram.Filters.regex>`.

        command (List of ``str``, *optional*):
            A list containing the command and its arguments, if any.
            E.g.: "/start 1 2 3" would produce ["start", "1", "2", "3"].
            Only applicable when using :obj:`~hydrogram.filters.command`.

        forum_topic_created (:obj:`~hydrogram.types.ForumTopicCreated`, *optional*):
            Service message: forum topic created

        forum_topic_closed (:obj:`~hydrogram.types.ForumTopicClosed`, *optional*):
            Service message: forum topic closed

        forum_topic_reopened (:obj:`~hydrogram.types.ForumTopicReopened`, *optional*):
            Service message: forum topic reopened

        forum_topic_edited (:obj:`~hydrogram.types.ForumTopicEdited`, *optional*):
            Service message: forum topic edited

        general_topic_hidden (:obj:`~hydrogram.types.GeneralTopicHidden`, *optional*):
            Service message: forum general topic hidden

        general_topic_unhidden (:obj:`~hydrogram.types.GeneralTopicUnhidden`, *optional*):
            Service message: forum general topic unhidden

        video_chat_scheduled (:obj:`~hydrogram.types.VideoChatScheduled`, *optional*):
            Service message: voice chat scheduled.

        video_chat_started (:obj:`~hydrogram.types.VideoChatStarted`, *optional*):
            Service message: the voice chat started.

        video_chat_ended (:obj:`~hydrogram.types.VideoChatEnded`, *optional*):
            Service message: the voice chat has ended.

        video_chat_members_invited (:obj:`~hydrogram.types.VoiceChatParticipantsInvited`, *optional*):
            Service message: new members were invited to the voice chat.

        web_app_data (:obj:`~hydrogram.types.WebAppData`, *optional*):
            Service message: web app data sent to the bot.

        reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardRemove` | :obj:`~hydrogram.types.ForceReply`, *optional*):
            Additional interface options. An object for an inline keyboard, custom reply keyboard,
            instructions to remove reply keyboard or to force a reply from the user.

        reactions (List of :obj:`~hydrogram.types.Reaction`):
            List of the reactions to this message.

        link (``str``, *property*):
            Generate a link to this message, only for groups and channels.
    """

    # TODO: Add game missing field. Also invoice, successful_payment, connected_website

    def __init__(
        self,
        *,
        client: hydrogram.Client = None,
        id: int,
        message_thread_id: int | None = None,
        from_user: types.User = None,
        sender_chat: types.Chat = None,
        date: datetime | None = None,
        chat: types.Chat = None,
        topics: types.ForumTopic = None,
        forward_from: types.User = None,
        forward_sender_name: str | None = None,
        forward_from_chat: types.Chat = None,
        forward_from_message_id: int | None = None,
        forward_signature: str | None = None,
        forward_date: datetime | None = None,
        is_topic_message: bool | None = None,
        reply_to_message_id: int | None = None,
        reply_to_top_message_id: int | None = None,
        reply_to_message: Message = None,
        mentioned: bool | None = None,
        empty: bool | None = None,
        service: enums.MessageServiceType = None,
        scheduled: bool | None = None,
        from_scheduled: bool | None = None,
        media: enums.MessageMediaType = None,
        edit_date: datetime | None = None,
        media_group_id: str | None = None,
        author_signature: str | None = None,
        has_protected_content: bool | None = None,
        has_media_spoiler: bool | None = None,
        text: Str = None,
        entities: list[types.MessageEntity] | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        show_caption_above_media: bool | None = None,
        audio: types.Audio = None,
        document: types.Document = None,
        photo: types.Photo = None,
        sticker: types.Sticker = None,
        animation: types.Animation = None,
        game: types.Game = None,
        video: types.Video = None,
        voice: types.Voice = None,
        video_note: types.VideoNote = None,
        caption: Str = None,
        contact: types.Contact = None,
        location: types.Location = None,
        venue: types.Venue = None,
        web_page: types.WebPage = None,
        poll: types.Poll = None,
        dice: types.Dice = None,
        new_chat_members: list[types.User] | None = None,
        left_chat_member: types.User = None,
        new_chat_title: str | None = None,
        new_chat_photo: types.Photo = None,
        delete_chat_photo: bool | None = None,
        group_chat_created: bool | None = None,
        supergroup_chat_created: bool | None = None,
        channel_chat_created: bool | None = None,
        migrate_to_chat_id: int | None = None,
        migrate_from_chat_id: int | None = None,
        pinned_message: Message = None,
        game_high_score: int | None = None,
        views: int | None = None,
        forwards: int | None = None,
        via_bot: types.User = None,
        outgoing: bool | None = None,
        matches: list[Match] | None = None,
        command: list[str] | None = None,
        forum_topic_created: types.ForumTopicCreated = None,
        forum_topic_closed: types.ForumTopicClosed = None,
        forum_topic_reopened: types.ForumTopicReopened = None,
        forum_topic_edited: types.ForumTopicEdited = None,
        general_topic_hidden: types.GeneralTopicHidden = None,
        general_topic_unhidden: types.GeneralTopicUnhidden = None,
        video_chat_scheduled: types.VideoChatScheduled = None,
        video_chat_started: types.VideoChatStarted = None,
        video_chat_ended: types.VideoChatEnded = None,
        video_chat_members_invited: types.VideoChatMembersInvited = None,
        web_app_data: types.WebAppData = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply = None,
        reactions: list[types.Reaction] | None = None,
    ):
        super().__init__(client)

        self.id = id
        self.message_thread_id = message_thread_id
        self.from_user = from_user
        self.sender_chat = sender_chat
        self.date = date
        self.chat = chat
        self.topics = topics
        self.forward_from = forward_from
        self.forward_sender_name = forward_sender_name
        self.forward_from_chat = forward_from_chat
        self.forward_from_message_id = forward_from_message_id
        self.forward_signature = forward_signature
        self.forward_date = forward_date
        self.is_topic_message = is_topic_message
        self.reply_to_message_id = reply_to_message_id
        self.reply_to_top_message_id = reply_to_top_message_id
        self.reply_to_message = reply_to_message
        self.mentioned = mentioned
        self.empty = empty
        self.service = service
        self.scheduled = scheduled
        self.from_scheduled = from_scheduled
        self.media = media
        self.edit_date = edit_date
        self.media_group_id = media_group_id
        self.author_signature = author_signature
        self.has_protected_content = has_protected_content
        self.has_media_spoiler = has_media_spoiler
        self.text = text
        self.entities = entities
        self.caption_entities = caption_entities
        self.show_caption_above_media = show_caption_above_media
        self.audio = audio
        self.document = document
        self.photo = photo
        self.sticker = sticker
        self.animation = animation
        self.game = game
        self.video = video
        self.voice = voice
        self.video_note = video_note
        self.caption = caption
        self.contact = contact
        self.location = location
        self.venue = venue
        self.web_page = web_page
        self.poll = poll
        self.dice = dice
        self.new_chat_members = new_chat_members
        self.left_chat_member = left_chat_member
        self.new_chat_title = new_chat_title
        self.new_chat_photo = new_chat_photo
        self.delete_chat_photo = delete_chat_photo
        self.group_chat_created = group_chat_created
        self.supergroup_chat_created = supergroup_chat_created
        self.channel_chat_created = channel_chat_created
        self.migrate_to_chat_id = migrate_to_chat_id
        self.migrate_from_chat_id = migrate_from_chat_id
        self.pinned_message = pinned_message
        self.game_high_score = game_high_score
        self.views = views
        self.forwards = forwards
        self.via_bot = via_bot
        self.outgoing = outgoing
        self.matches = matches
        self.command = command
        self.reply_markup = reply_markup
        self.forum_topic_created = forum_topic_created
        self.forum_topic_closed = forum_topic_closed
        self.forum_topic_reopened = forum_topic_reopened
        self.forum_topic_edited = forum_topic_edited
        self.general_topic_hidden = general_topic_hidden
        self.general_topic_unhidden = general_topic_unhidden
        self.video_chat_scheduled = video_chat_scheduled
        self.video_chat_started = video_chat_started
        self.video_chat_ended = video_chat_ended
        self.video_chat_members_invited = video_chat_members_invited
        self.web_app_data = web_app_data
        self.reactions = reactions

    async def wait_for_click(
        self,
        from_user_id: int | str | list[int | str] | None = None,
        timeout: int | None = None,
        filters=None,
        alert: str | bool = True,
    ) -> types.CallbackQuery:
        """
        Waits for a callback query to be clicked on the message.

        Parameters:
            from_user_id (``Optional[Union[int, str], List[Union[int, str]]]``):
                The user ID(s) to wait for. If None, waits for any user.

            timeout (``Optional[int]``):
                The timeout in seconds. If None, waits forever.

            filters (``Optional[Filter]``):
                A filter to check if the callback query should be accepted.

            alert (``Union[str, bool]``):
                The alert to show when the button is clicked by users that are not allowed in from_user_id.
                If True, shows the default alert. If False, shows no alert.

        Returns:
            :obj:`~hydrogram.types.CallbackQuery`: The callback query that was clicked.
        """
        message_id = getattr(self, "id", getattr(self, "message_id", None))

        return await self._client.listen(
            listener_type=types.ListenerTypes.CALLBACK_QUERY,
            timeout=timeout,
            filters=filters,
            unallowed_click_alert=alert,
            chat_id=self.chat.id,
            user_id=from_user_id,
            message_id=message_id,
        )

    @staticmethod
    async def _parse(
        *,
        client: hydrogram.Client,
        message: raw.base.Message,
        users: dict,
        chats: dict,
        topics: dict | None = None,
        is_scheduled: bool = False,
        replies: int = 1,
    ):
        if isinstance(message, raw.types.MessageEmpty):
            return Message(id=message.id, empty=True, client=client)

        from_id = utils.get_raw_peer_id(message.from_id)
        peer_id = utils.get_raw_peer_id(message.peer_id)
        user_id = from_id or peer_id

        if (
            isinstance(message.from_id, raw.types.PeerUser)
            and isinstance(message.peer_id, raw.types.PeerUser)
            and (from_id not in users or peer_id not in users)
        ):
            try:
                r = await client.invoke(
                    raw.functions.users.GetUsers(
                        id=[
                            await client.resolve_peer(from_id),
                            await client.resolve_peer(peer_id),
                        ]
                    )
                )
            except PeerIdInvalid:
                pass
            else:
                users.update({i.id: i for i in r})

        if isinstance(message, raw.types.MessageService):
            message_thread_id = None
            action = message.action

            new_chat_members = None
            left_chat_member = None
            new_chat_title = None
            delete_chat_photo = None
            migrate_to_chat_id = None
            migrate_from_chat_id = None
            group_chat_created = None
            channel_chat_created = None
            new_chat_photo = None
            is_topic_message = None
            forum_topic_created = None
            forum_topic_closed = None
            forum_topic_reopened = None
            forum_topic_edited = None
            general_topic_hidden = None
            general_topic_unhidden = None
            video_chat_scheduled = None
            video_chat_started = None
            video_chat_ended = None
            video_chat_members_invited = None
            web_app_data = None

            service_type = None

            if isinstance(action, raw.types.MessageActionChatAddUser):
                new_chat_members = [types.User._parse(client, users[i]) for i in action.users]
                service_type = enums.MessageServiceType.NEW_CHAT_MEMBERS
            elif isinstance(action, raw.types.MessageActionChatJoinedByLink):
                new_chat_members = [
                    types.User._parse(client, users[utils.get_raw_peer_id(message.from_id)])
                ]
                service_type = enums.MessageServiceType.NEW_CHAT_MEMBERS
            elif isinstance(action, raw.types.MessageActionChatDeleteUser):
                left_chat_member = types.User._parse(client, users[action.user_id])
                service_type = enums.MessageServiceType.LEFT_CHAT_MEMBERS
            elif isinstance(action, raw.types.MessageActionChatEditTitle):
                new_chat_title = action.title
                service_type = enums.MessageServiceType.NEW_CHAT_TITLE
            elif isinstance(action, raw.types.MessageActionChatDeletePhoto):
                delete_chat_photo = True
                service_type = enums.MessageServiceType.DELETE_CHAT_PHOTO
            elif isinstance(action, raw.types.MessageActionChatMigrateTo):
                migrate_to_chat_id = action.channel_id
                service_type = enums.MessageServiceType.MIGRATE_TO_CHAT_ID
            elif isinstance(action, raw.types.MessageActionChannelMigrateFrom):
                migrate_from_chat_id = action.chat_id
                service_type = enums.MessageServiceType.MIGRATE_FROM_CHAT_ID
            elif isinstance(action, raw.types.MessageActionChatCreate):
                group_chat_created = True
                service_type = enums.MessageServiceType.GROUP_CHAT_CREATED
            elif isinstance(action, raw.types.MessageActionChannelCreate):
                channel_chat_created = True
                service_type = enums.MessageServiceType.CHANNEL_CHAT_CREATED
            elif isinstance(action, raw.types.MessageActionChatEditPhoto):
                new_chat_photo = types.Photo._parse(client, action.photo)
                service_type = enums.MessageServiceType.NEW_CHAT_PHOTO
            elif isinstance(action, raw.types.MessageActionTopicCreate):
                forum_topic_created = types.ForumTopicCreated._parse(action)
                service_type = enums.MessageServiceType.FORUM_TOPIC_CREATED
            elif isinstance(action, raw.types.MessageActionTopicEdit):
                if action.title:
                    forum_topic_edited = types.ForumTopicEdited._parse(action)
                    service_type = enums.MessageServiceType.FORUM_TOPIC_EDITED
                elif action.hidden:
                    general_topic_hidden = types.GeneralTopicHidden()
                    service_type = enums.MessageServiceType.GENERAL_TOPIC_HIDDEN
                elif action.closed:
                    forum_topic_closed = types.ForumTopicClosed()
                    service_type = enums.MessageServiceType.FORUM_TOPIC_CLOSED
                elif hasattr(action, "hidden"):
                    general_topic_unhidden = types.GeneralTopicUnhidden()
                    service_type = enums.MessageServiceType.GENERAL_TOPIC_UNHIDDEN
                else:
                    forum_topic_reopened = types.ForumTopicReopened()
                    service_type = enums.MessageServiceType.FORUM_TOPIC_REOPENED
            elif isinstance(action, raw.types.MessageActionGroupCallScheduled):
                video_chat_scheduled = types.VideoChatScheduled._parse(action)
                service_type = enums.MessageServiceType.VIDEO_CHAT_SCHEDULED
            elif isinstance(action, raw.types.MessageActionGroupCall):
                if action.duration:
                    video_chat_ended = types.VideoChatEnded._parse(action)
                    service_type = enums.MessageServiceType.VIDEO_CHAT_ENDED
                else:
                    video_chat_started = types.VideoChatStarted()
                    service_type = enums.MessageServiceType.VIDEO_CHAT_STARTED
            elif isinstance(action, raw.types.MessageActionInviteToGroupCall):
                video_chat_members_invited = types.VideoChatMembersInvited._parse(
                    client, action, users
                )
                service_type = enums.MessageServiceType.VIDEO_CHAT_MEMBERS_INVITED
            elif isinstance(action, raw.types.MessageActionWebViewDataSentMe):
                web_app_data = types.WebAppData._parse(action)
                service_type = enums.MessageServiceType.WEB_APP_DATA

            from_user = types.User._parse(client, users.get(user_id))
            sender_chat = (
                None
                if from_user
                else types.Chat._parse(client, message, users, chats, is_chat=False)
            )

            parsed_message = Message(
                id=message.id,
                message_thread_id=message_thread_id,
                date=utils.timestamp_to_datetime(message.date),
                chat=types.Chat._parse(client, message, users, chats, is_chat=True),
                topics=None,
                from_user=from_user,
                sender_chat=sender_chat,
                service=service_type,
                new_chat_members=new_chat_members,
                left_chat_member=left_chat_member,
                new_chat_title=new_chat_title,
                new_chat_photo=new_chat_photo,
                delete_chat_photo=delete_chat_photo,
                migrate_to_chat_id=utils.get_channel_id(migrate_to_chat_id)
                if migrate_to_chat_id
                else None,
                migrate_from_chat_id=-migrate_from_chat_id if migrate_from_chat_id else None,
                group_chat_created=group_chat_created,
                channel_chat_created=channel_chat_created,
                is_topic_message=is_topic_message,
                forum_topic_created=forum_topic_created,
                forum_topic_closed=forum_topic_closed,
                forum_topic_reopened=forum_topic_reopened,
                forum_topic_edited=forum_topic_edited,
                general_topic_hidden=general_topic_hidden,
                general_topic_unhidden=general_topic_unhidden,
                video_chat_scheduled=video_chat_scheduled,
                video_chat_started=video_chat_started,
                video_chat_ended=video_chat_ended,
                video_chat_members_invited=video_chat_members_invited,
                web_app_data=web_app_data,
                client=client,
                # TODO: supergroup_chat_created
            )

            if isinstance(action, raw.types.MessageActionPinMessage):
                try:
                    parsed_message.pinned_message = await client.get_messages(
                        parsed_message.chat.id,
                        reply_to_message_ids=message.id,
                        replies=0,
                    )

                    parsed_message.service = enums.MessageServiceType.PINNED_MESSAGE
                except MessageIdsEmpty:
                    pass

            if isinstance(action, raw.types.MessageActionGameScore):
                parsed_message.game_high_score = types.GameHighScore._parse_action(
                    client, message, users
                )

                if message.reply_to and replies:
                    try:
                        parsed_message.reply_to_message = await client.get_messages(
                            parsed_message.chat.id,
                            reply_to_message_ids=message.id,
                            replies=0,
                        )

                        parsed_message.service = enums.MessageServiceType.GAME_HIGH_SCORE
                    except MessageIdsEmpty:
                        pass

            client.message_cache[parsed_message.chat.id, parsed_message.id] = parsed_message

            if message.reply_to and message.reply_to.forum_topic:
                if message.reply_to.reply_to_top_id:
                    parsed_message.message_thread_id = message.reply_to.reply_to_top_id
                else:
                    parsed_message.message_thread_id = message.reply_to.reply_to_msg_id
                parsed_message.is_topic_message = True

            return parsed_message

        if isinstance(message, raw.types.Message):
            message_thread_id = None
            entities = [
                types.MessageEntity._parse(client, entity, users) for entity in message.entities
            ]
            entities = types.List(filter(lambda x: x is not None, entities))

            forward_from = None
            forward_sender_name = None
            forward_from_chat = None
            forward_from_message_id = None
            forward_signature = None
            forward_date = None
            is_topic_message = None

            if forward_header := message.fwd_from:
                forward_date = utils.timestamp_to_datetime(forward_header.date)

                if forward_header.from_id:
                    raw_peer_id = utils.get_raw_peer_id(forward_header.from_id)
                    peer_id = utils.get_peer_id(forward_header.from_id)

                    if peer_id > 0:
                        forward_from = types.User._parse(client, users[raw_peer_id])
                    else:
                        forward_from_chat = types.Chat._parse_channel_chat(
                            client, chats[raw_peer_id]
                        )
                        forward_from_message_id = forward_header.channel_post
                        forward_signature = forward_header.post_author
                elif forward_header.from_name:
                    forward_sender_name = forward_header.from_name

            photo = None
            location = None
            contact = None
            venue = None
            game = None
            audio = None
            voice = None
            animation = None
            video = None
            video_note = None
            sticker = None
            document = None
            web_page = None
            poll = None
            dice = None

            media = message.media
            media_type = None
            has_media_spoiler = None

            if media:
                if isinstance(media, raw.types.MessageMediaPhoto):
                    photo = types.Photo._parse(client, media.photo, media.ttl_seconds)
                    media_type = enums.MessageMediaType.PHOTO
                    has_media_spoiler = media.spoiler
                elif isinstance(media, raw.types.MessageMediaGeo):
                    location = types.Location._parse(client, media.geo)
                    media_type = enums.MessageMediaType.LOCATION
                elif isinstance(media, raw.types.MessageMediaContact):
                    contact = types.Contact._parse(client, media)
                    media_type = enums.MessageMediaType.CONTACT
                elif isinstance(media, raw.types.MessageMediaVenue):
                    venue = types.Venue._parse(client, media)
                    media_type = enums.MessageMediaType.VENUE
                elif isinstance(media, raw.types.MessageMediaGame):
                    game = types.Game._parse(client, message)
                    media_type = enums.MessageMediaType.GAME
                elif isinstance(media, raw.types.MessageMediaDocument):
                    doc = media.document

                    if isinstance(doc, raw.types.Document):
                        attributes = {type(i): i for i in doc.attributes}

                        file_name = getattr(
                            attributes.get(raw.types.DocumentAttributeFilename),
                            "file_name",
                            None,
                        )

                        if raw.types.DocumentAttributeAnimated in attributes:
                            video_attributes = attributes.get(raw.types.DocumentAttributeVideo)
                            animation = types.Animation._parse(
                                client, doc, video_attributes, file_name
                            )
                            media_type = enums.MessageMediaType.ANIMATION
                            has_media_spoiler = media.spoiler
                        elif raw.types.DocumentAttributeSticker in attributes:
                            sticker = await types.Sticker._parse(client, doc, attributes)
                            media_type = enums.MessageMediaType.STICKER
                        elif raw.types.DocumentAttributeVideo in attributes:
                            video_attributes = attributes[raw.types.DocumentAttributeVideo]

                            if video_attributes.round_message:
                                video_note = types.VideoNote._parse(client, doc, video_attributes)
                                media_type = enums.MessageMediaType.VIDEO_NOTE
                            else:
                                video = types.Video._parse(
                                    client,
                                    doc,
                                    video_attributes,
                                    file_name,
                                    media.ttl_seconds,
                                )
                                media_type = enums.MessageMediaType.VIDEO
                                has_media_spoiler = media.spoiler
                        elif raw.types.DocumentAttributeAudio in attributes:
                            audio_attributes = attributes[raw.types.DocumentAttributeAudio]

                            if audio_attributes.voice:
                                voice = types.Voice._parse(client, doc, audio_attributes)
                                media_type = enums.MessageMediaType.VOICE
                            else:
                                audio = types.Audio._parse(
                                    client, doc, audio_attributes, file_name
                                )
                                media_type = enums.MessageMediaType.AUDIO
                        else:
                            document = types.Document._parse(client, doc, file_name)
                            media_type = enums.MessageMediaType.DOCUMENT
                elif isinstance(media, raw.types.MessageMediaWebPage):
                    if isinstance(media.webpage, raw.types.WebPage):
                        web_page = types.WebPage._parse(client, media.webpage)
                        media_type = enums.MessageMediaType.WEB_PAGE
                    else:
                        media = None
                elif isinstance(media, raw.types.MessageMediaPoll):
                    poll = types.Poll._parse(client, media)
                    media_type = enums.MessageMediaType.POLL
                elif isinstance(media, raw.types.MessageMediaDice):
                    dice = types.Dice._parse(client, media)
                    media_type = enums.MessageMediaType.DICE
                else:
                    media = None

            reply_markup = message.reply_markup

            if reply_markup:
                if isinstance(reply_markup, raw.types.ReplyKeyboardForceReply):
                    reply_markup = types.ForceReply.read(reply_markup)
                elif isinstance(reply_markup, raw.types.ReplyKeyboardMarkup):
                    reply_markup = types.ReplyKeyboardMarkup.read(reply_markup)
                elif isinstance(reply_markup, raw.types.ReplyInlineMarkup):
                    reply_markup = types.InlineKeyboardMarkup.read(reply_markup)
                elif isinstance(reply_markup, raw.types.ReplyKeyboardHide):
                    reply_markup = types.ReplyKeyboardRemove.read(reply_markup)
                else:
                    reply_markup = None

            from_user = types.User._parse(client, users.get(user_id))
            sender_chat = (
                None
                if from_user
                else types.Chat._parse(client, message, users, chats, is_chat=False)
            )

            reactions = types.MessageReactions._parse(client, message.reactions)

            parsed_message = Message(
                id=message.id,
                message_thread_id=message_thread_id,
                date=utils.timestamp_to_datetime(message.date),
                chat=types.Chat._parse(client, message, users, chats, is_chat=True),
                topics=None,
                from_user=from_user,
                sender_chat=sender_chat,
                text=(
                    Str(message.message).init(entities) or None
                    if media is None or web_page is not None
                    else None
                ),
                caption=(
                    Str(message.message).init(entities) or None
                    if media is not None and web_page is None
                    else None
                ),
                entities=(entities or None if media is None or web_page is not None else None),
                caption_entities=(
                    entities or None if media is not None and web_page is None else None
                ),
                author_signature=message.post_author,
                has_protected_content=message.noforwards,
                has_media_spoiler=has_media_spoiler,
                forward_from=forward_from,
                forward_sender_name=forward_sender_name,
                forward_from_chat=forward_from_chat,
                forward_from_message_id=forward_from_message_id,
                forward_signature=forward_signature,
                forward_date=forward_date,
                is_topic_message=is_topic_message,
                mentioned=message.mentioned,
                scheduled=is_scheduled,
                from_scheduled=message.from_scheduled,
                media=media_type,
                edit_date=utils.timestamp_to_datetime(message.edit_date),
                media_group_id=message.grouped_id,
                photo=photo,
                location=location,
                contact=contact,
                venue=venue,
                audio=audio,
                voice=voice,
                animation=animation,
                game=game,
                video=video,
                video_note=video_note,
                sticker=sticker,
                document=document,
                web_page=web_page,
                poll=poll,
                dice=dice,
                views=message.views,
                forwards=message.forwards,
                via_bot=types.User._parse(client, users.get(message.via_bot_id)),
                outgoing=message.out,
                reply_markup=reply_markup,
                reactions=reactions,
                client=client,
            )

            if message.reply_to:
                if isinstance(message.reply_to, raw.types.MessageReplyHeader):
                    if message.reply_to.forum_topic:
                        if message.reply_to.reply_to_top_id:
                            thread_id = message.reply_to.reply_to_top_id
                            parsed_message.reply_to_message_id = message.reply_to.reply_to_msg_id
                        else:
                            thread_id = message.reply_to.reply_to_msg_id
                        parsed_message.message_thread_id = thread_id
                        parsed_message.is_topic_message = True
                        if topics:
                            parsed_message.topics = types.ForumTopic._parse(topics[thread_id])
                        else:
                            try:
                                msg = await client.get_messages(parsed_message.chat.id, message.id)
                                if getattr(msg, "topics"):
                                    parsed_message.topics = msg.topics
                            except Exception:
                                pass
                    else:
                        parsed_message.reply_to_message_id = message.reply_to.reply_to_msg_id
                        parsed_message.reply_to_top_message_id = message.reply_to.reply_to_top_id
                if isinstance(message.reply_to, raw.types.MessageReplyStoryHeader):
                    parsed_message.reply_to_message_id = message.reply_to.story_id

                if replies:
                    try:
                        key = (
                            parsed_message.chat.id,
                            parsed_message.reply_to_message_id,
                        )
                        reply_to_message = client.message_cache[key] or await client.get_messages(
                            parsed_message.chat.id,
                            reply_to_message_ids=message.id,
                            replies=replies - 1,
                        )
                        if reply_to_message and not reply_to_message.forum_topic_created:
                            parsed_message.reply_to_message = reply_to_message
                    except MessageIdsEmpty:
                        pass

            if not parsed_message.poll:  # Do not cache poll messages
                client.message_cache[parsed_message.chat.id, parsed_message.id] = parsed_message

            return parsed_message
        return None

    def listen(
        self,
        filters: filters.Filter | None = None,
        listener_type: ListenerTypes = ListenerTypes.MESSAGE,
        timeout: int | None = None,
        unallowed_click_alert: bool = True,
        user_id: int | str | list[int | str] | None = None,
        message_id: int | list[int] | None = None,
        inline_message_id: str | list[str] | None = None,
    ):
        """
        Bound method *listen* of :obj:`~hydrogram.types.Chat`.

        Use as a shortcut for:

        .. code-block:: python

            await client.listen(chat_id=chat_id)

        Example:
            .. code-block:: python

                await chat.listen()

        Parameters:
            filters (``Optional[filters.Filter]``):
                A filter to check if the listener should be fulfilled.

            listener_type (``ListenerTypes``):
                The type of listener to create. Defaults to :attr:`hydrogram.types.ListenerTypes.MESSAGE`.

            timeout (``Optional[int]``):
                The maximum amount of time to wait for the listener to be fulfilled. Defaults to ``None``.

            unallowed_click_alert (``bool``):
                Whether to alert the user if they click on a button that is not intended for them. Defaults to ``True``.

            user_id (``Optional[Union[int, str], List[Union[int, str]]]``):
                The user ID(s) to listen for. Defaults to ``None``.

            message_id (``Optional[Union[int, List[int]]]``):
                The message ID(s) to listen for. Defaults to ``None``.

            inline_message_id (``Optional[Union[str, List[str]]]``):
                The inline message ID(s) to listen for. Defaults to ``None``.

        Returns:
            Union[:obj:`~hydrogram.types.Message`, :obj:`~hydrogram.types.CallbackQuery`]: The Message or CallbackQuery
        """
        return self._client.listen(
            chat_id=self.chat.id if self.chat else None,
            filters=filters,
            listener_type=listener_type,
            timeout=timeout,
            unallowed_click_alert=unallowed_click_alert,
            user_id=user_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
        )

    def ask(
        self,
        text: str,
        filters: filters.Filter | None = None,
        listener_type: ListenerTypes = ListenerTypes.MESSAGE,
        timeout: int | None = None,
        unallowed_click_alert: bool = True,
        user_id: int | str | list[int | str] | None = None,
        message_id: int | list[int] | None = None,
        inline_message_id: str | list[str] | None = None,
        *args,
        **kwargs,
    ):
        """
        Bound method *ask* of :obj:`~hydrogram.types.Chat`.

        Use as a shortcut for:

        .. code-block:: python

            await client.ask(chat_id=chat_id, text=text)

        Example:

            .. code-block:: python

                await chat.ask("What's your name?")

        Parameters:
            text (``str``):
                The text to send.

            filters (``Optional[filters.Filter]``):
                Same as :meth:`hydrogram.Client.listen`.

            listener_type (``ListenerTypes``):
                Same as :meth:`hydrogram.Client.listen`.

            timeout (``Optional[int]``):
                Same as :meth:`hydrogram.Client.listen`.

            unallowed_click_alert (``bool``):
                Same as :meth:`hydrogram.Client.listen`.

            user_id (``Optional[Union[int, str], List[Union[int, str]]]``):
                The user ID(s) to listen for. Defaults to ``None``.

            message_id (``Optional[Union[int, List[int]]]``):
                The message ID(s) to listen for. Defaults to ``None``.

            inline_message_id (``Optional[Union[str, List[str]]]``):
                The inline message ID(s) to listen for. Defaults to ``None``.

            args (``Any``):
                Additional arguments to pass to :meth:`hydrogram.Client.send_message`.

            kwargs (``Any``):
                Additional keyword arguments to pass to :meth:`hydrogram.Client.send_message`.

        Returns:
            Union[:obj:`~hydrogram.types.Message`, :obj:`~hydrogram.types.CallbackQuery`]: The Message or CallbackQuery
        """
        return self._client.ask(
            chat_id=self.chat.id if self.chat else None,
            text=text,
            filters=filters,
            listener_type=listener_type,
            timeout=timeout,
            unallowed_click_alert=unallowed_click_alert,
            user_id=user_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
            *args,
            **kwargs,
        )

    def stop_listening(
        self,
        listener_type: ListenerTypes = ListenerTypes.MESSAGE,
        user_id: int | str | list[int | str] | None = None,
        message_id: int | list[int] | None = None,
        inline_message_id: str | list[str] | None = None,
    ):
        """
        Bound method *stop_listening* of :obj:`~hydrogram.types.Chat`.

        Use as a shortcut for:

        .. code-block:: python

            await client.stop_listening(chat_id=chat_id)

        Example:
            .. code-block:: python

                await chat.stop_listening()

        Parameters:
            listener_type (``ListenerTypes``):
                The type of listener to stop listening for. Defaults to :attr:`hydrogram.types.ListenerTypes.MESSAGE`.

            user_id (``Optional[Union[int, str], List[Union[int, str]]]``):
                The user ID(s) to stop listening for. Defaults to ``None``.

            message_id (``Optional[Union[int, List[int]]]``):
                The message ID(s) to stop listening for. Defaults to ``None``.

            inline_message_id (``Optional[Union[str, List[str]]]``):
                The inline message ID(s) to stop listening for. Defaults to ``None``.

        Returns:
            ``bool``: The return value of :meth:`hydrogram.Client.stop_listening`.
        """
        return self._client.stop_listening(
            chat_id=self.chat.id if self.chat else None,
            listener_type=listener_type,
            user_id=user_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
        )

    @property
    def link(self) -> str:
        if (
            self.chat.type
            in {enums.ChatType.GROUP, enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL}
            and self.chat.username
        ):
            return f"https://t.me/{self.chat.username}/{self.id}"
        return f"https://t.me/c/{utils.get_channel_id(self.chat.id)}/{self.id}"

    async def get_media_group(self) -> list[types.Message]:
        """Bound method *get_media_group* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.get_media_group(chat_id=message.chat.id, message_id=message.id)

        Example:
            .. code-block:: python

                await message.get_media_group()

        Returns:
            List of :obj:`~hydrogram.types.Message`: On success, a list of messages of the media group is returned.

        Raises:
            ValueError: In case the passed message id doesn't belong to a media group.
        """

        return await self._client.get_media_group(chat_id=self.chat.id, message_id=self.id)

    async def reply_text(
        self,
        text: str,
        quote: bool | None = None,
        parse_mode: enums.ParseMode | None = None,
        entities: list[types.MessageEntity] | None = None,
        disable_web_page_preview: bool | None = None,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        reply_markup=None,
    ) -> Message:
        """Bound method *reply_text* of :obj:`~hydrogram.types.Message`.

        An alias exists as *reply*.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_message(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                text="hello",
                reply_to_message_id=message.id,
            )

        Example:
            .. code-block:: python

                await message.reply_text("hello", quote=True)

        Parameters:
            text (``str``):
                Text of the message to be sent.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            parse_mode (:obj:`~hydrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            entities (List of :obj:`~hydrogram.types.MessageEntity`):
                List of special entities that appear in message text, which can be specified instead of *parse_mode*.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardRemove` | :obj:`~hydrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent Message is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != enums.ChatType.PRIVATE

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.id

        return await self._client.send_message(
            chat_id=self.chat.id,
            message_thread_id=self.message_thread_id,
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            schedule_date=schedule_date,
            protect_content=protect_content,
            reply_markup=reply_markup,
        )

    reply = reply_text

    async def reply_animation(
        self,
        animation: str | BinaryIO,
        quote: bool | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        has_spoiler: bool | None = None,
        duration: int = 0,
        width: int = 0,
        height: int = 0,
        thumb: str | BinaryIO | None = None,
        disable_notification: bool | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply = None,
        reply_to_message_id: int | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message:
        """Bound method *reply_animation* :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_animation(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                animation=animation,
            )

        Example:
            .. code-block:: python

                await message.reply_animation(animation)

        Parameters:
            animation (``str``):
                Animation to send.
                Pass a file_id as string to send an animation that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get an animation from the Internet, or
                pass a file path as string to upload a new animation that exists on your local machine.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            caption (``str``, *optional*):
                Animation caption, 0-1024 characters.

            parse_mode (:obj:`~hydrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~hydrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            has_spoiler (``bool``, *optional*):
                Pass True if the animation needs to be covered with a spoiler animation.

            duration (``int``, *optional*):
                Duration of sent animation in seconds.

            width (``int``, *optional*):
                Animation width.

            height (``int``, *optional*):
                Animation height.

            thumb (``str | BinaryIO``, *optional*):
                Thumbnail of the animation file sent.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardRemove` | :obj:`~hydrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~hydrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~hydrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != enums.ChatType.PRIVATE

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.id

        return await self._client.send_animation(
            chat_id=self.chat.id,
            message_thread_id=self.message_thread_id,
            animation=animation,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            has_spoiler=has_spoiler,
            duration=duration,
            width=width,
            height=height,
            thumb=thumb,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def reply_audio(
        self,
        audio: str | BinaryIO,
        quote: bool | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        duration: int = 0,
        performer: str | None = None,
        title: str | None = None,
        thumb: str | BinaryIO | None = None,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message:
        """Bound method *reply_audio* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_audio(
                chat_id=message.chat.id, message_thread_id=message.message_thread_id, audio=audio
            )

        Example:
            .. code-block:: python

                await message.reply_audio(audio)

        Parameters:
            audio (``str``):
                Audio file to send.
                Pass a file_id as string to send an audio file that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get an audio file from the Internet, or
                pass a file path as string to upload a new audio file that exists on your local machine.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            caption (``str``, *optional*):
                Audio caption, 0-1024 characters.

            parse_mode (:obj:`~hydrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~hydrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            duration (``int``, *optional*):
                Duration of the audio in seconds.

            performer (``str``, *optional*):
                Performer.

            title (``str``, *optional*):
                Track name.

            thumb (``str | BinaryIO``, *optional*):
                Thumbnail of the music file album cover.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardRemove` | :obj:`~hydrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~hydrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~hydrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != enums.ChatType.PRIVATE

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.id

        return await self._client.send_audio(
            chat_id=self.chat.id,
            message_thread_id=self.message_thread_id,
            audio=audio,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            duration=duration,
            performer=performer,
            title=title,
            thumb=thumb,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def reply_cached_media(
        self,
        file_id: str,
        quote: bool | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply = None,
    ) -> Message:
        """Bound method *reply_cached_media* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_cached_media(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                file_id=file_id,
            )

        Example:
            .. code-block:: python

                await message.reply_cached_media(file_id)

        Parameters:
            file_id (``str``):
                Media to send.
                Pass a file_id as string to send a media that exists on the Telegram servers.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            caption (``bool``, *optional*):
                Media caption, 0-1024 characters.

            parse_mode (:obj:`~hydrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~hydrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardRemove` | :obj:`~hydrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent :obj:`~hydrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != enums.ChatType.PRIVATE

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.id

        return await self._client.send_cached_media(
            chat_id=self.chat.id,
            message_thread_id=self.message_thread_id,
            file_id=file_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
        )

    async def reply_chat_action(self, action: enums.ChatAction) -> bool:
        """Bound method *reply_chat_action* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            from hydrogram import enums

            await client.send_chat_action(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                action=enums.ChatAction.TYPING,
            )

        Example:
            .. code-block:: python

                from hydrogram import enums

                await message.reply_chat_action(enums.ChatAction.TYPING)

        Parameters:
            action (:obj:`~hydrogram.enums.ChatAction`):
                Type of action to broadcast.

        Returns:
            ``bool``: On success, True is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
            ValueError: In case the provided string is not a valid chat action.
        """
        return await self._client.send_chat_action(
            chat_id=self.chat.id, message_thread_id=self.message_thread_id, action=action
        )

    async def reply_contact(
        self,
        phone_number: str,
        first_name: str,
        quote: bool | None = None,
        last_name: str = "",
        vcard: str = "",
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply = None,
    ) -> Message:
        """Bound method *reply_contact* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_contact(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                phone_number=phone_number,
                first_name=first_name,
            )

        Example:
            .. code-block:: python

                await message.reply_contact("+1-123-456-7890", "Name")

        Parameters:
            phone_number (``str``):
                Contact's phone number.

            first_name (``str``):
                Contact's first name.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            last_name (``str``, *optional*):
                Contact's last name.

            vcard (``str``, *optional*):
                Additional data about the contact in the form of a vCard, 0-2048 bytes

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardRemove` | :obj:`~hydrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent :obj:`~hydrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != enums.ChatType.PRIVATE

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.id

        return await self._client.send_contact(
            chat_id=self.chat.id,
            message_thread_id=self.message_thread_id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            vcard=vcard,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
        )

    async def reply_document(
        self,
        document: str | BinaryIO,
        quote: bool | None = None,
        thumb: str | BinaryIO | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        file_name: str | None = None,
        force_document: bool | None = None,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        schedule_date: datetime | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message:
        """Bound method *reply_document* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_document(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                document=document,
            )

        Example:
            .. code-block:: python

                await message.reply_document(document)

        Parameters:
            document (``str``):
                File to send.
                Pass a file_id as string to send a file that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a file from the Internet, or
                pass a file path as string to upload a new file that exists on your local machine.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            thumb (``str | BinaryIO``, *optional*):
                Thumbnail of the file sent.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            caption (``str``, *optional*):
                Document caption, 0-1024 characters.

            parse_mode (:obj:`~hydrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~hydrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            file_name (``str``, *optional*):
                File name of the document sent.
                Defaults to file's path basename.

            force_document (``bool``, *optional*):
                Pass True to force sending files as document. Useful for video files that need to be sent as
                document messages instead of video messages.
                Defaults to False.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardRemove` | :obj:`~hydrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~hydrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~hydrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != enums.ChatType.PRIVATE

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.id

        return await self._client.send_document(
            chat_id=self.chat.id,
            message_thread_id=self.message_thread_id,
            document=document,
            thumb=thumb,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            file_name=file_name,
            force_document=force_document,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            schedule_date=schedule_date,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def reply_game(
        self,
        game_short_name: str,
        quote: bool | None = None,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply = None,
    ) -> Message:
        """Bound method *reply_game* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_game(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                game_short_name="lumberjack",
            )

        Example:
            .. code-block:: python

                await message.reply_game("lumberjack")

        Parameters:
            game_short_name (``str``):
                Short name of the game, serves as the unique identifier for the game. Set up your games via Botfather.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup`, *optional*):
                An object for an inline keyboard. If empty, one ‘Play game_title’ button will be shown automatically.
                If not empty, the first button must launch the game.

        Returns:
            On success, the sent :obj:`~hydrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != enums.ChatType.PRIVATE

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.id

        return await self._client.send_game(
            chat_id=self.chat.id,
            message_thread_id=self.message_thread_id,
            game_short_name=game_short_name,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
        )

    async def reply_inline_bot_result(
        self,
        query_id: int,
        result_id: str,
        quote: bool | None = None,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
    ) -> Message:
        """Bound method *reply_inline_bot_result* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_inline_bot_result(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                query_id=query_id,
                result_id=result_id,
            )

        Example:
            .. code-block:: python

                await message.reply_inline_bot_result(query_id, result_id)

        Parameters:
            query_id (``int``):
                Unique identifier for the answered query.

            result_id (``str``):
                Unique identifier for the result that was chosen.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

        Returns:
            On success, the sent Message is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != enums.ChatType.PRIVATE

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.id

        return await self._client.send_inline_bot_result(
            chat_id=self.chat.id,
            message_thread_id=self.message_thread_id,
            query_id=query_id,
            result_id=result_id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
        )

    async def reply_location(
        self,
        latitude: float,
        longitude: float,
        quote: bool | None = None,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply = None,
    ) -> Message:
        """Bound method *reply_location* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_location(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                latitude=latitude,
                longitude=longitude,
            )

        Example:
            .. code-block:: python

                await message.reply_location(latitude, longitude)

        Parameters:
            latitude (``float``):
                Latitude of the location.

            longitude (``float``):
                Longitude of the location.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardRemove` | :obj:`~hydrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent :obj:`~hydrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != enums.ChatType.PRIVATE

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.id

        return await self._client.send_location(
            chat_id=self.chat.id,
            message_thread_id=self.message_thread_id,
            latitude=latitude,
            longitude=longitude,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
        )

    async def reply_media_group(
        self,
        media: list[types.InputMediaPhoto | types.InputMediaVideo],
        quote: bool | None = None,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
    ) -> list[types.Message]:
        """Bound method *reply_media_group* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_media_group(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                media=list_of_media,
            )

        Example:
            .. code-block:: python

                await message.reply_media_group(list_of_media)

        Parameters:
            media (``list``):
                A list containing either :obj:`~hydrogram.types.InputMediaPhoto` or
                :obj:`~hydrogram.types.InputMediaVideo` objects
                describing photos and videos to be sent, must include 2–10 items.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

        Returns:
            On success, a :obj:`~hydrogram.types.Messages` object is returned containing all the
            single messages sent.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != enums.ChatType.PRIVATE

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.id

        return await self._client.send_media_group(
            chat_id=self.chat.id,
            message_thread_id=self.message_thread_id,
            media=media,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
        )

    async def reply_photo(
        self,
        photo: str | BinaryIO,
        quote: bool | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        has_spoiler: bool | None = None,
        ttl_seconds: int | None = None,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message:
        """Bound method *reply_photo* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_photo(
                chat_id=message.chat.id, message_thread_id=message.message_thread_id, photo=photo
            )

        Example:
            .. code-block:: python

                await message.reply_photo(photo)

        Parameters:
            photo (``str``):
                Photo to send.
                Pass a file_id as string to send a photo that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a photo from the Internet, or
                pass a file path as string to upload a new photo that exists on your local machine.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            caption (``str``, *optional*):
                Photo caption, 0-1024 characters.

            parse_mode (:obj:`~hydrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~hydrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            has_spoiler (``bool``, *optional*):
                Pass True if the photo needs to be covered with a spoiler animation.

            ttl_seconds (``int``, *optional*):
                Self-Destruct Timer.
                If you set a timer, the photo will self-destruct in *ttl_seconds*
                seconds after it was viewed.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardRemove` | :obj:`~hydrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~hydrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~hydrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != enums.ChatType.PRIVATE

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.id

        return await self._client.send_photo(
            chat_id=self.chat.id,
            message_thread_id=self.message_thread_id,
            photo=photo,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            has_spoiler=has_spoiler,
            ttl_seconds=ttl_seconds,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def reply_poll(
        self,
        question: str,
        options: list[types.InputPollOption],
        question_parse_mode: enums.ParseMode = None,
        question_entities: list[types.MessageEntity] | None = None,
        is_anonymous: bool = True,
        type: enums.PollType = enums.PollType.REGULAR,
        allows_multiple_answers: bool | None = None,
        correct_option_id: int | None = None,
        explanation: str | None = None,
        explanation_parse_mode: enums.ParseMode = None,
        explanation_entities: list[types.MessageEntity] | None = None,
        open_period: int | None = None,
        close_date: datetime | None = None,
        is_closed: bool | None = None,
        quote: bool | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_to_message_id: int | None = None,
        schedule_date: datetime | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply = None,
    ) -> Message:
        """Bound method *reply_poll* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_poll(
                chat_id=message.chat.id,
                question="This is a poll",
                options=[
                    InputPollOption(text="A"),
                    InputPollOption(text="B"),
                    InputPollOption(text="C"),
                ],
            )

        Example:
            .. code-block:: python

                await message.reply_poll(
                    question="This is a poll",
                    options=[
                        InputPollOption(text="A"),
                        InputPollOption(text="B"),
                        InputPollOption(text="C"),
                    ],
                )

        Parameters:
            question (``str``):
                Poll question, 1-255 characters.

            options (List of :obj:`~hydrogram.types.InputPollOption`):
                List of answer options, 2-10 answer options,  1-100 characters for each option.

            question_parse_mode (:obj:`~hydrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            question_entities (List of :obj:`~hydrogram.types.MessageEntity`):
                List of special entities that appear in the poll question, which can be specified instead of *question_parse_mode*.

            is_anonymous (``bool``, *optional*):
                True, if the poll needs to be anonymous.
                Defaults to True.

            type (:obj`~hydrogram.enums.PollType`, *optional*):
                Poll type, :obj:`~hydrogram.enums.PollType.QUIZ` or :obj:`~hydrogram.enums.PollType.REGULAR`.
                Defaults to :obj:`~hydrogram.enums.PollType.REGULAR`.

            allows_multiple_answers (``bool``, *optional*):
                True, if the poll allows multiple answers, ignored for polls in quiz mode.
                Defaults to False.

            correct_option_id (``int``, *optional*):
                0-based identifier of the correct answer option, required for polls in quiz mode.

            explanation (``str``, *optional*):
                Text that is shown when a user chooses an incorrect answer or taps on the lamp icon in a quiz-style
                poll, 0-200 characters with at most 2 line feeds after entities parsing.

            explanation_parse_mode (:obj:`~hydrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            explanation_entities (List of :obj:`~hydrogram.types.MessageEntity`):
                List of special entities that appear in the poll explanation, which can be specified instead of
                *parse_mode*.

            open_period (``int``, *optional*):
                Amount of time in seconds the poll will be active after creation, 5-600.
                Can't be used together with *close_date*.

            close_date (:py:obj:`~datetime.datetime`, *optional*):
                Point in time when the poll will be automatically closed.
                Must be at least 5 and no more than 600 seconds in the future.
                Can't be used together with *open_period*.

            is_closed (``bool``, *optional*):
                Pass True, if the poll needs to be immediately closed.
                This can be useful for poll preview.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardRemove` | :obj:`~hydrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent :obj:`~hydrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != enums.ChatType.PRIVATE

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.id

        return await self._client.send_poll(
            chat_id=self.chat.id,
            message_thread_id=self.message_thread_id,
            question=question,
            options=options,
            question_parse_mode=question_parse_mode,
            question_entities=question_entities,
            is_anonymous=is_anonymous,
            type=type,
            allows_multiple_answers=allows_multiple_answers,
            correct_option_id=correct_option_id,
            explanation=explanation,
            explanation_parse_mode=explanation_parse_mode,
            explanation_entities=explanation_entities,
            open_period=open_period,
            close_date=close_date,
            is_closed=is_closed,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            schedule_date=schedule_date,
            reply_markup=reply_markup,
        )

    async def reply_sticker(
        self,
        sticker: str | BinaryIO,
        quote: bool | None = None,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message:
        """Bound method *reply_sticker* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_sticker(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                sticker=sticker,
            )

        Example:
            .. code-block:: python

                await message.reply_sticker(sticker)

        Parameters:
            sticker (``str``):
                Sticker to send.
                Pass a file_id as string to send a sticker that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a .webp sticker file from the Internet, or
                pass a file path as string to upload a new sticker that exists on your local machine.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardRemove` | :obj:`~hydrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~hydrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~hydrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != enums.ChatType.PRIVATE

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.id

        return await self._client.send_sticker(
            chat_id=self.chat.id,
            message_thread_id=self.message_thread_id,
            sticker=sticker,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def reply_venue(
        self,
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        quote: bool | None = None,
        foursquare_id: str = "",
        foursquare_type: str = "",
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply = None,
    ) -> Message:
        """Bound method *reply_venue* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_venue(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                latitude=latitude,
                longitude=longitude,
                title="Venue title",
                address="Venue address",
            )

        Example:
            .. code-block:: python

                await message.reply_venue(latitude, longitude, "Venue title", "Venue address")

        Parameters:
            latitude (``float``):
                Latitude of the venue.

            longitude (``float``):
                Longitude of the venue.

            title (``str``):
                Name of the venue.

            address (``str``):
                Address of the venue.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            foursquare_id (``str``, *optional*):
                Foursquare identifier of the venue.

            foursquare_type (``str``, *optional*):
                Foursquare type of the venue, if known.
                (For example, "arts_entertainment/default", "arts_entertainment/aquarium" or "food/icecream".)

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardRemove` | :obj:`~hydrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent :obj:`~hydrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != enums.ChatType.PRIVATE

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.id

        return await self._client.send_venue(
            chat_id=self.chat.id,
            message_thread_id=self.message_thread_id,
            latitude=latitude,
            longitude=longitude,
            title=title,
            address=address,
            foursquare_id=foursquare_id,
            foursquare_type=foursquare_type,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
        )

    async def reply_video(
        self,
        video: str | BinaryIO,
        quote: bool | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        has_spoiler: bool | None = None,
        ttl_seconds: int | None = None,
        duration: int = 0,
        width: int = 0,
        height: int = 0,
        thumb: str | BinaryIO | None = None,
        supports_streaming: bool = True,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        no_sound: bool | None = False,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message:
        """Bound method *reply_video* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_video(
                chat_id=message.chat.id, message_thread_id=message.message_thread_id, video=video
            )

        Example:
            .. code-block:: python

                await message.reply_video(video)

        Parameters:
            video (``str``):
                Video to send.
                Pass a file_id as string to send a video that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a video from the Internet, or
                pass a file path as string to upload a new video that exists on your local machine.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            caption (``str``, *optional*):
                Video caption, 0-1024 characters.

            parse_mode (:obj:`~hydrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~hydrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            has_spoiler (``bool``, *optional*):
                Pass True if the video needs to be covered with a spoiler animation.

            ttl_seconds (``int``, *optional*):
                Self-Destruct Timer.
                If you set a timer, the video will self-destruct in *ttl_seconds*
                seconds after it was viewed.

            duration (``int``, *optional*):
                Duration of sent video in seconds.

            width (``int``, *optional*):
                Video width.

            height (``int``, *optional*):
                Video height.

            thumb (``str | BinaryIO``, *optional*):
                Thumbnail of the video sent.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            supports_streaming (``bool``, *optional*):
                Pass True, if the uploaded video is suitable for streaming.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            no_sound (``bool``, *optional*):
                Pass True if the video you are uploading is a video message with no sound.
                Does not work for external links.

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardRemove` | :obj:`~hydrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~hydrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~hydrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != enums.ChatType.PRIVATE

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.id

        return await self._client.send_video(
            chat_id=self.chat.id,
            message_thread_id=self.message_thread_id,
            video=video,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            has_spoiler=has_spoiler,
            ttl_seconds=ttl_seconds,
            duration=duration,
            width=width,
            height=height,
            thumb=thumb,
            supports_streaming=supports_streaming,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            no_sound=no_sound,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def reply_video_note(
        self,
        video_note: str | BinaryIO,
        quote: bool | None = None,
        duration: int = 0,
        length: int = 1,
        thumb: str | BinaryIO | None = None,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message:
        """Bound method *reply_video_note* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_video_note(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                video_note=video_note,
            )

        Example:
            .. code-block:: python

                await message.reply_video_note(video_note)

        Parameters:
            video_note (``str``):
                Video note to send.
                Pass a file_id as string to send a video note that exists on the Telegram servers, or
                pass a file path as string to upload a new video note that exists on your local machine.
                Sending video notes by a URL is currently unsupported.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            duration (``int``, *optional*):
                Duration of sent video in seconds.

            length (``int``, *optional*):
                Video width and height.

            thumb (``str | BinaryIO``, *optional*):
                Thumbnail of the video sent.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardRemove` | :obj:`~hydrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~hydrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~hydrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != enums.ChatType.PRIVATE

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.id

        return await self._client.send_video_note(
            chat_id=self.chat.id,
            message_thread_id=self.message_thread_id,
            video_note=video_note,
            duration=duration,
            length=length,
            thumb=thumb,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def reply_voice(
        self,
        voice: str | BinaryIO,
        quote: bool | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        duration: int = 0,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message:
        """Bound method *reply_voice* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_voice(
                chat_id=message.chat.id, message_thread_id=message.message_thread_id, voice=voice
            )

        Example:
            .. code-block:: python

                await message.reply_voice(voice)

        Parameters:
            voice (``str``):
                Audio file to send.
                Pass a file_id as string to send an audio that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get an audio from the Internet, or
                pass a file path as string to upload a new audio that exists on your local machine.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            caption (``str``, *optional*):
                Voice message caption, 0-1024 characters.

            parse_mode (:obj:`~hydrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~hydrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            duration (``int``, *optional*):
                Duration of the voice message in seconds.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardRemove` | :obj:`~hydrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~hydrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~hydrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != enums.ChatType.PRIVATE

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.id

        return await self._client.send_voice(
            chat_id=self.chat.id,
            message_thread_id=self.message_thread_id,
            voice=voice,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            duration=duration,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def edit_text(
        self,
        text: str,
        parse_mode: enums.ParseMode | None = None,
        entities: list[types.MessageEntity] | None = None,
        disable_web_page_preview: bool | None = None,
        reply_markup: types.InlineKeyboardMarkup = None,
    ) -> Message:
        """Bound method *edit_text* of :obj:`~hydrogram.types.Message`.

        An alias exists as *edit*.

        Use as a shortcut for:

        .. code-block:: python

            await client.edit_message_text(
                chat_id=message.chat.id, message_id=message.id, text="hello"
            )

        Example:
            .. code-block:: python

                await message.edit_text("hello")

        Parameters:
            text (``str``):
                New text of the message.

            parse_mode (:obj:`~hydrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            entities (List of :obj:`~hydrogram.types.MessageEntity`):
                List of special entities that appear in message text, which can be specified instead of *parse_mode*.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            On success, the edited :obj:`~hydrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.edit_message_text(
            chat_id=self.chat.id,
            message_id=self.id,
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=reply_markup,
        )

    edit = edit_text

    async def edit_caption(
        self,
        caption: str,
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        reply_markup: types.InlineKeyboardMarkup = None,
    ) -> Message:
        """Bound method *edit_caption* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.edit_message_caption(
                chat_id=message.chat.id, message_id=message.id, caption="hello"
            )

        Example:
            .. code-block:: python

                await message.edit_caption("hello")

        Parameters:
            caption (``str``):
                New caption of the message.

            parse_mode (:obj:`~hydrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~hydrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            On success, the edited :obj:`~hydrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.edit_message_caption(
            chat_id=self.chat.id,
            message_id=self.id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            reply_markup=reply_markup,
        )

    async def edit_media(
        self,
        media: types.InputMedia,
        reply_markup: types.InlineKeyboardMarkup = None,
    ) -> Message:
        """Bound method *edit_media* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.edit_message_media(
                chat_id=message.chat.id, message_id=message.id, media=media
            )

        Example:
            .. code-block:: python

                await message.edit_media(media)

        Parameters:
            media (:obj:`~hydrogram.types.InputMedia`):
                One of the InputMedia objects describing an animation, audio, document, photo or video.

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            On success, the edited :obj:`~hydrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.edit_message_media(
            chat_id=self.chat.id,
            message_id=self.id,
            media=media,
            reply_markup=reply_markup,
        )

    async def edit_reply_markup(self, reply_markup: types.InlineKeyboardMarkup = None) -> Message:
        """Bound method *edit_reply_markup* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.edit_message_reply_markup(
                chat_id=message.chat.id, message_id=message.id, reply_markup=inline_reply_markup
            )

        Example:
            .. code-block:: python

                await message.edit_reply_markup(inline_reply_markup)

        Parameters:
            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup`):
                An InlineKeyboardMarkup object.

        Returns:
            On success, if edited message is sent by the bot, the edited
            :obj:`~hydrogram.types.Message` is returned, otherwise True is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.edit_message_reply_markup(
            chat_id=self.chat.id, message_id=self.id, reply_markup=reply_markup
        )

    async def forward(
        self,
        chat_id: int | str,
        message_thread_id: int | None = None,
        disable_notification: bool | None = None,
        schedule_date: datetime | None = None,
    ) -> types.Message | list[types.Message]:
        """Bound method *forward* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.forward_messages(
                chat_id=chat_id, from_chat_id=message.chat.id, message_ids=message.id
            )

        Example:
            .. code-block:: python

                await message.forward(chat_id)

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs; for supergroups only

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

        Returns:
            On success, the forwarded Message is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.forward_messages(
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            from_chat_id=self.chat.id,
            message_ids=self.id,
            disable_notification=disable_notification,
            schedule_date=schedule_date,
        )

    async def copy(
        self,
        chat_id: int | str,
        caption: str | None = None,
        message_thread_id: int | None = None,
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        show_caption_above_media: bool | None = None,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply = object,
    ) -> types.Message | list[types.Message]:
        """Bound method *copy* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.copy_message(
                chat_id=chat_id, from_chat_id=message.chat.id, message_id=message.id
            )

        Example:
            .. code-block:: python

                await message.copy(chat_id)

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            caption (``string``, *optional*):
                New caption for media, 0-1024 characters after entities parsing.
                If not specified, the original caption is kept.
                Pass "" (empty string) to remove the caption.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                for forum supergroups only.

            parse_mode (:obj:`~hydrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~hydrogram.types.MessageEntity`):
                List of special entities that appear in the new caption, which can be specified instead of *parse_mode*.

            show_caption_above_media (``bool``, *optional*):
                Pass True if the caption should be shown above the media.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardMarkup` | :obj:`~hydrogram.types.ReplyKeyboardRemove` | :obj:`~hydrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.
                If not specified, the original reply markup is kept.
                Pass None to remove the reply markup.

        Returns:
            :obj:`~hydrogram.types.Message`: On success, the copied message is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if self.service:
            log.warning(
                "Service messages cannot be copied. chat_id: %s, message_id: %s",
                self.chat.id,
                self.id,
            )
            return None
        if self.game and not await self._client.storage.is_bot():
            log.warning(
                "Users cannot send messages with Game media type. chat_id: %s, message_id: %s",
                self.chat.id,
                self.id,
            )
            return None
        if self.empty:
            log.warning("Empty messages cannot be copied.")
            return None
        if self.text:
            return await self._client.send_message(
                chat_id,
                text=self.text,
                entities=self.entities,
                parse_mode=enums.ParseMode.DISABLED,
                disable_web_page_preview=not self.web_page,
                disable_notification=disable_notification,
                message_thread_id=message_thread_id,
                reply_to_message_id=reply_to_message_id,
                schedule_date=schedule_date,
                protect_content=protect_content,
                reply_markup=self.reply_markup if reply_markup is object else reply_markup,
            )
        if self.media:
            send_media = partial(
                self._client.send_cached_media,
                chat_id=chat_id,
                disable_notification=disable_notification,
                message_thread_id=message_thread_id,
                reply_to_message_id=reply_to_message_id,
                schedule_date=schedule_date,
                protect_content=protect_content,
                reply_markup=self.reply_markup if reply_markup is object else reply_markup,
            )

            if self.photo:
                file_id = self.photo.file_id
            elif self.audio:
                file_id = self.audio.file_id
            elif self.document:
                file_id = self.document.file_id
            elif self.video:
                file_id = self.video.file_id
            elif self.animation:
                file_id = self.animation.file_id
            elif self.voice:
                file_id = self.voice.file_id
            elif self.sticker:
                file_id = self.sticker.file_id
            elif self.video_note:
                file_id = self.video_note.file_id
            elif self.contact:
                return await self._client.send_contact(
                    chat_id,
                    phone_number=self.contact.phone_number,
                    first_name=self.contact.first_name,
                    last_name=self.contact.last_name,
                    vcard=self.contact.vcard,
                    disable_notification=disable_notification,
                    message_thread_id=message_thread_id,
                    schedule_date=schedule_date,
                )
            elif self.location:
                return await self._client.send_location(
                    chat_id,
                    latitude=self.location.latitude,
                    longitude=self.location.longitude,
                    disable_notification=disable_notification,
                    message_thread_id=message_thread_id,
                    schedule_date=schedule_date,
                )
            elif self.venue:
                return await self._client.send_venue(
                    chat_id,
                    latitude=self.venue.location.latitude,
                    longitude=self.venue.location.longitude,
                    title=self.venue.title,
                    address=self.venue.address,
                    foursquare_id=self.venue.foursquare_id,
                    foursquare_type=self.venue.foursquare_type,
                    disable_notification=disable_notification,
                    message_thread_id=message_thread_id,
                    schedule_date=schedule_date,
                )
            elif self.poll:
                return await self._client.send_poll(
                    chat_id,
                    question=self.poll.question,
                    options=[opt.text for opt in self.poll.options],
                    disable_notification=disable_notification,
                    message_thread_id=message_thread_id,
                    schedule_date=schedule_date,
                )
            elif self.game:
                return await self._client.send_game(
                    chat_id,
                    game_short_name=self.game.short_name,
                    disable_notification=disable_notification,
                    message_thread_id=message_thread_id,
                )
            else:
                raise ValueError("Unknown media type")

            if self.sticker or self.video_note:
                return await send_media(file_id=file_id, message_thread_id=message_thread_id)

            if caption is None:
                caption = self.caption or ""
                caption_entities = self.caption_entities

            return await send_media(
                file_id=file_id,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                show_caption_above_media=show_caption_above_media,
                message_thread_id=message_thread_id,
            )
        raise ValueError("Can't copy this message")

    async def delete(self, revoke: bool = True):
        """Bound method *delete* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.delete_messages(chat_id=chat_id, message_ids=message.id)

        Example:
            .. code-block:: python

                await message.delete()

        Parameters:
            revoke (``bool``, *optional*):
                Deletes messages on both parts.
                This is only for private cloud chats and normal groups, messages on
                channels and supergroups are always revoked (i.e.: deleted for everyone).
                Defaults to True.

        Returns:
            True on success, False otherwise.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.delete_messages(
            chat_id=self.chat.id, message_ids=self.id, revoke=revoke
        )

    async def click(
        self,
        x: int | str = 0,
        y: int | None = None,
        quote: bool | None = None,
        timeout: int = 10,
    ):
        """Bound method *click* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for clicking a button attached to the message instead of:

        - Clicking inline buttons:

        .. code-block:: python

            await client.request_callback_answer(
                chat_id=message.chat.id,
                message_id=message.id,
                callback_data=message.reply_markup[i][j].callback_data,
            )

        - Clicking normal buttons:

        .. code-block:: python

            await client.send_message(
                chat_id=message.chat.id, text=message.reply_markup[i][j].text
            )

        Example:
            This method can be used in three different ways:

            1.  Pass one integer argument only (e.g.: ``.click(2)``, to click a button at index 2).
                Buttons are counted left to right, starting from the top.

            2.  Pass two integer arguments (e.g.: ``.click(1, 0)``, to click a button at position (1, 0)).
                The origin (0, 0) is top-left.

            3.  Pass one string argument only (e.g.: ``.click("Settings")``, to click a button by using its label).
                Only the first matching button will be pressed.

        Parameters:
            x (``int`` | ``str``):
                Used as integer index, integer abscissa (in pair with y) or as string label.
                Defaults to 0 (first button).

            y (``int``, *optional*):
                Used as ordinate only (in pair with x).

            quote (``bool``, *optional*):
                Useful for normal buttons only, where pressing it will result in a new message sent.
                If ``True``, the message will be sent as a reply to this message.
                Defaults to ``True`` in group chats and ``False`` in private chats.

            timeout (``int``, *optional*):
                Timeout in seconds.

        Returns:
            -   The result of :meth:`~hydrogram.Client.request_callback_answer` in case of inline callback button clicks.
            -   The result of :meth:`~Message.reply()` in case of normal button clicks.
            -   A string in case the inline button is a URL, a *switch_inline_query* or a
                *switch_inline_query_current_chat* button.

        Raises:
            RPCError: In case of a Telegram RPC error.
            ValueError: In case the provided index or position is out of range or the button label was not found.
            TimeoutError: In case, after clicking an inline button, the bot fails to answer within the timeout.
        """

        if isinstance(self.reply_markup, types.ReplyKeyboardMarkup):
            keyboard = self.reply_markup.keyboard
            is_inline = False
        elif isinstance(self.reply_markup, types.InlineKeyboardMarkup):
            keyboard = self.reply_markup.inline_keyboard
            is_inline = True
        else:
            raise ValueError("The message doesn't contain any keyboard")

        if isinstance(x, int) and y is None:
            try:
                button = [button for row in keyboard for button in row][x]
            except IndexError as e:
                raise ValueError(f"The button at index {x} doesn't exist") from e
        elif isinstance(x, int) and isinstance(y, int):
            try:
                button = keyboard[y][x]
            except IndexError as e:
                raise ValueError(f"The button at position ({x}, {y}) doesn't exist") from e
        elif isinstance(x, str) and y is None:
            label = x.encode("utf-16", "surrogatepass").decode("utf-16")

            try:
                button = next(button for row in keyboard for button in row if label == button.text)
            except IndexError as e:
                raise ValueError(f"The button with label '{x}' doesn't exists") from e
        else:
            raise ValueError("Invalid arguments")

        if is_inline:
            if button.callback_data:
                return await self._client.request_callback_answer(
                    chat_id=self.chat.id,
                    message_id=self.id,
                    callback_data=button.callback_data,
                    timeout=timeout,
                )
            if button.url:
                return button.url
            if button.switch_inline_query:
                return button.switch_inline_query
            if button.switch_inline_query_current_chat:
                return button.switch_inline_query_current_chat
            raise ValueError("This button is not supported yet")
        await self.reply(button, quote=quote)
        return None

    async def react(self, emoji: str = "", big: bool = False) -> bool:
        """Bound method *react* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_reaction(chat_id=chat_id, message_id=message.id, emoji="🔥")

        Example:
            .. code-block:: python

                await message.react(emoji="🔥")

        Parameters:
            emoji (``str``, *optional*):
                Reaction emoji.
                Pass "" as emoji (default) to retract the reaction.

            big (``bool``, *optional*):
                Pass True to show a bigger and longer reaction.
                Defaults to False.

        Returns:
            ``bool``: On success, True is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """

        return await self._client.send_reaction(
            chat_id=self.chat.id, message_id=self.id, emoji=emoji, big=big
        )

    async def retract_vote(
        self,
    ) -> types.Poll:
        """Bound method *retract_vote* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            client.retract_vote(
                chat_id=message.chat.id,
                message_id=message_id,
            )

        Example:
            .. code-block:: python

                message.retract_vote()

        Returns:
            :obj:`~hydrogram.types.Poll`: On success, the poll with the retracted vote is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """

        return await self._client.retract_vote(chat_id=self.chat.id, message_id=self.id)

    async def download(
        self,
        file_name: str = "",
        in_memory: bool = False,
        block: bool = True,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> str:
        """Bound method *download* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.download_media(message)

        Example:
            .. code-block:: python

                await message.download()

        Parameters:
            file_name (``str``, *optional*):
                A custom *file_name* to be used instead of the one provided by Telegram.
                By default, all files are downloaded in the *downloads* folder in your working directory.
                You can also specify a path for downloading files in a custom location: paths that end with "/"
                are considered directories. All non-existent folders will be created automatically.

            in_memory (``bool``, *optional*):
                Pass True to download the media in-memory.
                A binary file-like object with its attribute ".name" set will be returned.
                Defaults to False.

            block (``bool``, *optional*):
                Blocks the code execution until the file has been downloaded.
                Defaults to True.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the absolute path of the downloaded file as string is returned, None otherwise.

        Raises:
            RPCError: In case of a Telegram RPC error.
            ``ValueError``: If the message doesn't contain any downloadable media
        """
        return await self._client.download_media(
            message=self,
            file_name=file_name,
            in_memory=in_memory,
            block=block,
            progress=progress,
            progress_args=progress_args,
        )

    async def vote(
        self,
        option: int,
    ) -> types.Poll:
        """Bound method *vote* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            client.vote_poll(chat_id=message.chat.id, message_id=message.id, option=1)

        Example:
            .. code-block:: python

                message.vote(6)

        Parameters:
            option (``int``):
                Index of the poll option you want to vote for (0 to 9).

        Returns:
            :obj:`~hydrogram.types.Poll`: On success, the poll with the chosen option is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """

        return await self._client.vote_poll(
            chat_id=self.chat.id, message_id=self.id, options=option
        )

    async def pin(
        self, disable_notification: bool = False, both_sides: bool = False
    ) -> types.Message:
        """Bound method *pin* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.pin_chat_message(chat_id=message.chat.id, message_id=message_id)

        Example:
            .. code-block:: python

                await message.pin()

        Parameters:
            disable_notification (``bool``):
                Pass True, if it is not necessary to send a notification to all chat members about the new pinned
                message. Notifications are always disabled in channels.

            both_sides (``bool``, *optional*):
                Pass True to pin the message for both sides (you and recipient).
                Applicable to private chats only. Defaults to False.

        Returns:
            :obj:`~hydrogram.types.Message`: On success, the service message is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.pin_chat_message(
            chat_id=self.chat.id,
            message_id=self.id,
            disable_notification=disable_notification,
            both_sides=both_sides,
        )

    async def unpin(self) -> bool:
        """Bound method *unpin* of :obj:`~hydrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.unpin_chat_message(chat_id=message.chat.id, message_id=message_id)

        Example:
            .. code-block:: python

                await message.unpin()

        Returns:
            True on success.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.unpin_chat_message(chat_id=self.chat.id, message_id=self.id)
