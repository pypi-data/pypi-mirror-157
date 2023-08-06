from typing import Any, Callable, Dict, Optional, Type, TypeVar

from .serde_bson import as_bson, from_bson
from .serde_json import as_json, from_json

T = TypeVar("T", bound="Serde")


class Serde:
    def as_bson(
        self,
        *,
        as_type: Optional[Type] = None,
        custom_serializers: Dict[Type, Callable[[Any], Any]] = {},
    ) -> Dict[str, Any]:
        """
        Serialize the entire instance to BSON, by applying the field serializer
        to each field. Field names are converted to camel case.
        """
        assert as_type is None or issubclass(self.__class__, as_type), as_type
        return as_bson(
            self,
            as_type=as_type,
            custom_serializers=custom_serializers,
        )

    def as_json(
        self,
        *,
        as_type: Optional[Type] = None,
        custom_serializers: Dict[Type, Callable[[Any], Any]] = {},
    ) -> Dict[str, Any]:
        """
        Serialize the entire instance to JSON, by applying the field serializer
        to each field. Field names are converted to camel case.
        """
        assert as_type is None or issubclass(self.__class__, as_type), as_type
        return as_json(
            self,
            as_type=as_type,
            custom_serializers=custom_serializers,
        )

    @classmethod
    def from_bson(
        cls: Type[T],
        document: Dict[str, Any],
        custom_deserializers: Dict[Type, Callable[[Any], Any]] = {},
    ) -> T:
        """
        Deserialize an entire data class from BSON, by applying the field
        deserializer to each field. Field names are converted to camel case. The
        value may be modified by this function!
        """
        return from_bson(
            document,
            as_type=cls,
            custom_deserializers=custom_deserializers,
        )

    @classmethod
    def from_json(
        cls: Type[T],
        document: Dict[str, Any],
        custom_deserializers: Dict[Type, Callable[[Any], Any]] = {},
    ) -> T:
        """
        Deserialize an entire data class from JSON, by applying the field
        deserializer to each field. Field names are converted to camel case. The
        value may be modified by this function!
        """
        return from_json(
            document,
            as_type=cls,
            custom_deserializers=custom_deserializers,
        )
