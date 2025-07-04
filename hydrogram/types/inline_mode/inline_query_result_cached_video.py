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

import hydrogram
from hydrogram import enums, raw, types, utils
from hydrogram.file_id import FileId

from .inline_query_result import InlineQueryResult


class InlineQueryResultCachedVideo(InlineQueryResult):
    """A link to a video file stored on the Telegram servers.

    By default, this video file will be sent by the user with an optional caption.
    Alternatively, you can use *input_message_content* to send a message with the specified content instead of the
    video.

    Parameters:
        video_file_id (``str``):
            A valid file identifier for the video file.

        title (``str``):
            Title for the result.

        id (``str``, *optional*):
            Unique identifier for this result, 1-64 bytes.
            Defaults to a randomly generated UUID4.

        description (``str``, *optional*):
            Short description of the result.

        caption (``str``, *optional*):
            Caption of the photo to be sent, 0-1024 characters.

        parse_mode (:obj:`~hydrogram.enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        caption_entities (List of :obj:`~hydrogram.types.MessageEntity`):
            List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

        show_caption_above_media (:obj:`bool`, *optional*):
            Wether the caption should be shown above the video.

        reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup`, *optional*):
            An InlineKeyboardMarkup object.

        input_message_content (:obj:`~hydrogram.types.InputMessageContent`):
            Content of the message to be sent instead of the photo.
    """

    def __init__(
        self,
        video_file_id: str,
        title: str,
        id: str | None = None,
        description: str | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        show_caption_above_media: bool | None = None,
        reply_markup: types.InlineKeyboardMarkup = None,
        input_message_content: types.InputMessageContent = None,
    ):
        super().__init__("video", id, input_message_content, reply_markup)

        self.video_file_id = video_file_id
        self.title = title
        self.description = description
        self.caption = caption
        self.parse_mode = parse_mode
        self.caption_entities = caption_entities
        self.show_caption_above_media = show_caption_above_media
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content

    async def write(self, client: hydrogram.Client):
        message, entities = (
            await utils.parse_text_entities(
                client, self.caption, self.parse_mode, self.caption_entities
            )
        ).values()

        file_id = FileId.decode(self.video_file_id)

        return raw.types.InputBotInlineResultDocument(
            id=self.id,
            type=self.type,
            title=self.title,
            description=self.description,
            document=raw.types.InputDocument(
                id=file_id.media_id,
                access_hash=file_id.access_hash,
                file_reference=file_id.file_reference,
            ),
            send_message=(
                await self.input_message_content.write(client, self.reply_markup)
                if self.input_message_content
                else raw.types.InputBotInlineMessageMediaAuto(
                    reply_markup=await self.reply_markup.write(client)
                    if self.reply_markup
                    else None,
                    message=message,
                    entities=entities,
                    invert_media=self.show_caption_above_media,
                )
            ),
        )
