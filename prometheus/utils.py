import json
import datetime
import re
import os


def serialize(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()

    elif isinstance(obj, datetime.date):
        return datetime.datetime(obj.year, obj.month, obj.day, 0, 0, 0, 0)

    elif isinstance(obj, bytes):
        return str(obj, "utf8")

    elif isinstance(obj, dict):
        return obj.__dict__

    elif isinstance(obj, list):
        list_items = list()
        for list_item in obj:
            list_items.append(serialize(list_item))

        return list_items
    else:
        return str(obj)


def deserialize(obj):
    if type(obj) == str:
        if re.search(r"^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+Z$", obj):
            return datetime.datetime.strptime(obj, "%Y-%m-%dT%H:%M:%S.%fZ")
    elif type(obj) == list:
        return [deserialize(i) for i in obj]

    # TODO more

    return obj


def json_dumps(obj):
    return json.dumps(obj, default=serialize)


def json_loads(string):
    return deserialize(
        json.loads(
            string, object_pairs_hook=lambda obj: {k: deserialize(v) for k, v in obj}
        )
    )


def float_env_var(env_variable):
    return float(os.environ.get(env_variable)) if os.environ.get(env_variable) else None


def int_env_var(env_variable):
    return int(os.environ.get(env_variable)) if os.environ.get(env_variable) else None


def instant_str():
    instant = datetime.datetime.utcnow()
    return f"{instant.year}-{instant.month}-{instant.day} {instant.hour}:{instant.minute}:{instant.second}"
