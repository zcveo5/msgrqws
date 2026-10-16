import base64
import json
import random
import string
from json import JSONDecodeError

BASE_ALPHABET = sorted(list(set(
    string.printable +
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
)))


def generate_salt(base=BASE_ALPHABET) -> dict:
    shuffled = base.copy()
    random.shuffle(shuffled)

    return dict(zip(base, shuffled))


def encrypt(data: str, salt: dict) -> str:
    return ''.join(salt.get(sym, sym) for sym in data)


def decrypt(data: str, salt: dict) -> str:
    inv_salt = {v: k for k, v in salt.items()}

    return ''.join(inv_salt.get(sym, sym) for sym in data)


META_LEN = 32
ENC_OFFSET = False
ENC_ON_CHR = 4


def fixed_zfill(s, width):
    if len(str(s)) > width:
        raise Exception(s, width)

    return str(s).zfill(width)

def enc_content_ord(data: str) -> str:
    if not data:
        return data

    chr_size = ENC_ON_CHR + (ENC_OFFSET * 2)

    out = [f'00{chr_size}{int(ENC_OFFSET)}']

    for char in data:
        code = ord(char)

        if ENC_OFFSET:
            max_o = min(0xFF, 0xFFFF - code)
            o = random.randint(0, max_o)
        else:
            o = 0

        code_enc = code + o

        total = (f'{o:02X}' if ENC_OFFSET else '') + f"{fixed_zfill(f'{hex(code_enc)[2::].upper()}', ENC_ON_CHR)}"

        out.append(total)

    return "".join(out)


def dec_content_ord(raw: str) -> str:
    try:
        if not raw:
            return raw

        cnt_meta = raw[:4]
        chr_len = int(cnt_meta[2], 16)
        offset = bool(int(cnt_meta[3], 16))
        data_e = raw[4::]

        tot = []
        for i in range(0, len(data_e), chr_len):
            chr_info = data_e[i:i + chr_len]

            if offset:
                o_hex = chr_info[:2]
                c_hex = chr_info[2:]

                o = int(o_hex, 16)
                c = int(c_hex, 16)

                original_code = c - o
            else:
                c_hex = chr_info
                c = int(c_hex, 16)
                original_code = c

            ch = chr(original_code)

            tot.append(ch)

        return "".join(tot)
    except Exception as _ex:
        _ex.add_note(f'Data: {raw}')
        raise _ex


def enc_content_ord2(data: str):
    out = []

    for i in data:
        out.append(f'{ord(i):03x}')

    return ''.join(out)

def dec_content_ord2(data: str):
    try:
        out = []

        for i in range(0, len(data), 3):
            chr_info = data[i:i + 3]

            out.append(chr(int(chr_info, 16)))

        return ''.join(out)
    except Exception as _ex:
        _ex.add_note(f'Data: {data}')
        raise _ex

def enc_content(data: str, method=0) -> str:
    match method:
        case 0:
            return enc_content_ord(data)
        case 1:
            return enc_content_ord2(data)

    raise Exception(f'Unknown encrypt method: {method}')

def dec_content(raw: str):
    enc_method = int(raw[0])
    match enc_method:
        case 0:
            return dec_content_ord(raw)
        case 1:
            return dec_content_ord2(raw)
    raise Exception(f'Unknown encrypt method: {enc_method}')


def fetch_metadata(b: bytes):
    key_len = int(b[0:6], 16)
    key_off = int(b[6:12], 16)
    content_len = int(b[12:20], 16)
    content_off = int(b[20:28], 16)

    enc_key = b[key_off:key_off + key_len].decode('utf-8')

    return dec_content(enc_key), content_off, content_len


def create_key_with_metadata(key, content_len):
    _key = enc_content(json.dumps(key, separators=(",", ":"), ensure_ascii=True))

    key_len_hex = f"{len(_key):06x}"
    key_off_hex = f"{META_LEN:06x}"
    c_len_hex = f"{content_len:08x}"
    coff_hex = f"{(META_LEN + len(_key)):08x}"

    meta = f"{key_len_hex}{key_off_hex}{c_len_hex}{coff_hex}".upper()

    meta_padded = meta.ljust(META_LEN, '0')

    return meta_padded, _key


def wrap_long_lines(text: str, chunk_size: int = 128) -> str:
    result = []
    for line in text.splitlines():
        if len(line) > chunk_size:
            chunks = [line[i:i + chunk_size] for i in range(0, len(line), chunk_size)]
            result.append('\n'.join(chunks))
        else:
            result.append(line)

    return '\n'.join(result)


def encrypt_bundle(content: str, *, trash=True, only_ascii=False):
    t = list(BASE_ALPHABET * 50) if trash else []
    random.shuffle(t)
    trash_start = enc_content(''.join(t))
    random.shuffle(t)
    trash_end = enc_content(''.join(t))

    file_start = f'{len(trash_start) + 6:06X}'

    if only_ascii:
        key = generate_salt(list(string.printable))
    else:
        key = generate_salt()

    e_cnt = enc_content(encrypt(content, key))

    meta, e_key = create_key_with_metadata(key, len(e_cnt))

    total_str = f'{file_start}{trash_start}{meta}{e_key}{e_cnt}{trash_end}'

    formatted_str = wrap_long_lines(total_str, 150)
    return formatted_str


def decrypt_bundle(raw_bytes):
    bts = raw_bytes.decode('utf-8').replace('\n', '').replace('\r', '').encode('utf-8')

    file_start = int(bts[0:6], 16)
    file_c = bts[file_start:]

    key, coff, c_len = fetch_metadata(file_c)

    e_cnt = file_c[coff:coff + c_len]
    try:
        rkey = json.loads(key)
    except JSONDecodeError:
        raise Exception(f'Error loading key: {key}')

    cnt = decrypt(dec_content(e_cnt.decode('utf-8')), rkey)

    return cnt