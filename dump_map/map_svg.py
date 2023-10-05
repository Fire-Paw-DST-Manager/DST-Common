# -*- coding: utf-8 -*-
from random import randint
from io import BytesIO
from json import loads
import logging as log
import xml.etree.ElementTree as et
from itertools import chain

log.basicConfig(format='%(asctime)s | %(levelname)-8s | %(lineno)4d %(funcName)-10s | - %(message)s',
                datefmt='%y-%m-%d %H:%M:%S',
                level=log.DEBUG)


class Svg:
    # 仅包含所需的svg属性
    _attr_svg = {
        'x': '0',
        'y': '0',
        'width': '100',
        'height': '100',
        # 'version': '1.1',
        # 'baseProfile': 'full',
        'xmlns': 'http://www.w3.org/2000/svg',
        # 'xmlns:xlink': 'http://www.w3.org/1999/xlink',
        # 'pointer-events': 'none',  # 屏蔽鼠标事件，避免卡顿
        # 'buffered-rendering': 'static',  # 缓存渲染的图像，避免卡顿
        'shape-rendering': 'crispEdges',  # 质量优先，防止边缘渲染不对齐出现白线
        'fill-rule': 'evenodd',
    }
    # buffered-rendering: static contain: paint
    # requestAnimationFrame https://blog.csdn.net/a843334549/article/details/123296950

    _declaration = '<?xml version="1.0" encoding="UTF-8" ?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'

    def __init__(self, ele=None, **kwargs) -> None:
        if not ele:
            self._attr_svg.update(kwargs)
            self._attr_svg['viewBox'] = f'0 0 {self._attr_svg["width"]} {self._attr_svg["height"]}'
            self.root = self._create_svg()
            self._svg = et.ElementTree(self.root)
        elif isinstance(ele, et.Element):
            self.root = ele
            self._svg = et.ElementTree(self.root)
        elif isinstance(ele, et.ElementTree):
            self.root = ele.getroot()
            self._svg = ele
        else:
            raise TypeError('传入参数[ele]类型需要是 et.ElementTree 或 et.Element')
        self.g = {}
        # self._create_css()

    def _create_svg(self) -> et.Element:
        return et.Element('svg', self._attr_svg)

    def _create_css(self, css_text) -> None:
        # 测试每个元素单独设置 fill 和通过 css 统一设置 fill，在缩放测试下实际耗时差别不大
        # 直接给 g 设置元素，不需要每个单独设置。效率未测试，直觉应该是比单独设置好的
        defs = et.SubElement(self.root, 'defs')
        style = et.SubElement(defs, 'style', {'type': 'text/css'})
        # css = ''.join([f'#g{key} path {{fill:{val}}}' for key, val in color.items()])
        style.append(self._create_cdata(css_text))

    @staticmethod
    def _create_cdata(content):
        content_cdata_comment = f'--><![CDATA[{content}]]><!--'
        return et.Comment(content_cdata_comment)

    def print(self) -> None:
        print(self._declaration, end='')
        et.dump(self.root)

    def save(self, save_path: str = 'export.svg', get_io=False):
        # etree 没有对DTD的支持，也不允许定义根元素之外的注释，只能保存时候自行处理
        # MDN 给出的创作指南[https://jwatt.org/svg/authoring/]说最好不要加 DTD，编辑时间段是 2005~2007
        # 但是w3c的在线检测[https://validator.w3.org/]会检测这个，如果没有会被判定为 xml，暂时保持添加
        svgio = BytesIO()
        svgio.write(self._declaration.encode('utf-8'))
        self._svg.write(svgio, encoding='utf-8', xml_declaration=False)
        svgio.seek(0)
        if get_io:
            return svgio

        if not save_path.endswith('.svg'):
            save_path += '.svg'
        with open(save_path, 'wb') as svgf:
            svgf.write(svgio.read())
        svgio.close()

    def creat_group(self, **kwargs) -> et.Element:
        if 'id' not in kwargs:
            for index in range(9999):
                g_id = f'g{index}'
                if g_id not in self.g:
                    kwargs['id'] = g_id
        self.g[kwargs['id']] = et.SubElement(self.root, 'g', kwargs)
        return self.g[kwargs['id']]


