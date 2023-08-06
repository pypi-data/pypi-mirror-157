import os
import re
import ccxt

# 递归创建文件夹
def makedirs(path):
    if os.path.exists(path) is False: 
        os.makedirs(path)

# 获取时间周期的秒数
def getIntervalSeconds(s):
    timeMap = {
        'm': 60,
        'h': 60 * 60,
        'd': 60 * 60 * 24
    }
    regResult = re.findall(r'[0-9]+|[a-z]+', s)
    seconds = int(regResult[0]) * int(timeMap[regResult[1]])
    return seconds

# 获取交易所实例
def getExchangeInstance(s):
    if s == 'binance':
        return ccxt.binance()
    if s == 'okx':
        return ccxt.okx()
    if s == 'huobi':
        return ccxt.huobi()