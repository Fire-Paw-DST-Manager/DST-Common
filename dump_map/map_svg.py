# -*- coding: utf-8 -*-
import logging as log
import xml.etree.ElementTree as et
from collections import deque
from io import BytesIO
from json import loads
from random import shuffle
from typing import Union

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
            self._attr_svg.update({i: str(j) for i, j in kwargs.items()})
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
        # 直接给 g 元素设置，不需要每个单独设置。效率未测试，直觉应该是比单独设置好的
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
            for index in range(99999):
                g_id = f'g{index}'
                if g_id not in self.g:
                    kwargs['id'] = g_id
        self.g[kwargs['id']] = et.SubElement(self.root, 'g', kwargs)
        return self.g[kwargs['id']]


class Path:
    """绘制图像的边缘
    e.g. self.load_map
        input ([
                [1, 0, 0],
                [0, 0, 0],
                [0, 0, 1]
                ])
        output
            3,
            3,
            {
                0: [
                    [(1, 0), (3, 0), (3, 2), (2, 2), (2, 3), (0, 3), (0, 1), (1, 1)]
                ],
                1: [
                    [(0, 0), (1, 0), (1, 1), (0, 1)],
                    [(2, 2), (3, 2), (3, 3), (2, 3)]
                ],
            }
        *     *     *     *     |     *     *     *     *
                                |        1     0  -  0
        *     *           *     |     *     *  |     |  *
                                |        0  -  0  -  0
        *           *     *     |     *  |     |  *     *
                                |        0  -  0     1
        *     *     *     *     |     *     *     *     *
    """

    def __init__(self):
        self.width: int = 0
        self.height: int = 0

        # 对于一个二维数组，如果子元素中保存的是一行的数据，认为是正常图，一列的数据则认为是翻转 x, y 轴的图，默认处理正常方向的图
        self.flipped: bool = False

        self.map_data: list[list[int]] = []

        self.edges: dict[int, list[list[tuple[int, int]]]] = {}

        self.paths: dict[int, list[str]] = {}

    def load_map(self, map_data: list[list[int]], is_flipped: bool = False) -> tuple[int, int, dict[int, list[list[tuple[int, int]]]]]:

        if not map_data or not map_data[0]:
            return 0, 0, {}

        if isinstance(map_data[0], int):
            self.map_data = map_data.copy()
        else:
            self.map_data = [[j for j in i] for i in map_data]

        if self.flipped != is_flipped:
            self._flip_map()

        if self.map_data:
            self.width = len(self.map_data[0])
            self.height = len(self.map_data)
        else:
            self.width = 0
            self.height = 0

        for ele_id, single_info in self._link_point().items():
            self.edges[ele_id] = [self._attach(self._classify(rount)) for rount in single_info]

        return self.width, self.height, self.edges

    def _flip_map(self):
        # 翻转 x, y 轴
        self.map_data = [[i[x] for i in self.map_data] for x in range(len(self.map_data[0]))]

    def _link_point(self) -> dict[int, list[dict[tuple[int, int], set[tuple[int, int]]]]]:
        """分析传入地图信息，返回每种id的每块独立区域的边缘上的点与它们的出边
        默认处理正常图，若要处理反转图，可以通过翻转输入
        或调换函数内关于 self.map_data, map_data_padding, visited 的 x, y 值与 self.width, self.height
        e.g.
            self.map_data = [[0, 1],
                             [1, 0]]

                           |列表中每个字典代表一块独立区域|
                    {编号: [{顶点坐标: {出边向量, }, }, ], }  # 终点坐标 = 顶点坐标 + 出边向量   存图方式类似邻接表
            output: dict[int, list[dict[tuple[int, int], set[tuple[int, int]]]]] = {
            0: [
                {(0, 0): {(1, 0)}, (1, 0): {(0, 1)}, (1, 1): {(-1, 0)}, (0, 1): {(0, -1)}},  # 左上角的 0，没有与其它 0 相连，所以单独输出
                {(1, 1): {(1, 0)}, (2, 1): {(0, 1)}, (2, 2): {(-1, 0)}, (1, 2): {(0, -1)}}   # 右下角的 0，没有与其它 0 相连，所以单独输出
                ],
            1: [
                {(0, 1): {(1, 0)}, (1, 1): {(0, 1)}, (1, 2): {(-1, 0)}, (0, 2): {(0, -1)}},  # 左下角的 1，没有与其它 1 相连，所以单独输出
                {(1, 0): {(1, 0)}, (2, 0): {(0, 1)}, (2, 1): {(-1, 0)}, (1, 1): {(0, -1)}}   # 右上角的 1，没有与其它 1 相连，所以单独输出
                ]
            }
        """

        # 以左上角为原点为元素顶点建立坐标系
        # 每个地皮元素 顶点 自其自身左上角顺时针排序为 (0, 0), (1, 0), (1, 1), (0, 1)
        # 每条地皮元素 边缘 自其自身左上角顺时针排序为（不分方向） [(0, 0), (1, 0)], [(1, 0), (1, 1)], [(1, 1), (0, 1)], [(0, 1), (0, 0)]
        # 根据邻接元素的位置，先列出对应关系  出现环形图案时，内外连线方向一致会有问题，可以处理，但不必要，svg 的 fill-rule evenodd 可以解决
        # 邻接元素的偏移量
        right = (1, 0)
        left = (-1, 0)
        up = (0, -1)
        down = (0, 1)
        sides = (up, right, down, left)
        sides_edge = {
            # 切换坐标系时的偏移量 以该点为起点的连线
            up: ((0, 0), (1, 0)),
            right: ((1, 0), (0, 1)),
            down: ((1, 1), (-1, 0)),
            left: ((0, 1), (0, -1)),
        }
        # 上面只检查四向的元素，所以仅斜向相接的两块地皮不会被划分到同一个独立区域中，检查八向可以将它们划分在一个区域
        # 但是循环次数要多一倍，不是很值得
        # other_sides = (
        #     (1, -1),  # right up
        #     (1, 1),  # right down
        #     (-1, -1),  # left up
        #     (-1, 1),  # left down
        # )

        #           |列表中每个字典代表一块独立区域|
        # {地皮编号: [{顶点坐标: {出边向量, }, }, ], }
        all_tile_info: dict[int, list[dict[tuple[int, int], set[tuple[int, int]]]]] = {}

        queue = deque()

        # 令下标(-1)与(w+1)/(h+1)可被正常访问，并返回一个不会与地皮相同的值。
        # 与visited一起使用，免去判断是否下标越界，提高效率 可以省去接近 w * h * 4 * 4 次比较运算
        map_data_padding = [*[i + [None] for i in self.map_data], [None] * (self.width + 1)]

        # 初始值设为 False。额外添加的值设为 True，避免检查
        visited = [*[[False] * self.width + [True] for _ in range(self.height)], [True] * (self.width + 1)]

        # ehx, ehy -> element_header_x, element_header_y
        # for ehx, col in enumerate(self.map_data):
        for ehy, col in enumerate(self.map_data):
            # for ehy, tile_code in enumerate(col):
            for ehx, tile_code in enumerate(col):

                # if visited[ehx][ehy]:
                if visited[ehy][ehx]:
                    continue

                # print(f'out add {(ex, ey)} {tile_code=}')

                queue.append((ehx, ehy))
                # visited[ehx][ehy] = True
                visited[ehy][ehx] = True

                if tile_code not in all_tile_info:
                    all_tile_info[tile_code] = []

                all_tile_info[tile_code].append(single_tile_info := {})

                # ex, ey -> element_x, element_y
                while queue:
                    ex, ey = queue.pop()
                    # print(f'check {(px, py)}')

                    # 判断四个方向上是否需要添加边缘与检查
                    # eox, eoy -> element_offset_x, element_offset_y  邻接元素的偏移量
                    # nx, ny   -> neighbor_x, neighbor_y              邻接元素坐标
                    for eox, eoy in sides:
                        nx, ny = ex + eox, ey + eoy

                        # 邻接元素有 3 种情况，超出地图、与目标相同、与目标不同，1、3 需要添加边缘，2 需要检查邻接元素
                        # 添加了额外的数据使 1、3 具有相同的判断条件
                        # if map_data_padding[nx][ny] == tile_code:
                        if map_data_padding[ny][nx] == tile_code:
                            # if visited[nx][ny]:
                            if visited[ny][nx]:
                                continue

                            # print(f'in add {(nx, ny)} {tile_code=}')
                            queue.append((nx, ny))
                            # visited[nx][ny] = True
                            visited[ny][nx] = True
                            continue

                        # 情况 2
                        # vox, voy -> vertex_offset_x, vertex_offset_y    元素坐标转换顶点坐标的偏移量
                        (vox, voy), direction_vector = sides_edge[(eox, eoy)]

                        # 根据 offset 在对应位置添加边缘
                        start = ex + vox, ey + voy

                        if start not in single_tile_info:
                            single_tile_info[start] = set()

                        single_tile_info[start].add(direction_vector)

        return all_tile_info

    @staticmethod
    def _attach(rounts: list[list[tuple[int, int]]]) -> list[tuple[int, int]]:
        """独立区域可能包含多条边缘，比如环形区域有内边缘与外边缘
        将这些边缘合并为一条
        做法是 随机选一条作为主路径，将其封闭，再将其它路径添加在后面，然后回到主路径起点，继续连接下一条路径"""
        main_rount = max(rounts, key=lambda _: len(_))
        for rount in rounts:
            if rount is main_rount:
                continue
            mx, my = main_access = main_rount[0]
            access_index = 0
            for i, (px, py) in enumerate(rount):
                # 保证连线不是水平或竖直，一般情况无意义，是为了处理成 svg 路径时方便判断使用 M 命令，避免出现连线
                if mx != px and my != py:
                    access_index = i
                    break
            # [main_start, main_..., main_end] + /
            # [main_start, *rount[access_index:], *rount[:access_index], rount[access_index], main_start]
            if main_access != main_rount[-1]:
                main_rount.append(main_access)
            main_rount.extend(rount[access_index:])
            main_rount.extend(rount[:access_index + 1])
            # main_rount.append(main_access)

        return main_rount

    @staticmethod
    def _classify(links: dict[tuple[int, int], set[tuple[int, int]]]) -> list[list[tuple[int, int]]]:
        """通过传入的图的数据，将其中的通路连接起来并返回"""
        rounts = []

        def choose_start():
            # 选择某条连线的某个端点作为startpoint
            # 入度：以该顶点为终点的连线的数量；出度：以该顶点为起点的连线的数量
            # 点共有三种情况
            #   1 在连线中间，入度为 1，出度为 1，两条连线同向；
            #   2 在连线一端，入度为 1，出度为 1，两条连线反向；
            #   3 在连线一端，入度为 2，出度为 2，入的两条连线反向，出的两条连线反向。
            #                    ↑           ↑
            # eg: 1. → * →    2. * ←    3. → * ←
            #                                ↓
            # 所以 出度为 2 时，是 3；出度为 1 时，根据出入的连线方向确定是 1 或 2
            # 2 满足要求的点，返回
            # 1, 3 在出的连线中选择一条继续走，直到到达 2 的状态
            start_x, start_y = next(iter(links))
            current_direction = None

            # 寻找当前点的入边方向
            for direction_x, direction_y in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                pre_point = start_x + direction_x, start_y + direction_y

                if pre_point not in links:
                    continue

                pre_direction = -direction_x, -direction_y
                if pre_direction in links[pre_point]:
                    current_direction = pre_direction
                    break

            while True:
                next_directions = links[(start_x, start_y)]

                next_direction = next_directions.copy().pop()
                match len(next_directions):
                    case 1:
                        if next_direction == current_direction:
                            # 情况1
                            start_x, start_y = start_x + next_direction[0], start_y + next_direction[1]
                            continue
                        # 情况 2
                        return start_x, start_y
                    case 2:
                        # 情况 3
                        start_x, start_y = start_x + next_direction[0], start_y + next_direction[1]
                        current_direction = next_direction
                    case _:
                        raise

        while links:
            start = choose_start()

            rounts.append(rount := [start])

            next_point = start

            while True:
                # print(f'{next_point=} {start=}')
                current = next_point

                direction = links[current].pop()
                if not links[current]:
                    links.pop(current)

                next_point = current[0] + direction[0], current[1] + direction[1]

                if next_point == start:
                    break

                if next_point not in links:
                    raise ValueError(f'连线不能形成回路，{next_point=}, {links=}')

                if direction not in links[next_point]:
                    rount.append(next_point)
        return rounts

    def convert_path(self) -> dict[int, list[str]]:
        """将路径转为 svg 的 path 元素的 d 属性值，出现嵌套时需搭配 fill-rule evenodd 正确显示"""
        for ele_id, single_edges in self.edges.items():
            self.paths[ele_id] = (single_paths := [])
            for edge in single_edges:
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
                single_paths.append(''.join(path))

        return self.paths


