# -*- coding: utf-8 -*-

from pydantic import BaseModel


class WagpunkManager(BaseModel):

    # 距离废弃垃圾刷新的时间   旧的被敲才会有这个，时间是 4 - 7 天
    nextspawntime: float = None

    # 距离下次提示废弃垃圾位置的剩余时间   初始时间随提示次数由 15 -> 5 天，每次缩短一天
    nexthinttime: float = None

    # 沃格斯塔夫提示过废弃垃圾位置的次数
    hintcount: int = None

    # 最近一次废弃垃圾刷新位置所在的 nodeid，下次刷新会远离该 node 300 单位
    currentnodeindex: int
