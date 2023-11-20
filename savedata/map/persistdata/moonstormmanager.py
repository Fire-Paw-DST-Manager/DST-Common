# -*- coding: utf-8 -*-
from typing import Union, Literal

from pydantic import BaseModel


class Moonstormmanager(BaseModel):

    # 月亮风暴已循环次数
    _alterguardian_defeated_count: int

    # 遇到过风暴中科学家的玩家列表
    metplayers: Union[dict[str, Literal[False]]]
    stormdays: int


