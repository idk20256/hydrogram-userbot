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

from .inline_query_result import InlineQueryResult


class InlineQueryResultVoice(InlineQueryResult):
    """Link to a voice recording in an .OGG container encoded with OPUS.

    By default, this voice recording will be sent by the user.
    Alternatively, you can use *input_message_content* to send a message with the specified content instead of the
    voice message.

    Parameters:
        voice_url (``str``):
            A valid URL for the voice recording.

        title (``str``):
            Title for the result.

        id (``str``, *optional*):
            Unique identifier for this result, 1-64 bytes.
            Defaults to a randomly generated UUID4.

        voice_duration (``int``, *optional*):
            Recording duration in seconds.

        caption (``str``, *optional*):
            Caption of the audio to be sent, 0-1024 characters.

        parse_mode (:obj:`~hydrogram.enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        caption_entities (List of :obj:`~hydrogram.types.MessageEntity`):
            List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

        show_caption_above_media (:obj:`bool`, *optional*):
            Wether the caption should be shown above the voice message.

        reply_markup (:obj:`~hydrogram.types.InlineKeyboardMarkup`, *optional*):
            Inline keyboard attached to the message.

        input_message_content (:obj:`~hydrogram.types.InputMessageContent`, *optional*):
            Content of the message to be sent instead of the audio.
    """

    def __init__(
        self,
        voice_url: str,
        title: str,
        id: str | None = None,
        voice_duration: int = 0,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        show_caption_above_media: bool | None = None,
        reply_markup: types.InlineKeyboardMarkup = None,
        input_message_content: types.InputMessageContent = None,
    ):
        super().__init__("voice", id, input_message_content, reply_markup)

        self.voice_url = voice_url
        self.title = title
        self.voice_duration = voice_duration
        self.caption = caption
        self.parse_mode = parse_mode
        self.caption_entities = caption_entities
        self.show_caption_above_media = show_caption_above_media

    async def write(self, client: hydrogram.Client):
        audio = raw.types.InputWebDocument(
            url=self.voice_url,
            size=0,
            mime_type="audio/mpeg",
            attributes=[
                raw.types.DocumentAttributeAudio(
                    duration=self.voice_duration,
                    title=self.title,
                )
            ],
        )

        message, entities = (
            await utils.parse_text_entities(
                client, self.caption, self.parse_mode, self.caption_entities
            )
        ).values()

        return raw.types.InputBotInlineResult(
            id=self.id,
            type=self.type,
            title=self.title,
            content=audio,
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
