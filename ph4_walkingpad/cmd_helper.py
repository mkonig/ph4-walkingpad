#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Some sources inspired by:
# Copyright (c) 2016-present Valentin Kazakov
#
# This module is part of asyncpg and is released under
# the Apache 2.0 License: http://www.apache.org/licenses/LICENSE-2.0
#
# This lib is inspired by Cmd standard lib Python >3.5 (under Python Software
# Foundation License 2)

import asyncio
import logging
import sys

from blessed import Terminal
from cmd2 import Cmd as Cmd2

logger = logging.getLogger(__name__)


class Ph4Cmd(Cmd2):
    prompt = "$> "

    def __init__(self, *args, **kwargs):
        super().__init__(allow_cli_args=False, **kwargs)
        self.t = Terminal()
        self.worker_loop = None
        self.cmd_running = True

    async def _read_line(self):
        while True:
            line = await self.loop.run_in_executor(None, sys.stdin.readline)

            # does not work:
            # line = await self.loop.run_in_executor(None, lambda: self._read_command_line(self.prompt))
            self._exec_cmd(line)
            print(self.prompt)
            sys.stdout.flush()

    async def acmdloop(self):
        """Async command loop compatible with previous ph4-acmd2 usage."""
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        if getattr(self, "intro", None):
            print(self.intro)
        # ensure prompt shown
        print(self.prompt, end="", flush=True)
        reader_task = asyncio.create_task(self._read_line())
        try:
            while self.cmd_running:
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass
        finally:
            if not reader_task.done():
                reader_task.cancel()
                try:
                    await reader_task
                except asyncio.CancelledError:
                    pass

    def looper(self, loop):
        logger.debug("Starting looper for loop %s" % (loop,))
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def submit_coro(self, coro, loop=None):
        return asyncio.run_coroutine_threadsafe(coro, loop or self.worker_loop)

    def wait_coro(self, coro, loop=None):
        future = self.submit_coro(coro, loop=loop)
        return future.result()

    def get_term_width(self):
        try:
            width = self.t.width
            if width is None or width <= 0:
                return 80
            return width
        except Exception:
            pass
        return 80
