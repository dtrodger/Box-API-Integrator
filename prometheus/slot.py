"""
Prometheus type
"""

from __future__ import annotations
import datetime
from typing import Dict
import uuid
import json
import pprint
import logging

import aioredis
import six

import prometheus.redis_client as prometheus_redis_client


log = logging.getLogger(__name__)


class SlotSerializer:
    _ignored_slots = [
        "document_nodes",
        "xml_element_tree",
        "csv_writer",
        "report_sheet",
        "xlsx_workbook",
        "box_upload_user",
        "__weakref__"
    ]
    _native_types = {
        "int": int,
        "long": int,
        "float": float,
        "str": str,
        "bool": bool,
        "date": datetime.date,
        "datetime": datetime.datetime,
        "object": object,
    }
    _primitive_types = (float, bool, bytes, six.text_type) + six.integer_types

    @property
    def self(self):
        return f"{type(self).__name__}:{str(self.id)}"

    @property
    def self_redis_key(self):
        return self.self

    def __dict__(self) -> Dict:
        return {slot: self.serialize(slot) for slot in self.__slots__ if slot not in self._ignored_slots}

    def __iter__(self):
        yield from self.__dict__().items()

    def serialize(self, slot=None, obj=None):

        if not obj:
            obj = getattr(self, slot)

        if isinstance(obj, self._primitive_types):
            serialized_obj = obj

        elif isinstance(obj, uuid.UUID):
            serialized_obj = str(obj)
            
        elif isinstance(obj, SlotSerializer):
            serialized_obj = dict(obj)

        elif isinstance(obj, datetime.datetime):
            serialized_obj = obj.isoformat()

        elif isinstance(obj, datetime.date):
            serialized_obj = datetime.datetime(
                obj.year, obj.month, obj.day, 0, 0, 0, 0
            ).isoformat()

        elif isinstance(obj, bytes):
            serialized_obj = str(obj, "utf8")

        elif isinstance(obj, dict):
            serialized_obj = dict(obj)
            
        elif isinstance(obj, tuple):
            serialized_obj = tuple(self.serialize(sub_obj) for sub_obj in obj)

        elif isinstance(obj, list):
            serialized_obj = [self.serialize(obj=sub_obj) for sub_obj in obj]

        elif obj is None:
            serialized_obj = obj

        else:
            serialized_obj = str(obj)

        return serialized_obj

    async def set_self_to_redis(self, redis_client: aioredis.Redis = None) -> bool:
        self_redis_record_obj = json.dumps(dict(self), default=str)

        return await prometheus_redis_client.set(
            redis_client, self.self_redis_key, self_redis_record_obj
        )

    async def get_self_from_redis(self, redis_client: aioredis.Redis = None) -> Dict:
        redis_record_obj = await prometheus_redis_client.get(
            redis_client, self.self_redis_key
        )

        loaded_redis_record = json.loads(redis_record_obj.decode("utf-8"))

        return loaded_redis_record

    def log_formatted_self(self):
        log.info(pprint.pformat(dict(self)))
