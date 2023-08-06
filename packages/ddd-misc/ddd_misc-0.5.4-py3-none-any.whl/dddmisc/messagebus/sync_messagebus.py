import logging
import threading
import typing as t
from queue import Queue, Empty

from tenacity import Retrying, stop_after_attempt, wait_exponential, RetryError

from dddmisc import DDDEvent, AbstractSyncUnitOfWork, AbstractSyncRepository, DDDCommand, DDDResponse
from dddmisc.messagebus.abstract import AbstractInternalMessagebus, SyncEventHandlerType, SyncCommandHandlerType


class EventThreadExecutor(threading.Thread):
    def __init__(self, event: DDDEvent, handler, executor, finish_callback: t.Callable):
        self.event = event
        self.executor = executor
        self.handler = handler
        self.callback = finish_callback
        super(EventThreadExecutor, self).__init__()

    def run(self) -> None:
        try:
            self.executor(self.event, self.handler)
        finally:
            self.callback()


class EventQueueObserve(threading.Thread):

    def __init__(self, events_queue: Queue, executor: t.Callable[[DDDEvent], None], logger: logging.Logger):
        self.events_queue = events_queue
        self.executor = executor
        self._run_flag = False
        self.logger = logger
        super(EventQueueObserve, self).__init__(daemon=True)

    def run(self) -> None:
        is_empty = False
        self._run_flag = True
        while self._run_flag or not is_empty:
            try:
                event, handler = self.events_queue.get(block=True, timeout=0.0001)
                is_empty = False
                EventThreadExecutor(event, handler, self.executor, self.events_queue.task_done).start()
            except Empty:
                is_empty = True
                continue
            except Exception:
                self.logger.exception('Events queue observe error')

    def stop(self, exception=None):
        self._run_flag = False
        self.events_queue.join()


class MessageBus(AbstractInternalMessagebus[
                     AbstractSyncUnitOfWork, AbstractSyncRepository, SyncEventHandlerType, SyncCommandHandlerType]):

    def __init__(self, uow_class, engine, *, repository_class=None,
                 event_retrying: int = 5, logger='ddd-misc'):
        super(MessageBus, self).__init__(uow_class, engine, repository_class=repository_class, logger=logger)
        self._event_retrying = event_retrying
        self._logger = logging.getLogger(logger)
        self._events_queue = Queue()
        self._event_executor = EventQueueObserve(self._events_queue, self._exec_event, self._logger)

    def start(self):
        self._event_executor.start()

    def stop(self, exception: Exception = None):
        self._event_executor.stop(exception)

    @t.overload
    def handle(self, message: DDDEvent) -> t.NoReturn:
        ...

    @t.overload
    def handle(self, message: DDDCommand) -> DDDResponse:
        ...

    def handle(self, message):
        if isinstance(message, DDDCommand):
            return self._handle_command(message)
        elif isinstance(message, DDDEvent):
            self._handle_event(message)
        else:
            self._logger.error('Handle not valid message type %s in messagebus %s', message, self)
            raise TypeError(f'{message} was not and DDDEvent ot DDDCommand')

    def _handle_command(self, command: DDDCommand) -> DDDResponse:
        handler = self.get_handlers(command)
        uow = self.get_uow()
        try:
            response = handler(command, uow)
            result = DDDResponse(command.__reference__, response)
            return result
        except Exception:
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
            self._events_queue.put((event, handler))

    def _exec_event(self, event: DDDEvent, handler: t.Callable[[DDDEvent, AbstractSyncUnitOfWork], None]):
        uow = self.get_uow()
        try:
            for attempt in Retrying(stop=stop_after_attempt(self._event_retrying),
                                    wait=wait_exponential(min=1, max=15)):
                with attempt:
                    handler(event, uow)
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
