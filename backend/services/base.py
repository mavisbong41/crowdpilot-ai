from typing import Any, Generic, TypeVar

from bson import ObjectId
from pydantic import BaseModel

from database.connection import get_database
from database.mongo import parse_object_id, serialize_document

CreateT = TypeVar("CreateT", bound=BaseModel)
UpdateT = TypeVar("UpdateT", bound=BaseModel)
ResponseT = TypeVar("ResponseT", bound=BaseModel)


class CRUDService(Generic[CreateT, UpdateT, ResponseT]):
    collection_name: str
    response_model: type[ResponseT]

    def _collection(self):
        return get_database()[self.collection_name]

    def _to_response(self, doc: dict[str, Any] | None) -> ResponseT | None:
        serialized = serialize_document(doc)
        if serialized is None:
            return None
        return self.response_model.model_validate(serialized)

    async def create(self, payload: CreateT) -> ResponseT:
        doc = payload.model_dump(mode="json")
        result = await self._collection().insert_one(doc)
        created = await self._collection().find_one({"_id": result.inserted_id})
        return self._to_response(created)  # type: ignore[return-value]

    async def get_by_id(self, resource_id: str) -> ResponseT | None:
        oid = parse_object_id(resource_id)
        if oid is None:
            return None
        doc = await self._collection().find_one({"_id": oid})
        return self._to_response(doc)

    async def list_all(self, skip: int = 0, limit: int = 50) -> list[ResponseT]:
        cursor = self._collection().find().skip(skip).limit(min(limit, 100))
        items: list[ResponseT] = []
        async for doc in cursor:
            item = self._to_response(doc)
            if item is not None:
                items.append(item)
        return items

    async def update(self, resource_id: str, payload: UpdateT) -> ResponseT | None:
        oid = parse_object_id(resource_id)
        if oid is None:
            return None

        updates = payload.model_dump(exclude_unset=True, mode="json")
        if not updates:
            return await self.get_by_id(resource_id)

        result = await self._collection().update_one({"_id": oid}, {"$set": updates})
        if result.matched_count == 0:
            return None
        doc = await self._collection().find_one({"_id": oid})
        return self._to_response(doc)

    async def delete(self, resource_id: str) -> bool:
        oid = parse_object_id(resource_id)
        if oid is None:
            return False
        result = await self._collection().delete_one({"_id": oid})
        return result.deleted_count > 0
