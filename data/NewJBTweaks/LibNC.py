# METADATA
# {"req": []}
import json
import J
import Application


class NCApi:
    _non_dumped = {}

    @classmethod
    def create_ser(cls, name):
        name = f'JSON{name}'
        cls._non_dumped[name] = {}
        Application.dat_d[name] = '{}'

    @classmethod
    def _dump(cls):
        for ser, value in cls._non_dumped.items():
            Application.dat_d[ser] = json.dumps(value)

    @classmethod
    def write(cls, ser, key, value):
        try:
            cls._non_dumped[ser][key] = value
        except KeyError:
            cls._non_dumped[f'JSON{ser}'][key] = value
        cls._dump()

    @classmethod
    def read(cls, ser, key=None):
        try:
            got_ser = Application.dat_d[ser]
            is_json = False
        except KeyError:
            got_ser = Application.dat_d[f'JSON{ser}']
            is_json = True

        if is_json:
            got_ser = json.loads(got_ser)

        if key:
            return got_ser[key]
        else:
            return got_ser


J.SharedMemory['NCApi'] = NCApi
