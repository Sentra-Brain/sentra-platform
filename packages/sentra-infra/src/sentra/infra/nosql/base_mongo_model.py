# packages/sentra-infra/src/sentra/infra/nosql/base_mongo_model.py
from pydantic import BaseModel, ConfigDict, field_serializer
from typing import Any, Optional


class BaseMongoModel(BaseModel):
    id: Optional[Any] = None

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True
    )

    @classmethod
    def from_mongo(cls, data: dict):
        """Convert MongoDB _id to standard 'id' field."""
        if not data:
            return None
        return cls(**{
            "id": str(data["_id"]) if "_id" in data else None,
            **{k: v for k, v in data.items() if k != "_id"}
        })

    @field_serializer("id", when_used="always")
    def serialize_id(self, v):
        return str(v) if v is not None else None
