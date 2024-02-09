import tabulate
import ujson

from ... import const
from . import safety

def dict_as_table(json: dict | None) -> str:
    if isinstance(json, dict):
        for key, value in json.items():
            if key == 'token':
                json['token'] = safety.garble_token(json['token'])
            if value == None:
                json[key] = '?'
            if isinstance(value, (list, dict)):
                json[key] = ujson.dumps(value, sort_keys=True)[:72] + '...'
        return tabulate.tabulate(
            tabular_data=json.items(),
            headers=('field', 'value'),
            tablefmt='rounded_outline'
        )
    return ''