class Map:
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

    svg_attr_common = {
        'stroke-width': '0',
        'stroke-linejoin': "round",
        'stroke-linecap': "round",  # butt round square  无 圆角 方角
    }

    def __init__(self, map_data: list[Union[int, Union[list[int], tuple[int]]]], width: int = None, height: int = None,
                 is_flipped: bool = False):
        self.width: int = 0
        self.height: int = 0

        self.map_data: list[[list[int]]] = map_data

        self._format_data(width, height)

        path = Path()
        self.edges = path.load_map(self.map_data, is_flipped)
        self.paths = path.convert_path()

        self.svg: Svg = Svg(width=self.width, height=self.height, **self.svg_attr_common)
        self._root: et.Element = self.svg.root
        self._g: dict[int, et.Element] = self.svg.g

    def _format_data(self, width: int = None, height: int = None):
        if not self.map_data:
            raise ValueError('传入地图数据为空')
        if isinstance(self.map_data[0], int):
            map_data_len = len(self.map_data)
            if width is None:
                if height is None:
                    width = height = int(map_data_len ** 0.5)
                    if width * height != map_data_len:
                        raise ValueError(
                            f'未传入宽高，且 map_data 表示的地图不是正方形 {width=} {height=} {map_data_len=}')
                else:
                    width = map_data_len // height
            if height is None:
                height = map_data_len // width
            if width * height != map_data_len:
                raise ValueError(f'宽高数据与 map_data 表示的地图不符 {width} x {height} != {len(self.map_data)}')
            self.width = width
            self.height = height
            self.map_data = [self.map_data[i * self.height: (i + 1) * self.height] for i in range(self.width)]
        elif isinstance(self.map_data[0], (list, tuple)):
            self.width = len(self.map_data[0])
            self.height = len(self.map_data)

            if (width or height) and (self.width != width or self.height != height):
                log.warning(f'传入宽高 {width=}, {height=} 与图数据不符，已更正为 width={self.width}, height={self.height}')
        else:
            raise TypeError('传入地图数据格式错误')

    def get_priority(self):
        # 根据地皮优先级列表，首先生成低优先级的，再生成高优先级的覆盖，用来实现不同优先级地皮间的覆盖效果
        return sorted(list(self.paths))

    def get_tile_names(self):
        return {i: str(i) for i in self.get_priority()}

    def get_tile_colors(self):
        tile_colors = {}
        colors = []
        for tile_code in self.paths:
            if not colors:
                colors = self.svg_colors.copy()
                shuffle(colors)
            tile_colors[tile_code] = colors.pop()

        return tile_colors

    def save(self, save_path: str = 'map', get_io=False):
        tile_list = self.get_priority()
        tile_names = self.get_tile_names()
        tile_colors = self.get_tile_colors()

        for tile_code in tile_list:
            tile_name = tile_names[tile_code]
            if tile_name not in self._g:
                color = tile_colors.get(tile_name)
                # 通过边框实现地皮优先级覆盖会导致图形合并时连接的线也有边框，连接时避免同行同列，通过 M 命令连接可以避免
                self._g[tile_name] = et.SubElement(
                    self._root, 'g', {'id': f'g_{tile_name}',
                                      'stroke': color,
                                      # 'stroke-width': '0.25',  # 迁移到 svg 属性
                                      # 'stroke-linecap': "round",  # 迁移到 svg 属性
                                      # "stroke-linejoin": "round",  # 迁移到 svg 属性
                                      'fill': color})
            for path in self.paths[tile_code]:
                et.SubElement(self._g[tile_name], 'path', {'d': path})

        # 中心点
        # cx, cy = (self.width - 1) / 2 + 1, (self.height - 1) / 2 + 1
        # et.SubElement(self.root, 'path', {'stroke': 'red', 'stroke-width': '2', 'd': f'M{cx} {cy}Z'})

        return self.svg.save(save_path, get_io)


