import os
import pandas as pd;
from time import sleep
from math import ceil
from rich import print
from rich.progress import Progress
from msds.base.request import getOhlcv
from msds.base.util import makedirs, getIntervalSeconds, getExchangeInstance
from msds.config.config import EXCHANGE_LIMIT, CANDLE_DATA_COL_NAME

pd.set_option('expand_frame_repr', False)

def save_spot_candle_data_from_exchange(exchange, symbol, start_time_string, end_time_string, time_interval):
    exchangeInstance = getExchangeInstance(exchange)

    # 时间定义：毫秒时间戳、时间对象
    end_time = pd.to_datetime(end_time_string)
    start_time = pd.to_datetime(start_time_string)
    end_time_stamp_ms =  exchangeInstance.parse8601(end_time_string)
    start_time_stamp_ms = exchangeInstance.parse8601(start_time_string)

    # 变量定义
    df_list = []
    process_length = ceil((((end_time_stamp_ms - start_time_stamp_ms) / 1000) / getIntervalSeconds(time_interval)) / 500)

    # 请求数据
    with Progress() as progress:
        task1 = progress.add_task('[bold red]【下载数据】: ', total=process_length)
        while True:
            try:
                df_item = getOhlcv(exchangeInstance, symbol, time_interval, start_time_stamp_ms, EXCHANGE_LIMIT[exchangeInstance.id])
            except:
                progress.update(task1, visible=False)
                print('[bold red]【请求失败】: [/bold red]请检查网络和参数后重试')
                return
            # 格式处理
            df_item = pd.DataFrame(df_item, dtype=float)
            df_list.append(df_item)
            progress.update(task1, advance=1)

            # 分页判断
            df_item_time = pd.to_datetime(df_item.iloc[-1][0], unit='ms')
            start_time_stamp_ms = exchangeInstance.parse8601(str(df_item_time))
            if df_item_time >= end_time or df_item.shape[0] <= 1:
                progress.update(task1, visible=False)
                break
            sleep(1)

    # 数据合并
    df = pd.concat(df_list, ignore_index=True)

    # 内容调整：时间信息格式转化，将所有列重命名
    df[0] = pd.to_datetime(df[0], unit='ms')
    df.rename(columns=CANDLE_DATA_COL_NAME, inplace=True)

    # 去重排序
    df.drop_duplicates(subset='candle_begin_time', keep='last', inplace=True)
    df.sort_values('candle_begin_time', inplace=True)    
    df.reset_index(drop=True, inplace=True)
    df = df[(df['candle_begin_time'] >= start_time) & (df['candle_begin_time'] < end_time)]

    # 定义名称：数据文件夹名称 & 文件名称
    dataNameDir = '{}/{}/{}/{}'.format(
        exchangeInstance.id,
        symbol.replace('/', '-'),
        time_interval,
        str(start_time.date())+'_'+str(end_time.date())
    )
    dataNameFile = dataNameDir.replace('/', '_')

    # 创建文件：系统实际存储文件夹、文件
    absolute_path = os.path.join(os.getcwd(), dataNameDir)
    makedirs(absolute_path)
    df.to_csv(os.path.join(absolute_path, dataNameFile + '.csv'), index=False)
    df.to_hdf(os.path.join(absolute_path, dataNameFile + '.h5'), key="df", mode="w", index=False)
    print('[bold green]【存储成功】: [/bold green]' + absolute_path)
