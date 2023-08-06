# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dddmisc', 'dddmisc.exceptions', 'dddmisc.messagebus', 'dddmisc.messages']

package_data = \
{'': ['*']}

install_requires = \
['tenacity>=8.0.1,<9.0.0', 'yarl>=1.7.2,<2.0.0']

setup_kwargs = {
    'name': 'ddd-misc',
    'version': '0.5.4',
    'description': 'Python DDD utilites',
    'long_description': '# Domain-driven Design Misc\n\nПакет предоставляет базовые классы и утилиты для реализации проекта с событийно-ориентированной архитектурой\nс использованием набора принципов DDD.\n\n## Классы\n\n**Классы объектов**\n- `BaseAggregate` - базовый класс для создания агрегата домена\n- `DDDEvent` - базовый класс для реализации событий домена\n- `DDDCommand` - базовый класс для реализации команд домена\n- `DDDResponse` - класс исключение домена\n- `DDDStructure` - базовый класс для создания структур данных при описании команд и событий\n\nАтрибуты классов `DDDEvent`, `DDDCommand` и `DDDSturcture` задаются с использованием `Field`-классов из пакета `dddmisc.fields`\n\n- `get_message_class` - метод получения класса события или команды по его идентификатору из общего регистра\n- `get_error_class` - метод получения класса исключения домена из общего регистра\n\n**Класс репозиторий**\n\nРепозиторий уровень абстракции отвечающий за сохранение и воссоздание состояния агрегата.\n\nВ пакете репозиторий представлен 2-мя абстрактными классами для синхронной и асинхронной реализации:\n- `AbstractSyncRepository` - абстрактный класс для реализации синхронного репозитория\n- `AbstractAsyncRepository` - абстрактный класс для реализации асинхронного репозитория\n\n**UnitOfWork**\n\nUnit of work уровень абстракции отвечающий за обеспечения консистентности при сохранении состояния агрегата.\nUnit of work является надстройкой над репозиторием.\n\nВ пакете UnitOfWork представлен 2-мя абстрактными классами для синхронной и асинхронной реализации:\n- `AbstractSyncUnitOfWork` - абстрактный класс для реализации синхронного UnitOfWork\n- `AbstractAsyncUnitOfWork` - абстрактный класс для реализации асинхронного UnitOfWork\n\n**InternalMessageBus**\n\nВ целях абстрагирования и унификации процесса доставки событий и команд до их обработчиков используется \nвнутрення шина сообщений. Дополнительно внутренняя шина сообщений обеспечивает итеративный процесс доставки событий,\nпорожденных агрегатом в процессе исполнения обработчиков на предыдущей итерации.\n\nВ пакете внутрення шина сообщений представлена классами:\n- `AsyncMessageBus` - реализации шины сообщений для использования в асинхронном коде\n- `SyncMessageBus` - реализации шины сообщений для использования в синхронном коде\n\n**ExternalMessageBus**\n\nВ целях предоставления возможности обмена событиями и командами между различными системами или сервисами при использовании\nмикросервисной архитектуры пакетом предоставляются следующие классы:\n- `BaseExternalMessageBus` - Базовый класс предоставляющий функциональность по настройке и управлению подписками на события и команды\n- `AbstractAsyncExternalMessageBus` - абстрактный класс определяющий интерфейс для взаимодействия \nс внешней шиной сообщений для инициализации отправки событий и команд в асинхронном коде.\n- `AbstractSyncExternalMessageBus` - абстрактный класс определяющий интерфейс для взаимодействия \nс внешней шиной сообщений для инициализации отправки событий и команд в синхронном коде.\n\nДанные классы предназначены для разработки сторонних библиотек расширений \nпредоставляющих конкретные реализации протоколов обмена поверх `http`, `amoqp` и т.д.\n\n\n## Changelog\n\n**0.5.2**\n\n_bugfix:_\n- Fix error with nullable and default field attributes\n\n\n**0.5.3**\n\n_bugfix:_\n- Make parallel execute event handlers in messagebus\n- Change messagebus log format\n\n\n**0.5.4**\n_future:_\n- Execute events from commit aggregate changes when handler failed after commit\n- Parallel exec handlers subscribed to once event in sync messagebus\n\n\n',
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
