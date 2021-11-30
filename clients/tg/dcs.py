from dataclasses import field
from typing import ClassVar, Type, List, Dict, Any, Optional

from marshmallow_dataclass import dataclass
from marshmallow import Schema, EXCLUDE


@dataclass
class From:
    id: int
    is_bot: bool
    first_name: str
    username: str
    last_name: str = field(default='')
    language_code: str = field(default='')


@dataclass
class Chat:
    id: int
    first_name: str
    last_name: str
    username: str
    type: str


@dataclass
class File:
    file_id: str
    file_size: int
    file_unique_id: str
    file_path: Optional[str] = None
    file_name: Optional[str] = None

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


@dataclass
class Message:
    message_id: int
    from_: From = field(metadata={'data_key': 'from'})
    chat: Chat
    date: int
    text: str = field(default='')
    entities: List[Dict[str, Any]] = field(default_factory=list)
    document: Optional[File] = None

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


@dataclass
class UpdateObj:
    update_id: int
    message: Message


@dataclass
class GetUpdatesResponse:
    ok: bool
    result: List[UpdateObj]

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


@dataclass
class SendMessageResponse:
    ok: bool
    result: Message

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


@dataclass
class GetFileResponse:
    ok: bool
    result: File

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE
