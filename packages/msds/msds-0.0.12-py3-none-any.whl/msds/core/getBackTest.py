import pandas as pd
from msds.func.Signals import *
from msds.func.Position import *
from msds.func.Evaluate import *
from rich.progress import Progress
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行

def go_back_test(strategy, rule_type, data_path, face_value, c_rate, slippage, leverage_rate, min_margin_ratio):
    # =====读入数据
    df = pd.read_hdf(data_path, key='df')
    # 任何原始数据读入都进行一下排序、去重，以防万一
    df.sort_values(by=['candle_begin_time'], inplace=True)
    df.drop_duplicates(subset=['candle_begin_time'], inplace=True)
    df.reset_index(inplace=True, drop=True)


    # =====转换为其他分钟数据
    period_df = df.resample(rule=rule_type, on='candle_begin_time', label='left', closed='left').agg(
        {'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })
    period_df.dropna(subset=['open'], inplace=True)  # 去除一天都没有交易的周期
    period_df = period_df[period_df['volume'] > 0]  # 去除成交量为0的交易周期
    period_df.reset_index(inplace=True)
    df = period_df[['candle_begin_time', 'open', 'high', 'low', 'close', 'volume']]
    df = df[df['candle_begin_time'] >= pd.to_datetime('2021-6-01')]
    df = df[df['candle_begin_time'] < pd.to_datetime('2021-9-30')]
    df.reset_index(inplace=True, drop=True)


    # =====计算交易信号
    param = strategy.testParam()
    if not type(param[0]) == list:
        df = strategy.test(df, param)
        # =====计算实际持仓
        df = position_for_OKEx_future(df)
        df = equity_curve_for_OKEx_USDT_future_next_open(df, slippage=slippage, c_rate=c_rate, leverage_rate=leverage_rate,
                                                        face_value=face_value, min_margin_ratio=min_margin_ratio)
        return print('策略最终收益：', df.iloc[-1]['equity_curve'])

    rtn = pd.DataFrame()
    with Progress() as progress:
        task1 = progress.add_task('[bold green]【回测进度】: ', total=len(param))
        for item in param:
            _df = df.copy()
            # 计算交易信号
            _df = strategy.test(_df, item)
            _df = position_for_OKEx_future(_df)
            _df = equity_curve_for_OKEx_USDT_future_next_open(_df, slippage=slippage, c_rate=c_rate, leverage_rate=leverage_rate,
                                                            face_value=face_value, min_margin_ratio=min_margin_ratio)
            r = _df.iloc[-1]['equity_curve']
            rtn.loc[str(item), 'equity_curve'] = r
            progress.update(task1, advance=1)
        progress.update(task1, visible=False)
        print('[bold green]数据整理中...')
        rtn.sort_values(by='equity_curve', ascending=False, inplace=True)
    print(rtn)