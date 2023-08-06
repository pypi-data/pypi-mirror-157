# Domain-driven Design Misc

Пакет предоставляет базовые классы и утилиты для реализации проекта с событийно-ориентированной архитектурой
с использованием набора принципов DDD.

## Классы

**Классы объектов**
- `BaseAggregate` - базовый класс для создания агрегата домена
- `DDDEvent` - базовый класс для реализации событий домена
- `DDDCommand` - базовый класс для реализации команд домена
- `DDDStructure` - базовый класс для создания структур данных при описании команд и событий

Атрибуты классов `DDDEvent`, `DDDCommand` и `DDDSturcture` задаются с использованием `Field`-классов из пакета `dddmisc.fields`

- `get_message_class` - метод получения класса события или команды по его идентификатору из общего регистра
- `get_error_class` - метод получения класса исключения домена из общего регистра

**Класс репозиторий**

Репозиторий уровень абстракции отвечающий за сохранение и воссоздание состояния агрегата.

В пакете репозиторий представлен 2-мя абстрактными классами для синхронной и асинхронной реализации:
- `AbstractSyncRepository` - абстрактный класс для реализации синхронного репозитория
- `AbstractAsyncRepository` - абстрактный класс для реализации асинхронного репозитория

а также в пакете реализованы 2 декоратора `dddmisc.decorators.getter` и `dddmisc.decorators.agetter` для
декорирования методов репозитория для получения агрегата из базы данных.

**UnitOfWork**

Unit of work уровень абстракции отвечающий за обеспечения консистентности при сохранении состояния агрегата.
Unit of work является надстройкой над репозиторием.

В пакете UnitOfWork представлен 2-мя абстрактными классами для синхронной и асинхронной реализации:
- `AbstractSyncUnitOfWork` - абстрактный класс для реализации синхронного UnitOfWork
- `AbstractAsyncUnitOfWork` - абстрактный класс для реализации асинхронного UnitOfWork

**MessageBus**

В целях абстрагирования и унификации процесса доставки событий и команд до их обработчиков используется 
внутрення шина сообщений. Дополнительно внутренняя шина сообщений обеспечивает итеративный процесс доставки событий,
порожденных агрегатом в процессе исполнения обработчиков на предыдущей итерации.

В пакете внутрення шина сообщений представлена классами:
- `AsyncMessageBus` - реализации шины сообщений для использования в асинхронном коде
- `SyncMessageBus` - реализации шины сообщений для использования в синхронном коде


## Changelog

**0.6.1**

_future:_
- add `filter` method for `getter` and `agetter` decorators

**0.6.0**

_future:_
- Remove external messagebus from package.
- Remove DDDResponse from package. Now messagebus handle method return object returned from handler.
- Refactoring messagebus for set specified uow, repository and engine for handler.
- Add decorators for get methods of repository. Removed abstract method `_get_from_storage` from repository.


**0.5.4**

_future:_
- Execute events from commit aggregate changes when handler failed after commit
- Parallel exec handlers subscribed to once event in sync messagebus


**0.5.3**

_bugfix:_
- Make parallel execute event handlers in messagebus
- Change messagebus log format


**0.5.2**

_bugfix:_
- Fix error with nullable and default field attributes




