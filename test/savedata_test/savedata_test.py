# -*- coding: utf-8 -*-

from savedata import SaveData


from time import time
s = time()
a = SaveData('../../src/saved_data/0000000364')
# a = SaveData('../../src/saved_data/0000020657')
# a = SaveData('../../src/saved_data/0000000002_base_23-10-20')
# a = SaveData('../../src/saved_data/now_2023.11.14')
print(time() - s)
print(a)

print(list(a.all_data))

print(list(a.map.model_dump()))
print(list(a.meta))
print(list(a.world_network))
print(len(a.ents))
print(list(a.mods))

print(a.super)
print(list(a.snapshot))

print(list(a.extra_data))

print(a.map.topology.model_dump().keys())
print(a.map.persistdata)