class Tiles(Map):
    svg_attr_common = {
        'stroke-width': '0.3',
        'stroke-linejoin': "round",
        'stroke-linecap': "round",  # butt round square  无 圆角 方角
    }
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

    def __init__(self, map_data: list[Union[int, Union[list[int], tuple[int]]]], tile_id_name: dict = None, is_flipped: bool = True):
        super().__init__(map_data, is_flipped=is_flipped)

        if tile_id_name is not None:
            self.tile_names = {j: i for i, j in tile_id_name.items()}
        else:
            log.warning('未传入地皮名与地皮编号对应的关系，将使用预存的对应关系，对应关系并不一定准确')
            self.tile_names = self.tiles_cache

    def get_tile_names(self):
        for i in self.paths:
            if i not in self.tile_names:
                self.tile_names[i] = str(i)
        return self.tile_names

    def get_tile_colors(self):
        colors = []
        tile_names = self.get_tile_names()
        for i in self.paths:
            i = tile_names[i]
            if i not in self.colors:
                if not colors:
                    colors = self.svg_colors.copy()
                    shuffle(colors)
                color = colors.pop()
                log.warning(f'{i} 没有对应的颜色，已选取随机颜色：{color}')
                self.colors[str(i)] = color
        return self.colors

    def get_priority(self):
        return sorted(list(self.paths), key=lambda x: self.priority.get(self.tiles_cache.get(x), 0))


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
    map_data = [
        [1, 0, 1, 1, 1, 1],
        [0, 0, 1, 0, 1, 0],
        [1, 1, 1, 0, 1, 0],
        [1, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 1, 0],
        [1, 1, 1, 0, 1, 0],
        [1, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1],
    ]
    log.info('创建地图实例')
    map_ = Tiles(map_data)
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
    map_ = Tiles(tile_decode, name_id_map)
    log.info('保存地图')
    map_.save(f'map_{datatype}.svg')

    print(time() - start_time)


