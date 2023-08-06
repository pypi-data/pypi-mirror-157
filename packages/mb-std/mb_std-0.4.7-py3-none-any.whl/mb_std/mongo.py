from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Generic, Tuple, Type, TypeVar
from urllib.parse import urlparse

from bson import CodecOptions, Decimal128, ObjectId
from bson.codec_options import TypeCodec, TypeRegistry
from pydantic import BaseModel
from pymongo import ASCENDING, DESCENDING, IndexModel, MongoClient
from pymongo.collection import ReturnDocument
from pymongo.database import Database
from pymongo.results import DeleteResult, InsertManyResult, InsertOneResult, UpdateResult


class ObjectIdStr(str):
    @classmethod
    def validate(cls, v):
        return str(v)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate


class PropertyBaseModel(BaseModel):
    """
    Workaround for serializing properties with pydantic until
    https://github.com/samuelcolvin/pydantic/issues/935
    is solved
    """

    @classmethod
    def get_properties(cls):
        return [prop for prop in dir(cls) if isinstance(getattr(cls, prop), property) and prop not in ("__values__", "fields")]

    def dict(
        self,
        *,
        include=None,
        exclude=None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ):
        attribs = super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
        props = self.get_properties()
        # Include and exclude properties
        if include:
            props = [prop for prop in props if prop in include]
        if exclude:
            props = [prop for prop in props if prop not in exclude]

        # Update the attribute dict with the properties
        if props:
            attribs.update({prop: getattr(self, prop) for prop in props})

        return attribs


class MongoModel(PropertyBaseModel):
    __collection__: str = ""
    __validator__: dict | None = None
    __indexes__: list[IndexModel | str] = []

    def to_doc(self) -> dict:
        doc = self.dict()
        if doc["id"] is not None:
            doc["_id"] = doc["id"]
        del doc["id"]
        return doc

    @classmethod
    def init_collection(cls, database: Database) -> MongoCollection[T]:
        return MongoCollection.init(database, cls)


class DecimalCodec(TypeCodec):
    python_type = Decimal
    bson_type = Decimal128

    def transform_python(self, value):
        return Decimal128(value)

    def transform_bson(self, value):
        return value.to_decimal()


class MongoNotFoundError(Exception):
    def __init__(self, pk):
        self.pk = pk
        super().__init__(f"mongo document not found: {pk}")


@dataclass
class MongoConnection:
    client: MongoClient
    database: Database

    @staticmethod
    def connect(url: str) -> MongoConnection:
        client = MongoClient(url)
        database_name = MongoConnection.get_database_name_from_url(url)
        database = client[database_name]
        return MongoConnection(client=client, database=database)

    @staticmethod
    def get_database_name_from_url(db_url: str) -> str:
        return urlparse(db_url).path[1:]


T = TypeVar("T", bound=MongoModel)
SortType = list[Tuple[str, int]] | str | None
QueryType = dict[str, Any]
PKType = str | ObjectIdStr | int


def parse_str_index_model(index: str) -> IndexModel:
    unique = index.startswith("!")
    index = index.removeprefix("!")
    if "," in index:
        keys = []
        for i in index.split(","):
            order = DESCENDING if i.startswith("-") else ASCENDING
            i = i.removeprefix("-")
            keys.append((i, order))
    else:
        order = DESCENDING if index.startswith("-") else ASCENDING
        index = index.removeprefix("-")
        keys = [(index, order)]

    if unique:
        return IndexModel(keys, unique=True)
    return IndexModel(keys)


