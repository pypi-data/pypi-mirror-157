from eolymp.annotations import http_pb2 as _http_pb2
from eolymp.annotations import ratelimit_pb2 as _ratelimit_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Country(_message.Message):
    __slots__ = ["flag", "id", "name"]
    FLAG_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    flag: str
    id: str
    name: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., flag: _Optional[str] = ...) -> None: ...

class DescribeCountryInput(_message.Message):
    __slots__ = ["country_id"]
    COUNTRY_ID_FIELD_NUMBER: _ClassVar[int]
    country_id: str
    def __init__(self, country_id: _Optional[str] = ...) -> None: ...

class DescribeCountryOutput(_message.Message):
    __slots__ = ["country"]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    country: Country
    def __init__(self, country: _Optional[_Union[Country, _Mapping]] = ...) -> None: ...

class ListCountriesInput(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ListCountriesOutput(_message.Message):
    __slots__ = ["items", "total"]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[Country]
    total: int
    def __init__(self, items: _Optional[_Iterable[_Union[Country, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...