if __name__ == '__main__':
    main()
    # test_map()
    pass

"""
游戏内，地皮坐标轴正向是和地图坐标系一致的，在屏幕逆时针旋转 45° 后，向下是x(0, )的正向，向右是y(, 0)的正向
但保存的游戏数据是按列保存的，先第一列，再第二列以此类推，因此该处构造的坐标系轴方向是与游戏内对调的，x, y -> y, x
但该处构造的坐标系与 svg 坐标系轴方向是一致的，因此虽然 svg 中显示方向与游戏内一致，但其 x,y 值是互换的，不可以直接用

游戏内默认方向 两个坐标体系
1 以地皮排列为基础构建的坐标系，默认上方指向 地皮的零点(0, 0)。向上走 x,y 逐渐减小，最小为(0, 0)  425*425 x,y ∈[0,424]
425*425 游戏内显示实际长度是 426  除去(0~424)，(0, 0)后面还有一个(0, 0)，这一行一列的地皮也是impassable，426*426范围外则是invalid，invalid上创建新实体时游戏会崩溃  两个(0, 0)都越过之后，开始负值计数
2 以地图中心为原点构建的坐标系，默认上方指向 x, y 轴的负方向
按 q 将屏幕逆时针旋转 45° 后，左上为地皮原点(0, 0)，  地图中心右下方半个地皮为坐标原点，下方为 x 轴正向，右为 y 轴正向

下方地皮坐标默认以地皮左上角的坐标为原点，方便换算
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
