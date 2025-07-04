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

from gzip import compress, decompress
from io import BytesIO
from typing import Any, cast

from .primitives.bytes import Bytes
from .primitives.int import Int
from .tl_object import TLObject


class GzipPacked(TLObject):
    ID = 0x3072CFA1

    __slots__ = ["packed_data"]

    QUALNAME = "GzipPacked"

    def __init__(self, packed_data: TLObject):
        self.packed_data = packed_data

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "GzipPacked":
        # Return the Object itself instead of a GzipPacked wrapping it
        return cast("GzipPacked", TLObject.read(BytesIO(decompress(Bytes.read(data)))))

    def write(self, *args: Any) -> bytes:
        b = BytesIO()

        b.write(Int(self.ID, False))

        b.write(Bytes(compress(self.packed_data.write())))

        return b.getvalue()
