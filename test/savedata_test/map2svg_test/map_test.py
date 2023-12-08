# -*- coding: utf-8 -*-
from savedata import SaveData

from savedata.map.map2svg import Map, Tiles, NodeIdTileMap


def test_simple():
    map_data = list(zip(*[
        [1, 0, 1, 1, 1, 1],
        [0, 0, 1, 0, 1, 0],
        [1, 1, 1, 0, 1, 0],
        [1, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 1, 0],
        [1, 1, 1, 0, 1, 0],
        [1, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1],
    ]))
    map_ = Map(map_data, is_flipped=True)
    map_.save('test.svg')


def test_tiles():
    tiles = a.map.tiles
    world_tile_map = a.map.world_tile_map

    tile = Tiles(tiles, world_tile_map)
    tile.save('tiles.svg')


def test_nodeidtilemap():
    nodeidtilemap = a.map.nodeidtilemap
    ids = list(a.map.topology.ids.values())

    nm = NodeIdTileMap(nodeidtilemap, node_ids=ids, is_flipped=True)
    nm.save('nodeidtilemap.svg')


a = SaveData('../../../src/saved_data/0000000364')
# a = SaveData('../../../src/saved_data/0000020657')
# a = SaveData('../../../src/saved_data/now_2023.11.14')

test_simple()
test_tiles()
test_nodeidtilemap()