class Map:
    colors = {
        'TEST': 'orange',  # 测试用途

        'IMPASSABLE': '#000000',
        'ROAD': '#D1AE6E',
        'ROCKY': '#C2A163',
        'DIRT': '#F4CC80',
        'SAVANNA': '#DBA545',
        'GRASS': '#C7BD51',
        'FOREST': '#7D8146',
        'MARSH': '#836549',
        'WEB': '#000000',
        'WOODFLOOR': '#AE894A',
        'CARPET': '#B57647',
        'CHECKER': '#CE9E60',
        'CAVE': '#A48F63',
        'FUNGUS': '#57625F',
        'SINKHOLE': '#8C863C',
        'UNDERROCK': '#715E42',
        'MUD': '#8B5F2F',
        'BRICK': '#77734F',
        'BRICK_GLOW': '#787450',
        'TILES': '#6C4643',
        'TILES_GLOW': '#6E4744',
        'TRIM': '#473A2F',
        'TRIM_GLOW': '#6E4744',
        'FUNGUSRED': '#9A6647',
        'FUNGUSGREEN': '#69623A',
        'DECIDUOUS': '#A8784C',
        'DESERT_DIRT': '#E1B863',
        'SCALE': '#5C4929',
        'LAVAARENA_FLOOR': '#78270F',
        'LAVAARENA_TRIM': '#78270F',
        'QUAGMIRE_PEATFOREST': '#A0845A',
        'QUAGMIRE_PARKFIELD': '#A4754A',
        'QUAGMIRE_PARKSTONE': '#E7B879',
        'QUAGMIRE_GATEWAY': '#8B853B',
        'QUAGMIRE_SOIL': '#5A4429',
        'QUAGMIRE_CITYSTONE': '#DBB773',
        'PEBBLEBEACH': '#C0AD6B',
        'METEOR': '#8AA36D',
        'SHELLBEACH': '#C0AD6B',
        'ARCHIVE': '#906137',
        'FUNGUSMOON': '#59523A',
        'FARMING_SOIL': '#554127',

        'OCEAN_COASTAL': '#2E464E',
        'OCEAN_COASTAL_SHORE': '#2F464D',
        'OCEAN_SWELL': '#27354B',
        'OCEAN_ROUGH': '#2B2838',
        'OCEAN_BRINEPOOL': '#3E6467',
        'OCEAN_BRINEPOOL_SHORE': '#2F464D',
        'OCEAN_HAZARDOUS': '#1B181C',
        'OCEAN_WATERLOG': '#3A6165',

        'MONKEY_GROUND': '#BBA969',
        'MONKEY_DOCK': '#85664B',
        'MOSAIC_GREY': '#47362A',
        'MOSAIC_RED': '#702D2E',
        'MOSAIC_BLUE': '#46312D',
        'CARPET2': '#34171E',
    }

    svg_colors = [
        "aliceblue",
        "antiquewhite",
        "aqua",
        "aquamarine",
        "azure",
        "beige",
        "bisque",
        # "black",  # 背景专用
        "blanchedalmond",
        "blue",
        "blueviolet",
        "brown",
        "burlywood",
        "cadetblue",
        "chartreuse",
        "chocolate",
        "coral",
        "cornflowerblue",
        "cornsilk",
        "crimson",
        "cyan",
        "darkblue",
        "darkcyan",
        "darkgoldenrod",
        "darkgray",
        "darkgreen",
        "darkgrey",
        "darkkhaki",
        "darkmagenta",
        "darkolivegreen",
        "darkorange",
        "darkorchid",
        "darkred",
        "darksalmon",
        "darkseagreen",
        "darkslateblue",
        "darkslategray",
        "darkslategrey",
        "darkturquoise",
        "darkviolet",
        "deeppink",
        "deepskyblue",
        "dimgray",
        "dimgrey",
        "dodgerblue",
        "firebrick",
        "floralwhite",
        "forestgreen",
        "fuchsia",
        "gainsboro",
        "ghostwhite",
        "gold",
        "goldenrod",
        "gray",
        "grey",
        "green",
        "greenyellow",
        "honeydew",
        "hotpink",
        "indianred",
        "indigo",
        "ivory",
        "khaki",
        "lavender",
        "lavenderblush",
        "lawngreen",
        "lemonchiffon",
        "lightblue",
        "lightcoral",
        "lightcyan",
        "lightgoldenrodyellow",
        "lightgray",
        "lightgreen",
        "lightgrey",
        "lightpink",
        "lightsalmon",
        "lightseagreen",
        "lightskyblue",
        "lightslategray",
        "lightslategrey",
        "lightsteelblue",
        "lightyellow",
        "lime",
        "limegreen",
        "linen",
        "magenta",
        "maroon",
        "mediumaquamarine",
        "mediumblue",
        "mediumorchid",
        "mediumpurple",
        "mediumseagreen",
        "mediumslateblue",
        "mediumspringgreen",
        "mediumturquoise",
        "mediumvioletred",
        "midnightblue",
        "mintcream",
        "mistyrose",
        "moccasin",
        "navajowhite",
        "navy",
        "oldlace",
        "olive",
        "olivedrab",
        "orange",
        "orangered",
        "orchid",
        "palegoldenrod",
        "palegreen",
        "paleturquoise",
        "palevioletred",
        "papayawhip",
        "peachpuff",
        "peru",
        "pink",
        "plum",
        "powderblue",
        "purple",
        "red",
        "rosybrown",
        "royalblue",
        "saddlebrown",
        "salmon",
        "sandybrown",
        "seagreen",
        "seashell",
        "sienna",
        "silver",
        "skyblue",
        "slateblue",
        "slategray",
        "slategrey",
        "snow",
        "springgreen",
        "steelblue",
        "tan",
        "teal",
        "thistle",
        "tomato",
        "turquoise",
        "violet",
        "wheat",
        "white",
        "whitesmoke",
        "yellow",
        "yellowgreen",
    ]

    priority = {
        'INVALID': -1,
        'IMPASSABLE': 0,
        'OCEAN_COASTAL_SHORE': 1,
        'OCEAN_BRINEPOOL_SHORE': 2,
        'OCEAN_COASTAL': 3,
        'OCEAN_WATERLOG': 4,
        'OCEAN_BRINEPOOL': 5,
        'OCEAN_SWELL': 6,
        'OCEAN_ROUGH': 7,
        'OCEAN_HAZARDOUS': 8,
        'QUAGMIRE_GATEWAY': 9,
        'QUAGMIRE_CITYSTONE': 10,
        'QUAGMIRE_PARKFIELD': 11,
        'QUAGMIRE_PARKSTONE': 12,
        'QUAGMIRE_PEATFOREST': 13,
        'ROAD': 14,
        'PEBBLEBEACH': 15,
        'MONKEY_GROUND': 16,
        'SHELLBEACH': 17,
        'MARSH': 18,
        'ROCKY': 19,
        'SAVANNA': 20,
        'FOREST': 21,
        'GRASS': 22,
        'DIRT': 23,
        'DECIDUOUS': 24,
        'DESERT_DIRT': 25,
        'CAVE': 26,
        'FUNGUS': 27,
        'FUNGUSRED': 28,
        'FUNGUSGREEN': 29,
        'FUNGUSMOON': 30,
        'SINKHOLE': 31,
        'UNDERROCK': 32,
        'MUD': 33,
        'ARCHIVE': 34,
        'BRICK_GLOW': 35,
        'BRICK': 36,
        'TILES_GLOW': 37,
        'TILES': 38,
        'TRIM_GLOW': 39,
        'TRIM': 40,
        'METEOR': 41,
        'MONKEY_DOCK': 42,
        'SCALE': 43,
        'WOODFLOOR': 44,
        'CHECKER': 45,
        'MOSAIC_GREY': 46,
        'MOSAIC_RED': 47,
        'MOSAIC_BLUE': 48,
        'CARPET2': 49,
        'CARPET': 50,
        'QUAGMIRE_SOIL': 51,
        'FARMING_SOIL': 52,
        'LAVAARENA_TRIM': 53,
        'LAVAARENA_FLOOR': 54,
    }

    tiles_cache = {
        0: 'TEST',
        1: 'IMPASSABLE',
        2: 'ROAD',
        3: 'ROCKY',
        4: 'DIRT',
        5: 'SAVANNA',
        6: 'GRASS',
        7: 'FOREST',
        8: 'MARSH',
        9: 'WEB',
        10: 'WOODFLOOR',
        11: 'CARPET',
        12: 'CHECKER',
        13: 'CAVE',
        14: 'FUNGUS',
        15: 'SINKHOLE',
        16: 'UNDERROCK',
        17: 'MUD',
        18: 'BRICK',
        19: 'BRICK_GLOW',
        20: 'TILES',
        21: 'TILES_GLOW',
        22: 'TRIM',
        23: 'TRIM_GLOW',
        24: 'FUNGUSRED',
        25: 'FUNGUSGREEN',
        30: 'DECIDUOUS',
        31: 'DESERT_DIRT',
        32: 'SCALE',
        33: 'LAVAARENA_FLOOR',
        34: 'LAVAARENA_TRIM',
        35: 'QUAGMIRE_PEATFOREST',
        36: 'QUAGMIRE_PARKFIELD',
        37: 'QUAGMIRE_PARKSTONE',
        38: 'QUAGMIRE_GATEWAY',
        39: 'QUAGMIRE_SOIL',
        41: 'QUAGMIRE_CITYSTONE',
        42: 'PEBBLEBEACH',
        43: 'METEOR',
        44: 'SHELLBEACH',
        45: 'ARCHIVE',
        46: 'FUNGUSMOON',
        47: 'FARMING_SOIL',
        201: 'OCEAN_COASTAL',
        202: 'OCEAN_COASTAL_SHORE',
        203: 'OCEAN_SWELL',
        204: 'OCEAN_ROUGH',
        205: 'OCEAN_BRINEPOOL',
        206: 'OCEAN_BRINEPOOL_SHORE',
        207: 'OCEAN_HAZARDOUS',
        208: 'OCEAN_WATERLOG',
        256: 'MONKEY_GROUND',
        257: 'MONKEY_DOCK',
        258: 'MOSAIC_GREY',
        259: 'MOSAIC_RED',
        260: 'MOSAIC_BLUE',
        261: 'CARPET2',
        65535: 'INVALID',
    }

    def __init__(self, data_type: str = 'tiles', map_data: iter = None, world_tiles: dict = None, width: int = None, height: int = None,
                 bg_tile: int = 1):
        # map 相关
        self.data_type = data_type
        self.width = width
        self.height = height
        self.background_tile = bg_tile
        self.tile_codes: set = ...
        self.world_tiles: dict[str, int] = ...
        self.tiles: list[list[int]] = ...

        # svg 相关
        self.svg: Svg = ...
        self.root: et.Element = ...
        self.g: dict[int:et.Element] = ...

        # path 相关
        self.paths: Paths = ...

        if map_data:
            self.load_map_data(map_data, world_tiles, width, height)

    def _init(self, map_data: list, world_tiles: dict = None, width: int = None, height: int = None):
        """
        map_data 一维列表，数据需要是从左上角开始，由上至下，由左至右存入列表的（饥荒地图数据存储方式）
                 二维列表，数据需要是 列表长度为 width，子列表长度为 height 的二维列表
        """

        if not map_data:
            raise ValueError('传入地图数据为空')
        if isinstance(map_data[0], int):
            map_data_len = len(map_data)
            if width is None:
                if height is None:
                    width = height = int(map_data_len ** 0.5)
                    if width * height != map_data_len:
                        raise ValueError(f'未传入宽高，且 map_data 表示的地图不是正方形 {width=} {height=} {map_data_len=}')
                else:
                    width = map_data_len // height
            if height is None:
                height = map_data_len // width
            if width * height != map_data_len:
                raise ValueError(f'宽高数据与 map_data 表示的地图不符 {width} x {height} != {len(map_data)}')
            self.width = width
            self.height = height
            self.tile_codes = set(map_data)
            self.tiles = tuple(map_data[i * self.height: (i + 1) * self.height] for i in range(self.width))
        elif isinstance(map_data[0], (list, tuple)):
            self.width = len(map_data)
            self.height = len(map_data[0])
            self.tile_codes = set(chain(*map_data))
            self.tiles = map_data
        else:
            raise TypeError('传入地图数据格式错误')

        if not world_tiles:
            log.warning('未传入地皮名与地皮编号对应的关系，将使用预存的对应关系，对应关系并不一定准确')
            self.world_tiles = self.tiles_cache
        else:
            self.world_tiles = {j: i for i, j in world_tiles.items()}

        path_attr_common = {
            'stroke-width': '0.3' if self.data_type == 'tiles' else '0',
            'stroke-linejoin': "round",
            'stroke-linecap': "round",  # butt round square  无 圆角 方角
        }

        self.svg: Svg = Svg(width=str(self.width), height=str(self.height), **path_attr_common)
        self.root: et.Element = self.svg.root
        self.g: dict[int:et.Element] = self.svg.g

    def load_map_data(self, map_data: list, world_tiles: dict = None, width: int = None, height: int = None) -> None:
        self._init(map_data, world_tiles, width, height)

        # 根据地图数据构造对应的 Paths
        self.paths = Paths(self.tile_codes, self.background_tile)
        if self.background_tile in self.tile_codes:
            self.paths.paths[self.background_tile] = [f'M0 0h{self.width}v{self.height}h-{self.width}Z']

        # add_point = True
        add_point = False
        add_line = not add_point

        if add_point:
            paths = self.paths
            for row, line_tiles in enumerate(self.tiles):
                for col, tile_code in enumerate(line_tiles):
                    paths.add_point((row, col), tile_code)
            paths.merge_point()

        if add_line:
            temp_col, temp_tile = None, None
            max_col = self.height - 1
            for row, line_tiles in enumerate(self.tiles):
                for col, tile_code in enumerate(line_tiles):
                    if col == 0:
                        temp_col, temp_tile = col, tile_code
                    elif tile_code != temp_tile:
                        self.paths.add_line(temp_tile, row, temp_col, col - 1)
                        temp_col, temp_tile = col, tile_code
                        if col == max_col:
                            self.paths.add_line(temp_tile, row, col, col)
                    elif col == max_col:
                        self.paths.add_line(temp_tile, row, temp_col, col)
            self.paths.merge_line()

    def save(self, save_path: str = 'map', get_io=False):
        if self.data_type == 'tiles':
            # 根据地皮优先级列表，首先生成低优先级的，再生成高优先级的覆盖，用来支持不同优先级地皮间的覆盖效果
            tile_list = sorted(self.tile_codes, key=lambda x: self.priority.get(self.world_tiles.get(x), 0))
        else:
            tile_list = sorted(self.tile_codes)
        paths = self.paths.paths

        colors = self.svg_colors.copy()
        for tile_code in tile_list:
            path_list = paths[tile_code]
            if (self.data_type == 'tiles' or self.data_type == 'nodeidtilemap') and tile_code in self.world_tiles:
                tile_name = self.world_tiles[tile_code]
            else:
                tile_name = tile_code
            if tile_name not in self.g:
                color = self.colors.get(tile_name)
                if color is None:
                    if tile_name == self.background_tile:
                        color = 'black'
                    else:
                        if not colors:
                            colors = self.svg_colors.copy()
                        color = colors[randint(0, len(colors) - 1)]
                        colors.remove(color)
                        print(f'{tile_name} 没有对应的颜色，已随机选取颜色：{color}')
                # 通过边框实现地皮优先级覆盖会导致图形合并时连接的线也有边框，连接时避免同行同列，通过 M 命令连接可以避免
                self.g[tile_name] = et.SubElement(
                    self.root, 'g', {'id': f'g_{tile_name}',
                                     'stroke': color,
                                     # 'stroke-width': '0.25',  # 迁移到 svg 属性，在 self.init 中
                                     # 'stroke-linecap': "round",  # 迁移到 svg 属性，在 self.init 中
                                     # "stroke-linejoin": "round",  # 迁移到 svg 属性，在 self.init 中
                                     'fill': color})
            for path in path_list:
                et.SubElement(self.g[tile_name], 'path', {'d': path})

        # cx, cy = (self.width - 1) / 2 + 1, (self.height - 1) / 2 + 1
        # et.SubElement(self.root, 'path', {'stroke': 'red', 'stroke-width': '2', 'd': f'M{cx} {cy}Z'})

        return self.svg.save(save_path, get_io)