class MongoCollection(Generic[T]):
    def __init__(self, model: Type[T], database: Database, wrap_object_str_id: bool = True):
        if not model.__collection__:
            raise Exception("empty collection name")

        codecs = CodecOptions(type_registry=TypeRegistry([c() for c in [DecimalCodec]]))
        self.collection = database.get_collection(model.__collection__, codecs)
        if model.__indexes__:
            indexes = [parse_str_index_model(i) if isinstance(i, str) else i for i in model.__indexes__]
            self.collection.create_indexes(indexes)

        self.model_class = model
        self.wrap_object_id = model.__fields__["id"].type_ == ObjectIdStr and wrap_object_str_id
        if model.__validator__:
            # if collection exists
            if model.__collection__ in database.list_collection_names():
                query = [("collMod", model.__collection__), ("validator", model.__validator__)]
                res = database.command(OrderedDict(query))
                if "ok" not in res:
                    raise Exception("can't set schema validator")
            else:
                database.create_collection(model.__collection__, codec_options=codecs, validator=model.__validator__)

    def insert_one(self, doc: T) -> InsertOneResult:
        return self.collection.insert_one(doc.to_doc())

    def insert_many(self, docs: list[T], ordered=True) -> InsertManyResult:
        return self.collection.insert_many([obj.dict() for obj in docs], ordered=ordered)

    def _pk(self, pk: PKType):
        return ObjectId(pk) if self.wrap_object_id else pk

    def get_or_none(self, pk: PKType) -> T | None:
        res = self.collection.find_one({"_id": self._pk(pk)})
        if res:
            return self.model_class(**res)

    def get(self, pk: PKType) -> T:
        res = self.get_or_none(pk)
        if not res:
            raise MongoNotFoundError(pk)
        return res

    @staticmethod
    def _sort(sort: SortType):
        if isinstance(sort, str):
            if sort.startswith("-"):
                return [(sort[1:], -1)]
            return [(sort, 1)]
        return sort

    def find(self, query: QueryType, sort: SortType = None, limit: int = 0) -> list[T]:
        return [self.model_class(**d) for d in self.collection.find(query, sort=self._sort(sort), limit=limit)]

    def find_one(self, query: QueryType, sort: SortType = None) -> T | None:
        res = self.collection.find_one(query, sort=self._sort(sort))
        if res:
            return self.model_class(**res)

    def find_one_and_update(self, query: QueryType, update: QueryType) -> T | None:
        res = self.collection.find_one_and_update(query, update, return_document=ReturnDocument.AFTER)
        if res:
            return self.model_class(**res)

    def find_by_id_and_update(self, pk: PKType, update: QueryType) -> T | None:
        return self.find_one_and_update({"_id": self._pk(pk)}, update)

    def update_by_id(self, pk: PKType, update: QueryType, upsert=False) -> UpdateResult:
        return self.collection.update_one({"_id": self._pk(pk)}, update, upsert=upsert)

    def set_by_id(self, pk: PKType, update: QueryType) -> UpdateResult:
        return self.collection.update_one({"_id": self._pk(pk)}, {"$set": update})

    def set_and_push_by_id(self, pk: PKType, update: QueryType, push: QueryType) -> UpdateResult:
        return self.collection.update_one({"_id": self._pk(pk)}, {"$set": update, "$push": push})

    def update_one(self, query: QueryType, update: QueryType, upsert=False) -> UpdateResult:
        return self.collection.update_one(query, update, upsert=upsert)

    def update_many(self, query: QueryType, update: QueryType, upsert=False) -> UpdateResult:
        return self.collection.update_many(query, update, upsert=upsert)

    def delete_many(self, query: QueryType) -> DeleteResult:
        return self.collection.delete_many(query)

    def delete_one(self, query: QueryType) -> DeleteResult:
        return self.collection.delete_one(query)

    def delete_by_id(self, pk: PKType) -> DeleteResult:
        return self.collection.delete_one({"_id": self._pk(pk)})

    def count(self, query: QueryType) -> int:
        return self.collection.count_documents(query)

    def exists(self, query: QueryType) -> bool:
        return self.collection.count_documents(query) > 0

    def drop_collection(self):
        return self.collection.drop()

    @staticmethod
    def init(database: Database, model_class: Type[T]) -> MongoCollection[T]:
        return MongoCollection(model_class, database)


def make_query(**kwargs) -> QueryType:
    query: QueryType = {}
    for k, v in kwargs.items():
        if v:
            query[k] = v
    return query
