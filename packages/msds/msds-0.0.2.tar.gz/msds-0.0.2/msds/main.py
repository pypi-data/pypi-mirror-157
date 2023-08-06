#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import click
from msds.interact import interact
from msds.core.getCandleData import save_spot_candle_data_from_exchange

# ------------------------------ 命令定义 ------------------------------
@click.group()
def msds():
    pass

@msds.command()
def data():
    exchange, symbol, timeStart, timeEnd, timeInterval = interact.userAnswerData()
    save_spot_candle_data_from_exchange(exchange, symbol, timeStart, timeEnd, timeInterval)
    # save_spot_candle_data_from_exchange(exchange, symbol, '2022-01-01 00:00:00', '2022-01-05 00:00:00', timeInterval)

# ------------------------------ 服务入口 ------------------------------

def main():
    msds()

# 描述：只有脚本执行的方式时运行main函数
# case1、当该模块被直接执行时：__name__ 等于文件名（包含后缀 .py ）
# case2、当该模块 import 到其他模块中： __name__ 等于模块名称（不包含后缀.py）
if __name__ == '__main__':
    main()