class Paths:
    def __init__(self, tile_codes: set[int], ignore_tile: int = None):
        self.tile_codes: set = tile_codes.copy()
        if ignore_tile is not None:
            self.tile_codes.discard(ignore_tile)
        self._ignore_tile: int = ignore_tile

        self._path_points: dict[int, list[tuple[int, int]]] = {tile_code: [] for tile_code in self.tile_codes}
        self._path_links: dict[int, dict[int, list[tuple[int, int]]]] = {tile_code: {} for tile_code in self.tile_codes}

        self._edges: dict[int, list[list[tuple[int, int]]]] = {tile_code: [] for tile_code in self.tile_codes}
        self.paths: dict[int, list[str]] = {tile_code: [] for tile_code in self.tile_codes}

    def add_point(self, pos: tuple[int, int], tile_code: int):
        if tile_code == self._ignore_tile:
            return
        self._path_points[tile_code].append(pos)

    def add_line(self, tile_code: int, row: int, col_start: int, col_end: int):
        if tile_code == self._ignore_tile:
            return
        tile_links = self._path_links[tile_code]
        if row not in tile_links:
            tile_links[row] = []
        tile_links[row].append((col_start, col_end))

    def merge_line(self):
        """通过添加的连线集，绘制这些点的组成形状的边缘。同种地皮的独立区块会被分配到单独的 path 中"""

        def line_links(row_, col_start_, col_end_):
            row_right_ = row_ + 1
            col_down_ = col_end_ + 1
            link_top_ = (row_, col_start_), (row_right_, col_start_)
            link_down_ = (row_, col_down_), (row_right_, col_down_)
            links_left_ = (((row_, col_), (row_, col_ + 1)) for col_ in range(col_start_, col_down_))
            links_right_ = (((row_right_, col_), (row_right_, col_ + 1)) for col_ in range(col_start_, col_down_))
            return {link_top_, link_down_, *links_left_, *links_right_}

        graphs: dict[int, list[set[tuple[tuple[int, int], tuple[int, int]]]]] = {tile_code: [] for tile_code in self.tile_codes}
        for tile_code, tile_links in self._path_links.items():
            if not tile_links:
                continue
            graphs_tile = graphs[tile_code]
            # gtis -> graphs_tile_indexs  通过该索引访问 graphs_tile。
            # 每列的图形通过 gtii_rows{row: gtii_row} 访问gti，以避免修改对应关系时需要遍历修改 相较于不使用该索引，效率高很多
            gtis = []
            gtii_rows: dict[int, list[int]] = {row: [] for row in tile_links}

            # 从小到大遍历每列，将未与前一列图形连接的图形作为新的记录图形存到列表中。相连接的则并入前一个图形，
            for row in sorted(tile_links):
                pre_row = row - 1
                gtii_row = gtii_rows[row]
                if pre_row not in tile_links:
                    # 不需要判断是否与前列相接
                    for ls, le in tile_links[row]:
                        new_graph = line_links(row, ls, le)
                        gtii_row.append(len(gtis))
                        gtis.append((len(graphs_tile)))
                        graphs_tile.append(new_graph)
                    continue

                pre_gtii_row = gtii_rows[pre_row]
                for ls, le in tile_links[row]:
                    new_graph = line_links(row, ls, le)

                    linked_gtiis = tuple((i, pre_gtii_row[i]) for i, (ps, pe) in enumerate(tile_links[pre_row])
                                         # if not (le < ps or ls > pe))  # 代表  横、纵  向有连接时合并
                                         if not (le < ps - 1 or ls > pe + 1)  # 代表  横、纵、斜  向有连接时合并
                                         )

                    if linked_gtiis:
                        # 与前一列的图形相连，将该图形并入相连的图形
                        linked = tuple((i, gtii, gtis[gtii], graphs_tile[gtis[gtii]]) for i, gtii in linked_gtiis)
                        if len(linked) == 1:
                            _, main_gtii, main_gti, main_graph = linked[0]
                            main_graph ^= new_graph
                            gtii_row.append(main_gtii)
                            continue

                        _, main_gtii, main_gti, main_graph = max(linked, key=lambda x: len(x[3]))

                        main_graph ^= new_graph

                        # gtii_row 添加 main_graph 的索引的索引
                        gtii_row.append(main_gtii)

                        # 如果相连的不止一个，将其它项合并到 main_graph，清空其它项，并替换为 main_graph
                        for other_index, other_gtii, other_gti, other_graph in linked:
                            if other_graph is main_graph:
                                continue

                            # 合并到 main_graph
                            main_graph ^= other_graph
                            # 将 graphs_tile 中此项清空，后期过滤掉
                            other_graph.clear()
                            # gtis 中该项替换为 main_gti
                            for i, gti in enumerate(gtis):
                                if gti == other_gti:
                                    gtis[i] = main_gti
                        continue

                    # print(f'create new graph: row({row}) col({ls}~{le})')
                    # 未与前一列图形相连，创建新的图形（由links构成），并将该图形添加到 gtis gtii_rows 中用来记录
                    # [link_top(1), link_down(1), *links_left(end - start + 1), *links_right(end - start + 1)]
                    # links 是有可能与其它元素重合的，重合说明是在图形内部，合并时会删掉，剩余的是该图形的边界
                    gtii_row.append(len(gtis))
                    gtis.append((len(graphs_tile)))
                    graphs_tile.append(new_graph)

        for tile_code, graphs_tile in graphs.items():
            for graph in graphs_tile:
                if not graph:
                    # 跳过空项。上面合并图形时，被清空的附属图形
                    continue
                # 一种地皮可能存在多个独立的区块，每个区块都单独处理
                self._merge_area(tile_code, graph)

        self.convert_path()

    def merge_point(self):
        """通过添加的点集，绘制这些点组成形状的边缘。同一地皮的所有区块都会被合并在一个 path 中"""
        links_all: dict[int, set] = {tile_code: set() for tile_code in self.tile_codes}
        # p -> point
        for tile_code in self._path_points:
            links_tile = links_all[tile_code]
            for x, y in self._path_points[tile_code]:
                # 按由上向下、由左向右的规则描出每块地皮的边缘，舍去重复的，就只剩小方块组成的大图形的边缘了
                p0, p1, p2, p3 = (x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)
                links_tile ^= {(p0, p1), (p1, p3), (p0, p2), (p2, p3)}

            if not links_tile:
                continue

            self._merge_area(tile_code, links_tile)

        self.convert_path()

    @staticmethod
    def _simple_link(single_tile: list[list[bool]]):
        """遍历每个元素，根据其四向环境判断是否在四边绘制  比较慢"""

        h = len(single_tile)
        w = len(single_tile[0]) if single_tile else 0

        links = []

        # 以左上角为原点为元素顶点建立坐标系
        # 每个地皮元素顶点自其自身左上角顺时针排序为 (0, 0), (1, 0), (1, 1), (0, 1)
        # 每条地皮元素边缘自其自身左上角顺时针排序为（不分方向） [(0, 0), (1, 0)], [(1, 0), (1, 1)], [(1, 1), (0, 1)], [(0, 1), (0, 0)]
        # 根据邻接元素的位置，先列出对应关系  出现环形图案时，内外连线方向一致会有问题，但是无所谓，fill-rule evenodd 会出手
        top = (0, -1, ((0, 0), (1, 0)))
        right = (1, 0, ((1, 0), (1, 1)))
        bottom = (0, 1, ((1, 1), (0, 1)))
        left = (-1, 0, ((0, 1), (0, 0)))
        sides = (top, right, bottom, left)

        for ir, row in enumerate(single_tile):
            for ic, value in enumerate(row):
                # ir 表示第几行，对应 y 值；ic 表示第几列，对应 x 值
                if not value:
                    # 不是待处理的地皮类型
                    continue

                # 判断四个方向上需不需要添加边缘
                for x_offset, y_offset, edge in sides:
                    xn, yn = ic + x_offset, ir + y_offset
                    if 0 <= xn < w and 0 <= yn < h and single_tile[yn][xn]:
                        # 邻接元素有 3 种情况，超出地图、与目标相同、与目标不同，1、3 需要添加边缘，2 不需要，所以跳过
                        continue

                    # 根据 edge 在对应位置添加边缘
                    start_offset, end_offset = edge
                    start = (start_offset[0] + ic, start_offset[1] + ir)
                    end = (end_offset[0] + ic, end_offset[1] + ir)
                    links.append((start, end))

        return links

    def _merge_area(self, tile_code: int, links_tile: set[tuple[tuple[int, int], tuple[int, int]]]):
        def vector_difference(p0_, p1_):
            return p0_[0] - p1_[0], p0_[1] - p1_[1]

        # links_tile 是分段的形状的边缘，每段方向都是由上向下或由左向右  下一步是通过这些散落的线段，获取有序的边缘上的点
        # 由于当前线段都是自上向下，自左向右，为了可以形成环，把翻转后的线段一起纳入
        links = links_tile | {(i[1], i[0]) for i in links_tile}
        rounts = []
        while links:
            # p -> point, ps -> point_start, pe -> point_end
            p0, p1 = links.pop()
            links.remove((p1, p0))
            rount = [p0]
            rounts.append(rount)

            ps = p0
            # p0 为 rount 的起点，p1 为 oldlink 的终点，newlink 的起点
            while p0 != p1:
                # 以 p1 为新的起点，向四个方向寻找存在的 link
                rount.append(p1)
                sx, sy = p1
                for pe in ((sx + 1, sy), (sx - 1, sy), (sx, sy + 1), (sx, sy - 1)):
                    if pe == ps:
                        continue
                    if (p1, pe) in links:
                        links.remove((p1, pe))
                        links.remove((pe, p1))
                        ps, p1 = p1, pe
                        break

        # 删去线段中无用的中间点
        better_rounts = []
        for rount in rounts:
            tmp_rount, pre_diff = [], vector_difference(rount[-1], rount[0])
            better_rounts.append(tmp_rount)
            for point0, point1 in zip(rount, [*rount[1:], rount[0]]):
                diff = vector_difference(point0, point1)
                if diff != pre_diff:
                    pre_diff = diff
                    tmp_rount.append(point0)
            # 这里本来还应该处理一下第一个点，但是删第一个点应该就比较影响效率了

        # 处理嵌套的图形
        if len(better_rounts) != 1:
            # 梳理再连好麻烦，需要多次遍历，感觉效率很低，还是直接连吧，排好序和随便连区别不大
            main_rount = max(better_rounts, key=lambda x: len(x))
            for rount in better_rounts:
                if rount is main_rount:
                    continue
                mx, my = main_access = main_rount[0]
                access_index = 0
                for i, p in enumerate(rount):
                    # 保证连线不是水平或竖直，从而在 convert_path 时采用 M 命令，进而避免连线出现边框
                    if mx != p[0] and my != p[1]:
                        access_index = i
                        break
                # [main_start, main_..., main_end] +
                # [main_start, *rount[access_index:], *rount[:access_index], rount[access_index], main_start]
                if main_access is not main_rount[-1]:
                    main_rount.append(main_access)
                main_rount.extend(rount[access_index:])
                main_rount.extend(rount[:access_index + 1])
                # main_rount.append(main_access)
            better_rounts = [main_rount]

        self._edges[tile_code].extend(better_rounts)

    def convert_path(self):
        """转为 svg 的 path 路径字符串"""
        for tile_code in self.tile_codes:
            edge_tile = self._edges[tile_code]
            for edge in edge_tile:
                path = []
                edge_iter = iter(edge)
                # s -> start
                sx, sy = edge_iter.__next__()
                path.append(f'M{sx} {sy}')
                for x, y in edge_iter:
                    if sx == x:
                        command, offset, sy = 'v', y - sy, y
                    elif sy == y:
                        command, offset, sx = 'h', x - sx, x
                    else:
                        command, offset = 'M', f'{x} {y}'
                        sx, sy = x, y
                        # print('注意：两点不在同行或同列')
                    path.append(f'{command}{offset}')
                path.append(f'Z')
                self.paths[tile_code].append(''.join(path))

        # print(self.paths)

    def __iter__(self):
        for tile_code in sorted(self.paths):
            yield tile_code, self.paths[tile_code]


