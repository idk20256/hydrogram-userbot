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

import re
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO, Callable

import hydrogram
from hydrogram import StopTransmission, enums, raw, types, utils
from hydrogram.errors import FilePartMissing
from hydrogram.file_id import FileType

if TYPE_CHECKING:
    from datetime import datetime


class SendDocument:
    async def send_document(
        self: hydrogram.Client,
        chat_id: int | str,
        document: str | BinaryIO,
        thumb: str | BinaryIO | None = None,
        caption: str = "",
        *,
        message_thread_id: int | None = None,
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        file_name: str | None = None,
        force_document: bool | None = None,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> types.Message | None:
        """Send generic files.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            document (``str`` | ``BinaryIO``):
                File to send.
                Pass a file_id as string to send a file that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a file from the Internet,
                pass a file path as string to upload a new file that exists on your local machine, or
                pass a binary file-like object with its attribute ".name" set for in-memory uploads.

            thumb (``str`` | ``BinaryIO``, *optional*):
                Thumbnail of the file sent.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            caption (``str``, *optional*):
                Document caption, 0-1024 characters.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                for forum supergroups only.

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

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

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
            :obj:`~hydrogram.types.Message` | ``None``: On success, the sent document message is returned, otherwise, in
            case the upload is deliberately stopped with :meth:`~hydrogram.Client.stop_transmission`, None is returned.

        Example:
            .. code-block:: python

                # Send document by uploading from local file
                await app.send_document("me", "document.zip")

                # Add caption to the document file
                await app.send_document("me", "document.zip", caption="document caption")


                # Keep track of the progress while uploading
                async def progress(current, total):
                    print(f"{current * 100 / total:.1f}%")


                await app.send_document("me", "document.zip", progress=progress)
        """
        file = None

        try:
            if isinstance(document, str):
                if Path(document).is_file():
                    thumb = await self.save_file(thumb)
                    file = await self.save_file(
                        document, progress=progress, progress_args=progress_args
                    )
                    media = raw.types.InputMediaUploadedDocument(
                        mime_type=self.guess_mime_type(document) or "application/zip",
                        file=file,
                        force_file=force_document or None,
                        thumb=thumb,
                        attributes=[
                            raw.types.DocumentAttributeFilename(
                                file_name=file_name or Path(document).name
                            )
                        ],
                    )
                elif re.match(r"^https?://", document):
                    media = raw.types.InputMediaDocumentExternal(url=document)
                else:
                    media = utils.get_input_media_from_file_id(document, FileType.DOCUMENT)
            else:
                thumb = await self.save_file(thumb)
                file = await self.save_file(
                    document, progress=progress, progress_args=progress_args
                )
                media = raw.types.InputMediaUploadedDocument(
                    mime_type=self.guess_mime_type(file_name or document.name)
                    or "application/zip",
                    file=file,
                    thumb=thumb,
                    attributes=[
                        raw.types.DocumentAttributeFilename(file_name=file_name or document.name)
                    ],
                )

            reply_to = utils.get_reply_head_fm(message_thread_id, reply_to_message_id)

            while True:
                try:
                    r = await self.invoke(
                        raw.functions.messages.SendMedia(
                            peer=await self.resolve_peer(chat_id),
                            media=media,
                            silent=disable_notification or None,
                            reply_to=reply_to,
                            random_id=self.rnd_id(),
                            schedule_date=utils.datetime_to_timestamp(schedule_date),
                            noforwards=protect_content,
                            reply_markup=await reply_markup.write(self) if reply_markup else None,
                            **await utils.parse_text_entities(
                                self, caption, parse_mode, caption_entities
                            ),
                        )
                    )
                except FilePartMissing as e:
                    await self.save_file(document, file_id=file.id, file_part=e.value)
                else:
                    for i in r.updates:
                        if isinstance(
                            i,
                            (
                                raw.types.UpdateNewMessage,
                                raw.types.UpdateNewChannelMessage,
                                raw.types.UpdateNewScheduledMessage,
                            ),
                        ):
                            return await types.Message._parse(
                                client=self,
                                message=i.message,
                                users={i.id: i for i in r.users},
                                chats={i.id: i for i in r.chats},
                                is_scheduled=isinstance(i, raw.types.UpdateNewScheduledMessage),
                            )
        except StopTransmission:
            return None
