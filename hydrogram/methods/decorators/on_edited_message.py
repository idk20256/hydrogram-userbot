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

from typing import Callable, TypeVar

import hydrogram
from hydrogram.filters import Filter

F = TypeVar("F", bound=Callable)


class OnEditedMessage:
    def on_edited_message(
        self: hydrogram.Client | Filter | None = None,  # type: ignore
        filters: Filter | None = None,
        group: int = 0,
    ) -> Callable[[F], F]:
        """Decorator for handling edited messages.

        This does the same thing as :meth:`~hydrogram.Client.add_handler` using the
        :obj:`~hydrogram.handlers.EditedMessageHandler`.

        Parameters:
            filters (:obj:`~hydrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of messages to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: F) -> F:
            if isinstance(self, hydrogram.Client):
                self.add_handler(hydrogram.handlers.EditedMessageHandler(func, filters), group)
            elif isinstance(self, Filter) or self is None:
                if not hasattr(func, "handlers"):
                    func.handlers = []

                func.handlers.append((
                    hydrogram.handlers.EditedMessageHandler(func, self),
                    group if filters is None else filters,
                ))

            return func

        return decorator
