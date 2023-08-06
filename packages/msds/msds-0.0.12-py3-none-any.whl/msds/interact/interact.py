import click # 创建命令行工具
import inquirer # 通用交互命令行用户界面的集合
from msds.config.config import EXCHANGE_LIST, SYMBOL_LIST, CANDLE_INTERVAL # 常量配置

def userAnswerData():
    # 交互获取数据
    answer = inquirer.prompt([
        inquirer.List('exchange', message='请选择交易数据来源：', choices = EXCHANGE_LIST),
        inquirer.List('symbol', message='请选择币种名称：', choices = SYMBOL_LIST),
        inquirer.List('timeInterval', message='请选择数据间隔：', choices= CANDLE_INTERVAL),
    ])
    timeStart = click.prompt('请输入开始时间, YYYY-MM-DD', type=str)
    timeEnd = click.prompt('请输入结束时间, YYYY-MM-DD', type=str)
    click.clear()

    # 确认并返回
    tips = '确认通过 '+answer['exchange']+' 来请求 '+timeStart+' 到 '+timeEnd+' 之间的 '+answer['symbol']+' '+answer['timeInterval']+' 的数据吗'
    if click.confirm(tips):
        return answer['exchange'], answer['symbol'], timeStart+' 00:00:00', timeEnd+' 00:00:00', answer['timeInterval']
    userAnswerData()
