# Convention based, effortless serialization and deserialization

Uniserde can convert Python classes to/from JSON and BSON without any input
from your side. Simply define the classes, and the library does the rest.

Simply define your types as classes with type annotations, and call one of the
serialization/deserialization functions:

```py
from uniserde import Serde
from datetime import datetime, timezone
from dataclasses import dataclass
from bson import ObjectId


@dataclass
class Person(Serde):
    id: ObjectId
    name: str
    birth_date: datetime


Betty = Person(
    id=ObjectId(),
    name="Betty",
    birth_date=datetime(year=1988, month=12, day=1, tzinfo=timezone.utc),
)

print(Betty.as_json())
```

This will print a dictionary similar to this one

```py
{
    'id': '62bc6c77792fc617c52499d0',
    'name': 'Betty',
    'birthDate': '1988-12-01T00:00:00+00:00'
}
```

You can easily convert this to a string using Python's built-in `json` module if
that's what you need.

# API

The API is intentionally simple. Functions/Classes you might be interested in
are:

- `as_json`, `as_bson`

  Given a class with type annotations, these create a JSON/BSON like dictionary.
  You can feed those into functions like `json.dump`, or use them as is.

- `from_json`, `from_bson`

  Given a JSON/BSON like dictionary, these will instantiate the corresponding
  Python class. Raise `SerdeError` if the values are invalid.

- `Serde` is a helper class you can optionally apply to your models. It adds the
  convenience functions `as_json`, `as_bson`, `from_json`, and `from_bson`
  directly to the models.

- Sometimes a class simply acts as a type-safe base, but you really just want to
  serialize the children of that class. In that case you can decorate the class
  with `@as_child`. This will store an additional `type` field in the result, so
  the correct child class can be parsed.

- `as_mongodb_schema` automatically creates JSON schemas compatible with MongoDB
  from models

# Types & Conventions

The library tries to stick to the naming conventions used by the target formats:

- names in JSON are written in lowerCamelCase, as is commonly done in
  JavaScript
- BSON uses the same conventions as JSON
- Python class names are expected to be written in UpperCamelCase
- Python enum values must be in ALL_UPPER_CASE

## JSON

| Python         | JSON            | Notes                                                                                                               |
| -------------- | --------------- | ------------------------------------------------------------------------------------------------------------------- |
| bool           | bool            |
| int            | float           |
| float          | float           |
| str            | str             |
| List           | list            |
| Optional       | value or `None` |
| Any            | as-is           |
| Literal[str]   | str             |
| enum.Enum      | str             | Enum values are mapped to their name (NOT value!)                                                                   |
| custom class   | dict            | Each attribute is stored as key, in lowerCamelCase. If marked with `as_child`, an additional `type` field is added. |
| bytes          | str             | base64 encoded                                                                                                      |
| datetime       | str             | as ISO 8601 - With timezone. Naïve datetimes are not supported.                                                     |
| Dict[str, ...] | dict            |
| bson.ObjectID  | str             |

## BSON

BSON uses the same conventions as JSON, with just a few changes

| Python        | BSON          | Notes                                                                                               |
| ------------- | ------------- | -----------------------------------------------------------------------------                       |
| custom class  | object        | Same as JSON, but any fields named `id` are renamed to `_id` to match MongoDB                       |
| bytes         | bytes         |
| datetime      | datetime      | Serialization requires a timezone be set. Deserialization imputes UTC, to match MongoDB convention. |
| bson.ObjectID | bson.ObjectId |

# Schema Generation

If you are working with MongoDB you will come to appreciate the automatic schema
generation. Calling `uniserde.as_mongodb_schema` on any supported class will return
a MongoDB compatible JSON schema without hassle.

For example `uniserde.as_mongodb_schema(Person)` with the `Person` class from above:

```py
{
    'type': 'object',
    'properties': {
        '_id': {
            'bsonType': 'objectId'
        },
        'name': {
            'type': 'string'
        },
        'birthDate': {
            'bsonType': 'date'
        }
    },
    'additionalProperties': False,
    'required': [
        'name',
        'birthDate'
    ]
}
```

# TODO

- Support for `Union` is currently very limited. Really only `Optional` is
  supported (which maps to `Union`)
- `Literal` currently only supports strings
- Make support for BSON optional, so the library doesn't depend on MongoDB
- Extend `as_child`, to allow marking some classes as abstract. i.e. their
  parents/children can be serialized, but not those classes themselves
- Datetime handling is weird. MongoDB does not store the timezone, so the BSON
  code assumes there is none. But really, every datetime should have a timezone
  set.
- Being able to specify additional limitations to fields would be nice:
  - must match regex
  - minimum / maximum
  - custom validation functions
- more Unit tests
- Add more examples to the README
  - show custom serializers/deserializers
  - recommended usage
