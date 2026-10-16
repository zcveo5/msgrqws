import json


def _fix(fp):
    with open(fp, 'rb') as fl:
        orig_fl_bytes = fl.read()
    if not orig_fl_bytes:
        print(f'[Cp1251Fix] {fp} no data')

    fl_enc = json.detect_encoding(orig_fl_bytes)

    orig_fl_str = orig_fl_bytes.decode(fl_enc)

    with open(fp, 'wb') as fl_write:
        fl_write.write(orig_fl_str.encode('utf-8'))

    return orig_fl_bytes.decode(fl_enc)


try:
    cnt = json.loads(_fix('./data/base_data.json'))
    _fix(f'./data/{cnt['LOAD_NC']}')
except json.JSONDecodeError:
    print('[Error] base data corrupted')
    exit()
except FileNotFoundError:
    pass