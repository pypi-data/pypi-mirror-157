[DEFAULT]

# K线数据配置
[CANDLE_DATA]
exchange = binance
symbol = ATOM/USDT
time_start = 2020-04-27 00:00:00
time_end = 2022-07-02 00:00:00
time_interval = 5m

# 策略回测配置
[BACK_TEST]
strategy_name = strategy
strategy_path = /Users/zhanyongdong/Desktop/mycode/testmodule
strategy_time = 5T
data_path = /Users/zhanyongdong/Desktop/mycode/msds/data/binance/SHIB-USDT/5m/2021-05-10_2022-07-02/binance_SHIB-USDT_5m_2021-05-10_2022-07-02.h5
symbol_face_value = 100000
service_charge = 0.0005
slippage = 0.001
leverage_rate = 3
min_margin_ratio = 0.01
