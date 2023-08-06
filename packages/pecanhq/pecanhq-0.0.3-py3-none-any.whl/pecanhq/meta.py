# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import typing

T = typing.TypeVar("T")

class ResultSet(typing.Generic[T]):

    def __init__(self, uri: str, fn: typing.Callable[[str], typing.Dict]) -> None:
        self._uri = uri
        self._fn = fn
        self._rows = []
        self._cursor = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._cursor < len(self._rows):
            item = self._rows[self._cursor]
            self._cursor += 1
            return item
        elif self._uri:
            page = self._fn(self._uri)
            self._uri = page.get("@next", None)
            self._rows = page["rows"]
            self._cursor = 0
            return self.__next__()
        else:
            raise StopIteration


class Attachment(tuple):

    def __new__(self, filename: str, content: typing.IO, mimetype: str):
        return tuple.__new__(Attachment, (filename, content, mimetype))