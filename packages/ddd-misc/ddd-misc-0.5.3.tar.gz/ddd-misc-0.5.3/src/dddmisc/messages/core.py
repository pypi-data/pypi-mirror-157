import abc
import json
import typing as t
from dataclasses import dataclass
from types import MappingProxyType

from dddmisc import exceptions
from dddmisc.abstract import AbstractField
from dddmisc.exceptions import JsonDecodeError, ValidationError


class Nothing:
    pass


@dataclass(frozen=True)
class Metadata:
    fields: t.Mapping[str, AbstractField]
    domain: str
    is_baseclass: bool
    is_structure: bool = False


T = t.TypeVar('T')


class BaseDDDMessage(t.Generic[T]):
    __metadata__: Metadata

    def __init__(self, **kwargs):
        if self.__metadata__.is_baseclass:
            raise TypeError(f"cannot create instance of '{type(self).__name__}' class, because this is baseclass")
        self._data = self._deserialize(kwargs)

    def _deserialize(self, obj: dict):
        result = {}
        errors = {}
        for key, field in self.__metadata__.fields.items():
            if not (key.startswith('__') and key.endswith('__')):
                try:
                    result[key] = field.deserialize(obj.get(key, Nothing))
                except BaseException as err:
                    errors[key] = err
        if not errors:
            return result
        raise ValidationError(**errors)

    def _serialize(self):
        result = {}
        for key, field in self.__metadata__.fields.items():
            if not(key.startswith('__') and key.endswith('__')):
                result[key] = field.serialize(self._data.get(key))
        return result

    def get_attr(self, item: str):
        return self._data[item]

    def __eq__(self, other):
        return type(other) == type(self) and self._data == other._data

    def __hash__(self):
        return hash(repr(self.__dict__))

    def __repr__(self):
        fields = ', '.join(f'{name}={getattr(self, name)!r}' for name in self.__metadata__.fields.keys())
        return f'{self.__class__.__module__}.{self.__class__.__name__}({fields})'

    @classmethod
    def load(cls: t.Type[T], data: dict) -> T:
        """
        Method restore instance from data dict

        :param data:
        :return:
        """
        return cls(**data)

    @classmethod
    def loads(cls: t.Type[T], data: str) -> T:
        try:
            dict_data = json.loads(data)
        except json.JSONDecodeError as err:
            raise JsonDecodeError(str(err))
        return cls.load(dict_data)

    def dump(self) -> dict:
        """
        Method for dump instance to json dict

        :return:
        """
        return self._serialize()

    def dumps(self) -> str:
        data = self.dump()
        return json.dumps(data)


class DDDMessageMeta(abc.ABCMeta):
    __MESSAGE_COLLECTION: t.Dict[str, t.Type[BaseDDDMessage]] = {}

    def __new__(mcs, name: str, bases: t.Tuple[t.Type], attrs: dict):
        module = attrs.get('__module__')
        fullname = f'{module}.{name}'
        base_class = mcs._get_base_class(fullname, bases)
        if base_class not in bases:
            bases = (base_class, *bases)
        if attrs['__module__'] != __name__:
            fields = {key: field for key, field in attrs.items() if isinstance(field, AbstractField)}
            meta = attrs.get('Meta', None)
            attrs['__metadata__'] = mcs._create_metadata(base_class, meta, fields)
        klass = super().__new__(mcs, name, bases, attrs)
        mcs._register_message_class(klass)
        return klass

    @staticmethod
    def _get_base_class(name: str, bases: t.Tuple[t.Type]) -> t.Type[BaseDDDMessage]:
        domain_bases = [base for base in bases if issubclass(base, BaseDDDMessage)]
        if len(domain_bases) > 1:
            raise RuntimeError(f'{name} inherit from many "BaseDDDMessage" classes')
        elif len(domain_bases) == 0:
            return BaseDDDMessage
        else:
            return domain_bases[0]

    @staticmethod
    def _create_metadata(base: t.Type[BaseDDDMessage],
                         meta: t.Type, fields: t.Dict[str, AbstractField]) -> Metadata:
        base_meta = getattr(base, '__metadata__', Metadata(fields=MappingProxyType({}), domain=None,
                                                           is_baseclass=True, is_structure=False))
        is_baseclass = getattr(meta, 'is_baseclass', False)
        is_structure = base_meta.is_structure or bool(getattr(meta, 'is_structure', False))
        if is_structure:
            domain = None
        else:
            domain = base_meta.domain or getattr(meta, 'domain', None)
            if domain is None:
                is_baseclass = True
        fields = MappingProxyType({**base_meta.fields, **fields})
        return Metadata(fields=fields, domain=domain, is_baseclass=is_baseclass, is_structure=is_structure)

    @classmethod
    def _register_message_class(mcs, klass: t.Type[BaseDDDMessage]):
        if klass.__metadata__.is_baseclass or klass.__metadata__.domain is None:
            return
        domain = klass.__metadata__.domain
        name = klass.__name__
        key = f'{domain}.{name}'
        if key in mcs.__MESSAGE_COLLECTION:
            raise RuntimeError(f'Multiple message class in domain "{klass.__metadata__.domain}" with name "{name}"')
        mcs.__MESSAGE_COLLECTION[key] = klass

    @classmethod
    def get_message_collection(mcs) -> t.Mapping[str, t.Type[BaseDDDMessage]]:
        return MappingProxyType(mcs.__MESSAGE_COLLECTION)

    @property
    def __domain__(cls: BaseDDDMessage) -> str:
        return cls.__metadata__.domain


def get_message_class(key: str) -> t.Type[BaseDDDMessage]:

    collection = DDDMessageMeta.get_message_collection()
    if key in collection:
        return collection[key]
    raise exceptions.UnregisteredMessageClass(key=key)


