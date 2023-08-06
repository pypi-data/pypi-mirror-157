from msds.config.config import MAX_RETRY_NUMBER, MAX_RETRY_WAIT
from tenacity import retry, stop_after_attempt, wait_fixed

# 网络请求通用重试、错误重试的请求等待（重试3次 * 每次15秒超时 + 2 * 2秒等待，共计50秒超时时间）
COMMON_RETRY_NUMBER = stop_after_attempt(MAX_RETRY_NUMBER)
COMMON_RETRY_WAIT = wait_fixed(MAX_RETRY_WAIT)

# 重试装饰器
@retry(stop=COMMON_RETRY_NUMBER)
def getOhlcv(exchangeInstance, symbol, timeframe, since, limit):
    data = exchangeInstance.fetch_ohlcv(symbol, timeframe, since, limit)
    return data
