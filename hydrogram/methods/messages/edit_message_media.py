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

import io
import re
from pathlib import Path

import hydrogram
from hydrogram import raw, types, utils
from hydrogram.file_id import FileType


class EditMessageMedia:
    async def edit_message_media(
        self: hydrogram.Client,
        chat_id: int | str,
        message_id: int,
        media: types.InputMedia,
        reply_markup: types.InlineKeyboardMarkup = None,
        file_name: str | None = None,
    ) -> types.Message:
        """Edit animation, audio, document, photo or video messages.

        If a message is a part of a message album, then it can be edited only to a photo or a video. Otherwise, the
        message type can be changed arbitrarily.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            message_id (``int``):
                Message identifier in the chat specified in chat_id.

            media (:obj:`~hydrogram.types.InputMedia`):
                One of the InputMedia objects describing an animation, audio, document, photo or video.

            reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

            file_name (``str``, *optional*):
                File name of the media to be sent. Not applicable to photos.
                Defaults to file's path basename.

        Returns:
            :obj:`~hydrogram.types.Message`: On success, the edited message is returned.

        Example:
            .. code-block:: python

                from hydrogram.types import InputMediaPhoto, InputMediaVideo, InputMediaAudio

                # Replace the current media with a local photo
                await app.edit_message_media(chat_id, message_id, InputMediaPhoto("new_photo.jpg"))

                # Replace the current media with a local video
                await app.edit_message_media(chat_id, message_id, InputMediaVideo("new_video.mp4"))

                # Replace the current media with a local audio
                await app.edit_message_media(chat_id, message_id, InputMediaAudio("new_audio.mp3"))
        """
        caption = media.caption
        parse_mode = media.parse_mode

        message, entities = None, None

        if caption is not None:
            message, entities = (await self.parser.parse(caption, parse_mode)).values()

        if isinstance(media, types.InputMediaPhoto):
            if isinstance(media.media, io.BytesIO) or Path(media.media).is_file():
                uploaded_media = await self.invoke(
                    raw.functions.messages.UploadMedia(
                        peer=await self.resolve_peer(chat_id),
                        media=raw.types.InputMediaUploadedPhoto(
                            file=await self.save_file(media.media),
                            spoiler=media.has_spoiler,
                        ),
                    )
                )

                media = raw.types.InputMediaPhoto(
                    id=raw.types.InputPhoto(
                        id=uploaded_media.photo.id,
                        access_hash=uploaded_media.photo.access_hash,
                        file_reference=uploaded_media.photo.file_reference,
                    ),
                    spoiler=media.has_spoiler,
                )
            elif re.match(r"^https?://", media.media):
                media = raw.types.InputMediaPhotoExternal(
                    url=media.media, spoiler=media.has_spoiler
                )
            else:
                media = utils.get_input_media_from_file_id(media.media, FileType.PHOTO)
        elif isinstance(media, types.InputMediaVideo):
            if isinstance(media.media, io.BytesIO) or Path(media.media).is_file():
                uploaded_media = await self.invoke(
                    raw.functions.messages.UploadMedia(
                        peer=await self.resolve_peer(chat_id),
                        media=raw.types.InputMediaUploadedDocument(
                            mime_type=self.guess_mime_type(file_name or media.media.name)
                            or "video/mp4",
                            thumb=await self.save_file(media.thumb),
                            spoiler=media.has_spoiler,
                            file=await self.save_file(media.media),
                            attributes=[
                                raw.types.DocumentAttributeVideo(
                                    supports_streaming=media.supports_streaming or None,
                                    duration=media.duration,
                                    w=media.width,
                                    h=media.height,
                                ),
                                raw.types.DocumentAttributeFilename(
                                    file_name=file_name or Path(media.media).name
                                ),
                            ],
                        ),
                    )
                )

                media = raw.types.InputMediaDocument(
                    id=raw.types.InputDocument(
                        id=uploaded_media.document.id,
                        access_hash=uploaded_media.document.access_hash,
                        file_reference=uploaded_media.document.file_reference,
                    ),
                    spoiler=media.has_spoiler,
                )
            elif re.match(r"^https?://", media.media):
                media = raw.types.InputMediaDocumentExternal(
                    url=media.media, spoiler=media.has_spoiler
                )
            else:
                media = utils.get_input_media_from_file_id(media.media, FileType.VIDEO)
        elif isinstance(media, types.InputMediaAudio):
            if isinstance(media.media, io.BytesIO) or Path(media.media).is_file():
                media = await self.invoke(
                    raw.functions.messages.UploadMedia(
                        peer=await self.resolve_peer(chat_id),
                        media=raw.types.InputMediaUploadedDocument(
                            mime_type=self.guess_mime_type(file_name or media.media.name)
                            or "audio/mpeg",
                            thumb=await self.save_file(media.thumb),
                            file=await self.save_file(media.media),
                            attributes=[
                                raw.types.DocumentAttributeAudio(
                                    duration=media.duration,
                                    performer=media.performer,
                                    title=media.title,
                                ),
                                raw.types.DocumentAttributeFilename(
                                    file_name=file_name or Path(media.media).name
                                ),
                            ],
                        ),
                    )
                )

                media = raw.types.InputMediaDocument(
                    id=raw.types.InputDocument(
                        id=media.document.id,
                        access_hash=media.document.access_hash,
                        file_reference=media.document.file_reference,
                    )
                )
            elif re.match(r"^https?://", media.media):
                media = raw.types.InputMediaDocumentExternal(url=media.media)
            else:
                media = utils.get_input_media_from_file_id(media.media, FileType.AUDIO)
        elif isinstance(media, types.InputMediaAnimation):
            if isinstance(media.media, io.BytesIO) or Path(str(media.media)).is_file():
                uploaded_media = await self.invoke(
                    raw.functions.messages.UploadMedia(
                        peer=await self.resolve_peer(chat_id),
                        media=raw.types.InputMediaUploadedDocument(
                            mime_type=self.guess_mime_type(file_name or media.media.name)
                            or "video/mp4",
                            thumb=await self.save_file(media.thumb),
                            spoiler=media.has_spoiler,
                            file=await self.save_file(media.media),
                            attributes=[
                                raw.types.DocumentAttributeVideo(
                                    supports_streaming=True,
                                    duration=media.duration,
                                    w=media.width,
                                    h=media.height,
                                ),
                                raw.types.DocumentAttributeFilename(
                                    file_name=file_name or Path(media.media).name
                                ),
                                raw.types.DocumentAttributeAnimated(),
                            ],
                        ),
                    )
                )

                media = raw.types.InputMediaDocument(
                    id=raw.types.InputDocument(
                        id=uploaded_media.document.id,
                        access_hash=uploaded_media.document.access_hash,
                        file_reference=uploaded_media.document.file_reference,
                    ),
                    spoiler=media.has_spoiler,
                )
            elif re.match(r"^https?://", media.media):
                media = raw.types.InputMediaDocumentExternal(
                    url=media.media, spoiler=media.has_spoiler
                )
            else:
                media = utils.get_input_media_from_file_id(media.media, FileType.ANIMATION)
        elif isinstance(media, types.InputMediaDocument):
            if isinstance(media.media, io.BytesIO) or Path(media.media).is_file():
                media = await self.invoke(
                    raw.functions.messages.UploadMedia(
                        peer=await self.resolve_peer(chat_id),
                        media=raw.types.InputMediaUploadedDocument(
                            mime_type=self.guess_mime_type(file_name or media.media.name)
                            or "application/zip",
                            thumb=await self.save_file(media.thumb),
                            file=await self.save_file(media.media),
                            attributes=[
                                raw.types.DocumentAttributeFilename(
                                    file_name=file_name or Path(media.media).name
                                )
                            ],
                        ),
                    )
                )

                media = raw.types.InputMediaDocument(
                    id=raw.types.InputDocument(
                        id=media.document.id,
                        access_hash=media.document.access_hash,
                        file_reference=media.document.file_reference,
                    )
                )
            elif re.match(r"^https?://", media.media):
                media = raw.types.InputMediaDocumentExternal(url=media.media)
            else:
                media = utils.get_input_media_from_file_id(media.media, FileType.DOCUMENT)

        r = await self.invoke(
            raw.functions.messages.EditMessage(
                peer=await self.resolve_peer(chat_id),
                id=message_id,
                media=media,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                message=message,
                entities=entities,
            )
        )

        for i in r.updates:
            if isinstance(i, (raw.types.UpdateEditMessage, raw.types.UpdateEditChannelMessage)):
                return await types.Message._parse(
                    client=self,
                    message=i.message,
                    users={i.id: i for i in r.users},
                    chats={i.id: i for i in r.chats},
                )
        return None
