# -*- coding: utf-8 -*-

"""
存地皮信息的函数 比如 TheWorld.Map:GetStringEncode
前缀九字节  VRSN + \x00\x01\x00\x00\x00   （strcpy(pre, "VRSN"); *(pre + 5) = 1; memcpy(pre + 9, *(const void **)(a1 + 24), v5);）
后面数据是小端格式 \x01\x00 -> 00000000 00000001 -> 1
klei 在 2022.06 修改了地皮的数量，本来是一字节 256，修改为二字节 65536   https://forums.kleientertainment.com/forums/topic/140904-tiles-changes-and-more/
正式版实装应该是在 2022.06.30 的码头更新 513447，meta.saveversion 应该是 5.12
旧的 tiles 被拆分为 tiles 和 tiledata 两项
oldtiles(01 1a 01 11 01 18 01 1c) -> newtiles(01 00 01 00 01 00 01 00) + tiledata(ff 8a ff 81 ff 88 ff 8c)
"""

from base64 import b64decode
from itertools import chain
from struct import iter_unpack
from functools import wraps


def _convert_base(fn):
    @wraps(fn)
    def wrap(data: str) -> list[int]:
        if not data.startswith('VlJTTgABAAAA'):
            raise TypeError('传入数据不是编码后的饥荒地图数据')

        data_decoded = b64decode(data)
        magic, data_real = data_decoded[:9], data_decoded[9:]

        return fn(data_real)

    return wrap


@_convert_base
def convert_tiles(data: str) -> list[int]:
    return list(chain.from_iterable(iter_unpack('<H', data)))


@_convert_base
def convert_oldtiles(data: str) -> list[int]:
    return [i[0] for i in iter_unpack('<2B', data)]


@_convert_base
def convert_nodeidtilemap(data: str) -> list[int]:
    return list(chain.from_iterable(iter_unpack('<H', data)))


# 下面还不知道怎么处理，不太懂，下面的处理方式暂时只是猜测，虽然感觉差不太多


@_convert_base
def convert_tiledata(data: str) -> list[int]:
    return [i[1] - 0x70 for i in iter_unpack('<2B', data)]


@_convert_base
def convert_oldtiledata(data: str) -> list[int]:
    return [i[1] for i in iter_unpack('<2B', data)]


@_convert_base
def convert_nav(data: str) -> list[int]:
    return [i[1] for i in iter_unpack('<2B', data)]
