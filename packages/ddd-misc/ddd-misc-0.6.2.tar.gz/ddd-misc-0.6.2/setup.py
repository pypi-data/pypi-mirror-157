# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dddmisc',
 'dddmisc.exceptions',
 'dddmisc.messagebus',
 'dddmisc.messages',
 'dddmisc.repository']

package_data = \
{'': ['*']}

install_requires = \
['tenacity>=8.0.1,<9.0.0', 'yarl>=1.7.2,<2.0.0']

setup_kwargs = {
    'name': 'ddd-misc',
    'version': '0.6.2',
    'description': 'Python EDA & DDD utilites',
    'long_description': '# Domain-driven Design Misc\n\nПакет предоставляет базовые классы и утилиты для реализации проекта с событийно-ориентированной архитектурой\nс использованием набора принципов DDD.\n\n## Классы\n\n**Классы объектов**\n- `BaseAggregate` - базовый класс для создания агрегата домена\n- `DDDEvent` - базовый класс для реализации событий домена\n- `DDDCommand` - базовый класс для реализации команд домена\n- `DDDStructure` - базовый класс для создания структур данных при описании команд и событий\n\nАтрибуты классов `DDDEvent`, `DDDCommand` и `DDDSturcture` задаются с использованием `Field`-классов из пакета `dddmisc.fields`\n\n- `get_message_class` - метод получения класса события или команды по его идентификатору из общего регистра\n- `get_error_class` - метод получения класса исключения домена из общего регистра\n\n**Класс репозиторий**\n\nРепозиторий уровень абстракции отвечающий за сохранение и воссоздание состояния агрегата.\n\nВ пакете репозиторий представлен 2-мя абстрактными классами для синхронной и асинхронной реализации:\n- `AbstractSyncRepository` - абстрактный класс для реализации синхронного репозитория\n- `AbstractAsyncRepository` - абстрактный класс для реализации асинхронного репозитория\n\nа также в пакете реализованы 2 декоратора `dddmisc.decorators.getter` и `dddmisc.decorators.agetter` для\nдекорирования методов репозитория для получения агрегата из базы данных.\n\n**UnitOfWork**\n\nUnit of work уровень абстракции отвечающий за обеспечения консистентности при сохранении состояния агрегата.\nUnit of work является надстройкой над репозиторием.\n\nВ пакете UnitOfWork представлен 2-мя абстрактными классами для синхронной и асинхронной реализации:\n- `AbstractSyncUnitOfWork` - абстрактный класс для реализации синхронного UnitOfWork\n- `AbstractAsyncUnitOfWork` - абстрактный класс для реализации асинхронного UnitOfWork\n\n**MessageBus**\n\nВ целях абстрагирования и унификации процесса доставки событий и команд до их обработчиков используется \nвнутрення шина сообщений. Дополнительно внутренняя шина сообщений обеспечивает итеративный процесс доставки событий,\nпорожденных агрегатом в процессе исполнения обработчиков на предыдущей итерации.\n\nВ пакете внутрення шина сообщений представлена классами:\n- `AsyncMessageBus` - реализации шины сообщений для использования в асинхронном коде\n- `SyncMessageBus` - реализации шины сообщений для использования в синхронном коде\n\n\n## Changelog\n\n**0.6.1**\n\n_future:_\n- add `filter` method for `getter` and `agetter` decorators\n\n**0.6.0**\n\n_future:_\n- Remove external messagebus from package.\n- Remove DDDResponse from package. Now messagebus handle method return object returned from handler.\n- Refactoring messagebus for set specified uow, repository and engine for handler.\n- Add decorators for get methods of repository. Removed abstract method `_get_from_storage` from repository.\n\n\n**0.5.4**\n\n_future:_\n- Execute events from commit aggregate changes when handler failed after commit\n- Parallel exec handlers subscribed to once event in sync messagebus\n\n\n**0.5.3**\n\n_bugfix:_\n- Make parallel execute event handlers in messagebus\n- Change messagebus log format\n\n\n**0.5.2**\n\n_bugfix:_\n- Fix error with nullable and default field attributes\n\n\n\n\n',
    'author': 'Vladislav Vorobyov',
    'author_email': 'vladislav.vorobyov@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