def clip_map(map_data, height):
    test_tile = None
    row__start, row__end = 0, 92
    col__start, col__end = 0, 242
    if test_tile is not None:
        map_data = list(map(lambda x: 1 if x != test_tile else test_tile, map_data))
    map_data = map_data[row__start * height:row__end * height]
    map_data = [map_data[i * height: (i + 1) * height] for i in range(abs(row__start - row__end))]
    map_data = [i[col__start:col__end] for i in map_data]
    return map_data


def test_map():
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
    log.info('创建地图实例')
    map_ = Map('tiles', map_data, bg_tile=0)
    log.info('保存地图')
    map_.save()


def main():
    from decode_savedata import decode_tile

    with open('./saved_data/savadata4.json', 'r', encoding='utf-8') as savadata:
        data = loads(savadata.read())

    # from decode_savedata import load_savedata
    # data = load_savedata('./saved_data/0000000002')

    datatype = ['tiles', 'nav', 'nodeidtilemap', 'tiledata'][0]
    bg_tile = {'tiles': 1, 'nav': 0, 'nodeidtilemap': 0, 'tiledata': 0}[datatype]

    tile_encode = data['map'][datatype]

    # map_width = data['map']['width']
    # map_height = data['map']['height']

    if datatype == 'nodeidtilemap':
        """
        map.topology     这里存的应该都是 node 相关的数据
                    ids  存放nodeid，与nodeidtilemap共同指明各node的分布与范围
                    flattenedPoints  存放的是，各个node的边界，连接后可得到voronoi图
                    nodes  貌似是各个node的细节
        """
        name_id_map = data['map'].get('topology', {}).get('ids', [])
        name_id_map = {j: i + 1 for i, j in enumerate(name_id_map)}
    elif datatype == 'tiles':
        name_id_map = data['map'].get('world_tile_map')  # 地皮数量修改（22.06）之前的存档是没有该项的，且tiles与tiledata还没有分开
    else:
        name_id_map = {}

    # tile_decode = decode_tile(tile_encode, 'tiledata')
    tile_decode = decode_tile(tile_encode, datatype)
    # tile_decode = clip_map(tile_decode, map_height)
    # print(tile_decode[:100])
    # print(set(tile_decode))

    from time import time

    start_time = time()

    log.info('创建地图实例')
    map_ = Map(datatype, tile_decode, name_id_map, bg_tile=bg_tile)
    log.info('保存地图')
    map_.save(f'map_{datatype}.svg')

    print(time() - start_time)


