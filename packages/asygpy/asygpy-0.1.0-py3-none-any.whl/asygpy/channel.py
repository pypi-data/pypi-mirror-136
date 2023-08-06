from __future__ import annotations

import asyncio
import signal
import typing

if typing.TYPE_CHECKING:
    from typing_extensions import Self

__all__ = ('SignalChannel',)


class SignalChannel:
    __slots__ = ('_signals', '_queue')

    def __init__(self) -> None:
        self._signals: typing.List[int] = []
        self._queue: asyncio.Queue[int] = asyncio.Queue()

    def add_signal(self, signum: int) -> Self:
        if signum not in signal.valid_signals():
            raise TypeError(f'Invalid signal: {signum}')

        self._signals.append(signum)
        return self

    def get_signals(self) -> typing.Tuple[int]:
        return tuple(self._signals)

    def __repr__(self) -> str:
        signals = ', '.join(repr(sig) for sig in self._signals)
        return f'<SignalChannel ({signals})>'

    def send(self, signum: int) -> None:
        if signum not in signal.valid_signals():
            raise TypeError(f'Invalid signal: {signum}')

        if signum in self._signals:
            self._queue.put_nowait(signum)

    async def receive(self) -> int:
        return await self._queue.get()

    async def __aiter__(self) -> typing.AsyncIterator[int]:
        while True:
            yield await self._queue.get()
