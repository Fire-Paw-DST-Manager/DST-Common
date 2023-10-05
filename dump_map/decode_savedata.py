# 游戏内调用klei的算法对字符串编码
# TheSim:SetPersistentString('123456789.lua', 'ABC', is_encode_save_bool [, callback]) => \
# ~/Documents/Klei/DoNotStarveTogether/446835953/client_save/123456789.lua
# TheSim:GetPersistentString("123456789.lua", function(load_success, str) print(str) end, false)
# TheSim:DecodeAndUnzipString('str') -> str
# TheSim:ZipAndEncodeString('str') -> strwd


from base64 import b64decode
from json import dumps, loads
from struct import iter_unpack
from itertools import chain


"""
if not savedata.map.tiledata then
    map:SetFromStringLegacy(savedata.map.tiles)
else
    map:SetFromString(savedata.map.tiles)
    map:SetMapDataFromString(savedata.map.tiledata)
end
"""


def decode_tile(tile_info: str, data_type: str = 'tiles') -> list[int]:  # ties, nav, nodeidtilemap, tiledata
    # 存地皮信息的函数 比如 TheWorld.Map:GetStringEncode()
    # 前缀九字节  VRSN + \x00\x01\x00\x00\x00   （strcpy(pre, "VRSN"); *(pre + 5) = 1; memcpy(pre + 9, *(const void **)(a1 + 24), v5);）
    # 后面数据是小端格式 \x01\x00 -> 00000000 00000001 -> 1
    # klei 在 2022.06 修改了地皮的数量，本来是一字节255，修改为二字节65535，所以要做区分，地皮应该不太可能过千，暂时按地皮编号大小区分
    # 旧的 tiles 被拆分为 tiles 和 tiledata 两项
    # oldtiles(01 1a 01 11 01 18 01 1c) -> newtiles(01 00 01 00 01 00 01 00) + tiledata(ff 8a ff 81 ff 88 ff 8c)
    if not tile_info.startswith('VlJTTgABAAAA'):
        raise TypeError('传入数据不是编码后的饥荒地图数据')

    xx = b64decode(tile_info)
    magic, xx = xx[:9], xx[9:]
    # print((xx[:99]).hex(' '))

    if data_type == 'tiles':
        # TODO 不应该这里判断，存档文件中应包含保存时版本号，在传入数据前就应该分清楚新旧
        new = True if 999 > max(chain.from_iterable(iter_unpack('<H', xx[:200]))) else False
        if new:
            tiles = list(chain.from_iterable(iter_unpack('<H', xx)))
        else:
            # tiles = [i[0] for i in zip(*([iter(xx)] * 2))]
            tiles = [i[0] for i in iter_unpack('<2B', xx)]

    elif data_type == 'nodeidtilemap':
        tiles = list(chain.from_iterable(iter_unpack('<H', xx)))

    # 这些还不知道怎么处理，不太懂，下面的处理方式暂时只是猜测，虽然感觉差不太多
    elif data_type == 'tiledata':
        # oldtiles(01 1a 01 11 01 18 01 1c) -> newtiles(01 00 01 00 01 00 01 00) + tiledata(ff 8a ff 81 ff 88 ff 8c)
        # tiles = [i[1] for i in iter_unpack('<2B', xx)]
        tiles = [i[1] - 0x70 for i in iter_unpack('<2B', xx)]

    elif data_type == 'nav':
        tiles = [i[1] for i in iter_unpack('<2B', xx)]

    else:
        raise TypeError(f'不支持的数据格式：{data_type}。应为 ties、nav、nodeidtilemap、tiledata 其中之一')

    return tiles


def load_savedata(lua_path='0000020657'):
    def table_dict(lua_table):
        typel = lupa.lua_type(lua_table)
        if typel is None:  # ['nil', 'boolean', 'number', 'string'] -> python type:
            return lua_table
        elif typel == 'table':
            keys = list(lua_table)
            # 假如lupa.table为空，或keys从数字 1 开始并以 1 为单位递增，则认为是列表，否则为字典。其他情况有点复杂，就这样吧
            if not len(keys) or keys[0] == 1 and all(map(lambda x: keys[x] + 1 == keys[x + 1], range(len(keys) - 1))):
                return [table_dict(x) for x in lua_table.values()]
            return {x: table_dict(y) for x, y in lua_table.items()}
        else:  # ['function', 'userdata', 'thread']
            return f'this is a {typel}'

    import lupa
    lua = lupa.LuaRuntime()
    with open(f'{lua_path}', 'r', encoding='utf-8') as f:
        data = f.read().removesuffix('\x00')
    data and ...
    xx = lua.eval('loadstring(python.eval("data"))()')
    return table_dict(xx)


def save_savadata(lua_path='0000020657', save_path='savadata.json'):
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(dumps(load_savedata(lua_path)))


if __name__ == '__main__':
    with open('./saved_data/savadata.json', 'r', encoding='utf-8') as savadata:
        savadata = loads(savadata.read())
        tile_encode = savadata['map']['tiles']
        # tile_encode = savadata['map']['tiledata']
        # tile_encode = savadata['map']['nodeidtilemap']
        # tile_encode = savadata['map']['nav']
    map_size = savadata['map']['width']
    from race import race


    def fn0():
        decode_tile(tile_encode)
        # print(tile_decode[:10])


    race(fn0, 1)

    # print(savadata['map']['world_tile_map'])
    # print(tile_decode[:100000])
    # print(set(tile_decode))
    # save_savadata('saved_data/0000000036', 'saved_data/savadata6.json')
