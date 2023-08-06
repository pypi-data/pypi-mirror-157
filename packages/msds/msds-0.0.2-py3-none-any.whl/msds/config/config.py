# 交易所：名称列表
EXCHANGE_LIST = [
    'binance',
    'okx',
    'huobi'
]

# 交易所：请求条数限制
EXCHANGE_LIMIT = {
    'binance': None,
    'okx': None,
    'huobi': 2000
}

# 币种：标识列表
SYMBOL_LIST = [
    'BTC/USDT',
    'ETH/USDT',
    'SHIB/USDT',
    'ATOM/USDT',
    'EOS/USDT',
    'XRP/USDT',
    'XEM/USDT',
    'BCH/USDT',
    'DOT/USDT',
]

# 蜡烛图：时间间隔
CANDLE_INTERVAL = [
    '1m',
    '3m',
    '5m',
    '30m',
    '1h',
    '2h',
    '4h',
    '6h',
    '12h',
    '2d',
    '7d',
    '1M'
]

# 蜡烛图：数据列的含义名称
CANDLE_DATA_COL_NAME = {
    0: 'candle_begin_time',
    1: 'open',
    2: 'high',
    3: 'low',
    4: 'close',
    5: 'volume'
}

# 网络请求：最大重试次数
MAX_RETRY_NUMBER = 3

# 网络请求：重试等待间隔
MAX_RETRY_WAIT = 2
