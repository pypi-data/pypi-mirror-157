#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from rich import print
ROOT_PATH = os.path.join(sys.path[0], '../')
sys.path.append(ROOT_PATH)

import click
import shutil
import importlib
import configparser
from msds.interact import interact
from msds.core.getBackTest import go_back_test
from msds.core.getCandleData import save_spot_candle_data_from_exchange

config = configparser.ConfigParser()
config.read([os.path.join(os.getcwd(), 'msds.ini')])

# ------------------------------ 命令定义 ------------------------------
@click.group()
def msds():
    pass

@msds.command()
def init():
    origin_main = os.path.join(sys.path[-2], 'msds/template/main.py')
    target_main = os.path.join(os.getcwd(), 'main.py')
    origin_conf = os.path.join(sys.path[-2], 'msds/template/msds.ini.py')
    target_conf = os.path.join(os.getcwd(), 'msds.ini')
    origin_init = os.path.join(sys.path[-2], 'msds/template/__init__.py')
    target_init = os.path.join(os.getcwd(), '__init__.py')

    if not os.path.exists(origin_init):
        print('[bold red]默认初始化文件读取失败[/bold red]')
    if not os.path.exists(origin_main):
        print('[bold red]默认策略文件读取失败[/bold red]')
    if not os.path.exists(origin_conf):
        print('[bold red]默认配置文件读取失败[/bold red]')

    if not os.path.exists(target_init):
        shutil.copyfile(origin_init, target_init)
        print('[bold green]初始化文件创建成功[/bold green]')
    if not os.path.exists(target_main):
        shutil.copyfile(origin_main, target_main)
        print('[bold green]策略文件创建成功[/bold green]')
    if not os.path.exists(target_conf):
        shutil.copyfile(origin_conf, target_conf)
        print('[bold green]配置文件创建成功[/bold green]')

@msds.command()
def data():
    if not bool(config.has_section('CANDLE_DATA')):
        exchange, symbol, time_start, time_end, time_interval = interact.userAnswerData()
        save_spot_candle_data_from_exchange(exchange, symbol, time_start, time_end, time_interval)
    candleConfig = config['CANDLE_DATA']
    return save_spot_candle_data_from_exchange(
        candleConfig['exchange'],
        candleConfig['symbol'],
        candleConfig['time_start'],
        candleConfig['time_end'],
        candleConfig['time_interval']
    )

@msds.command()
def backtest():
    if not bool(config.has_section('BACK_TEST')):
        return
    BackTestConfig = config['BACK_TEST']

    # 配置引入
    strategy_name = BackTestConfig['strategy_name'] or 'main'
    strategy_path = BackTestConfig['strategy_path'] or os.getcwd()
    sys.path.append(strategy_path)
    strategy = importlib.import_module(strategy_name)
    go_back_test(
        strategy,
        eval(BackTestConfig['strategy_param']),
        BackTestConfig['strategy_time'],
        BackTestConfig['data_path'],
        BackTestConfig.getint('symbol_face_value'),
        BackTestConfig.getfloat('service_charge'),
        BackTestConfig.getfloat('slippage'),
        BackTestConfig.getint('leverage_rate'),
        BackTestConfig.getfloat('min_margin_ratio'),
    )

@msds.command()
def test():
    pass

# ------------------------------ 服务入口 ------------------------------

def main():
    msds()

# 描述：只有脚本执行的方式时运行main函数
# case1、当该模块被直接执行时：__name__ 等于文件名（包含后缀 .py ）
# case2、当该模块 import 到其他模块中： __name__ 等于模块名称（不包含后缀.py）
if __name__ == '__main__':
    main()
