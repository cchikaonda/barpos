# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      test2
# Author:    liangbaikai
# Date:      2020/1/17
# Desc:      there is a python file description
# ------------------------------------------------------------------

import time
from datetime import datetime

from cn.jsonfy.core import DateTimeDesc, BaseJsonModel, DictDesc


class Foo(BaseJsonModel):
    infos1 = DictDesc("infos1")
    up = DateTimeDesc("up", format='%Y-%m-%d')
    down = DateTimeDesc("down")


if __name__ == '__main__':
    f = Foo()
    _fake_time = datetime.now()
    f.up = _fake_time
    f.down = _fake_time
    _dict = {"key": "value"}
    f.infos1 = _dict

    print(f.toJson())
    f_obj = f.fromJson(f.toJson())
    print(f_obj)