import typing

import bson
from dataclasses import field
from marshmallow import Schema, ValidationError, fields, missing
from marshmallow_dataclass import dataclass


class ObjectIdField(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs,
    ):
        try:
            return bson.ObjectId(value)
        except Exception:
            raise ValidationError("invalid ObjectId `%s`" % value)

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        if value is None:
            return missing
        return str(value)


Schema.TYPE_MAPPING[bson.ObjectId] = ObjectIdField


@dataclass
class User:
    first_name: str
    last_name: str
    is_tutor: bool
    _id: typing.Optional[bson.ObjectId] = field(default=None)

    Schema: typing.ClassVar[typing.Type[Schema]] = Schema
