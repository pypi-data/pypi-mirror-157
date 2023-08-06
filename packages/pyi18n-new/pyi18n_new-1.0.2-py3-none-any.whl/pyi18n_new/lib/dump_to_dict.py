import jsons
import json


def dump_to_dict(object):
    return jsons.loads(jsons.dumps(object))
