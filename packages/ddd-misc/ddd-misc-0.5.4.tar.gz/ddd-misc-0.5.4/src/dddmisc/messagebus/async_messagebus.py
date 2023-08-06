import asyncio
import typing as t

from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential, RetryError

from dddmisc import AbstractAsyncUnitOfWork, AbstractAsyncRepository, DDDEvent, DDDCommand, DDDResponse
from dddmisc.messagebus.abstract import AbstractInternalMessagebus, AsyncEventHandlerType, AsyncCommandHandlerType


class AsyncMessageBus(AbstractInternalMessagebus[AbstractAsyncUnitOfWork, AbstractAsyncRepository,
                                                 AsyncEventHandlerType, AsyncCommandHandlerType]):
    _loop: asyncio.AbstractEventLoop

    def __init__(self, uow_class, engine, *, repository_class=None,
                 event_retrying: int = 5, logger='ddd-misc'):
        self._tasks: t.Set[asyncio.Task] = set()
        self._is_run = False
        self._daemon_task: t.Optional[asyncio.Task] = None
        self._start_event: t.Optional[asyncio.Event] = None

        self._event_retrying: int = event_retrying
        super(AsyncMessageBus, self).__init__(uow_class, engine, repository_class=repository_class, logger=logger)

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    @property
    def loop(self):
        return self._loop

    async def start(self):
        self._start_event = asyncio.Event(loop=self.loop)
        self._daemon_task = self.loop.create_task(self._run_daemon())
        await self._start_event.wait()

    async def stop(self, exception: Exception = None):
        self._start_event.clear()
        if self._daemon_task and not self._daemon_task.done():
            await self._daemon_task
        while self._tasks:
            tasks = tuple(self._tasks)
            await asyncio.gather(*tasks, return_exceptions=True)
            self._tasks.difference_update(tasks)

    async def _run_daemon(self):
        self._start_event.set()
        while self._start_event.is_set():
            if self._tasks:
                done, pending = await asyncio.wait(self._tasks, timeout=0.001)
                self._tasks.difference_update(done)
            else:
                await asyncio.sleep(0.001)

    @t.overload
    async def handle(self, message: DDDEvent):
        ...

    @t.overload
    async def handle(self, message: DDDCommand) -> DDDResponse:
        ...

    async def handle(self, message):
        if isinstance(message, DDDCommand):
            return await self._handle_command(message)
        elif isinstance(message, DDDEvent):
            return self._handle_event(message)
        else:
            self._logger.error('Handle not valid message type %s in messagebus %s', message, self)
            raise TypeError(f'{message} was not and DDDEvent ot DDDCommand')

    async def _handle_command(self, command: DDDCommand):
        handler = self.get_handlers(command)
        uow = self.get_uow()
        try:
            response = await handler(command, uow)
            result = DDDResponse(command.__reference__, response)
            return result
        except:
            self._logger.exception('Failure publish command', extra={
                'command': repr(command),
                'handler': repr(handler),
            })
            raise
        finally:
            for event in uow.collect_events():
                self._handle_event(event)

    def _handle_event(self, event: DDDEvent):
        for handler in self.get_handlers(event):
            task = self.loop.create_task(self._execute_handler_event(handler, event))
            self._tasks.add(task)

    async def _execute_handler_event(self, handler: AsyncEventHandlerType, event: DDDEvent):
        uow = self.get_uow()
        try:
            async for attempt in AsyncRetrying(stop=stop_after_attempt(self._event_retrying),
                                               wait=wait_exponential(min=1, max=15)):
                with attempt:
                    await handler(event, uow)

        except RetryError as retry_failure:
            self._logger.exception(
                'Failure publish event', extra={
                    'event': repr(event),
                    'handler': repr(handler),
                    'attempt_count': retry_failure.last_attempt.attempt_number,
                })
        finally:
            for ev in uow.collect_events():
                self._handle_event(ev)