if __name__ == '__main__':
    main()
    # test_map()

"""
游戏内，地皮坐标轴正向是和地图坐标系一致的，在屏幕逆时针旋转 45° 后，向下是x(0, )的正向，向右是y(, 0)的正向
但保存的游戏数据是按列保存的，先第一列，再第二列以此类推，因此该处构造的坐标系轴方向是与游戏内对调的，x, y -> y, x
但该处构造的坐标系与 svg 坐标系轴方向是一致的，因此虽然 svg 中显示方向与游戏内一致，但其 x,y 值是互换的，不可以直接用

游戏内默认方向 两个坐标体系
1 以地皮排列为基础构建的坐标系，默认上方指向 地皮的零点(0, 0)。向上走 x,y 逐渐减小，最小为(0, 0)  425*425 x,y ∈[0,424]
425*425 游戏内显示实际长度是 426  除去(0~424)，(0, 0)后面还有一个(0, 0)，这一行一列的地皮也是impassable，426*426范围外则是invalid，invalid上创建新实体时游戏会崩溃  两个(0, 0)都越过之后，开始负值计数
2 以地图中心为原点构建的坐标系，默认上方指向 x, y 轴的负方向
按 q 将屏幕逆时针旋转 45° 后，左上为地皮原点(0, 0)，  地图中心右下方半个地皮为坐标原点，下方为 x 轴正向，右为 y 轴正向

下方地皮坐标默认以地皮左上角的坐标为坐标，方便换算
坐标原点与地皮原点  425*425 坐标原点在 (212, 212)(213, 213) 两块地皮交接处，即 地皮(213, 213)    地皮(0, 0), (424, 424) 对应原点坐标(-852, -852) (844, 844)
400*400 坐标原点在 (200, 200) 地皮中心   地皮(0, 0), (399, 399) 对应坐标(-802, -802)(794, 794)
对于 size * size 的地图，地皮(0, 0) 的坐标是(-((size-1)/2+1)*4, -((size-1)/2+1)*4)
地皮(size-1, size-1) 的坐标是 (((size-1)/2 - 1)*4, ((size-1)/2 - 1)*4)
因为 size x size 大的地皮矩阵中，相邻边角的两块地皮间距是 size - 1，所以 (size - 1) - ((size-1)/2+1) = ((size-1)/2 - 1)

所以对于实体坐标，游戏内 x, y 坐标分别除以 4 并对调，加上 (size-1)/2+1，就是 svg 内实体坐标了
游戏 -> svg
(x, y) -> ( y / 4 + ((height-1)/2+1), x / 4 + ((width-1)/2+1) )
svg -> 游戏
(x, y) -> ( (y - (height-1)/2+1) * 4, (x - (width-1)/2+1) * 4 )
svg 中，地图中心坐标 ( (width-1)/2+1, (height-1)/2+1 )
游戏内地皮坐标中，地图中心坐标 ( (height-1)/2+1, (width-1)/2+1 )
"""
