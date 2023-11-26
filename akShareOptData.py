# import akshare as ak
from akshare import option_finance_board
from akshare import option_value_analysis_em
from urllib import request
from datetime import datetime


# import pandas as pd
# import time

def get_ETF_price(code):
    response = request.urlopen('http://qt.gtimg.cn/q=' + code)
    # print(response.read().decode('utf-8'))
    result = response.read().decode('gbk')
    valueString = result.split('=')[1]
    valueArray = valueString.split('~')
    price = valueArray[3]
    return price


# 根据合约代码生成合约名称
# def get_contact_name(contact_code):
#     name = ''
#     if contact_code[:6] == '510050':
#         name = name + '50ETF'
#     elif contact_code[:6] == '510300':
#         name = name + '300ETF'
#     if contact_code[6:7] == 'C':
#         name = name + '购'
#     elif contact_code[6:7] == 'P':
#         name = name + '沽'
#     month = int(contact_code[9:11])
#     monthStr = str(month) + '月'
#     name = name + monthStr
#     return name + contact_code[-4:]

def get_contact_name(contact_code, price):
    print(contact_code[:6])
    name = ''
    if contact_code[:6] == '510050':
        name = name + '50ETF'
    elif contact_code[:6] == '510300':
        name = name + '300ETF'

    print(contact_code[6:7])
    if contact_code[6:7] == 'C':
        name = name + '购'
    elif contact_code[6:7] == 'P':
        name = name + '沽'

    print(contact_code[9:11])
    month = int(contact_code[9:11])
    monthStr = str(month) + '月'
    name = name + monthStr

    return name + str(round(price * 1000))


# 嘉实沪深300ETF期权
# 华夏上证50ETF期权,sh510050
def getMergeOption(etfName, etfCode, expDateString):
    # 到期时间格式转换
    expDate = datetime.strptime(expDateString, '%Y-%m-%d')
    expDateList = expDateString.split("-")

    # 获取期权数据
    df = option_finance_board(symbol=etfName, end_month=expDateList[0] + expDateList[1])

    df = df.sort_values(by=['行权价', '合约交易代码'], ascending=(True, True))
    print(df[['行权价', '合约交易代码']])
    df.index = range(len(df))

    # df.to_excel('etf_opt.xlsx')

    # 获取ETF当前价格
    eftPrice = get_ETF_price(etfCode)
    print('ETF价格{}'.format(eftPrice))

    df['标的名称'] = etfName
    # df['合约名称'] = df['合约交易代码'].apply(lambda x: get_contact_name(x))
    df['合约名称'] = df.apply(lambda x: get_contact_name(x.合约交易代码, x.行权价), axis=1)
    df['标的价格'] = eftPrice
    df['合成价值'] = 0.0
    df['折价率'] = 0.0
    df['剩余天数'] = 0
    df['年化折价率'] = 0
    df['合约类型'] = ''
    df['合约单位'] = 10000
    # df['对应市值'] = 10000

    print(df['合约名称'].values)
    optionNames = df['合约名称'].values
    print('-------------------')
    print(optionNames)
    print('-------------------')
    option_value_analysis_em_df = option_value_analysis_em()
    option_value_analysis_em_df = option_value_analysis_em_df[option_value_analysis_em_df.期权名称.isin(optionNames)]
    option_value_analysis_em_df = option_value_analysis_em_df.loc[:, ['期权名称', '隐含波动率']]
    print(option_value_analysis_em_df)

    dict1 = dict(zip(option_value_analysis_em_df['期权名称'], option_value_analysis_em_df['隐含波动率']))

    print(dict1)
    # df['隐含波动率'] = df['合约名称'].apply(lambda x: dict1[x])
    df['隐含波动率'] = df['合约名称'].apply(lambda x: dict1.get(x))

    # print(option_value_analysis_em_df.head())

    # print(df.index)
    # print(eftPrice)
    # today = datetime.date.today()
    today = datetime.today()

    for i, row in df.iterrows():
        df.loc[i, '涨跌幅'] = str(df.loc[i, '涨跌幅']) + '%'
        if i % 2 == 0:
            df.loc[i, '合约类型'] = "认购"
            #认沽期权 - 认购期权
            priceGap = df.loc[i + 1, '当前价'] - df.loc[i, '当前价']
            # 内在价值
            interValue = float(eftPrice) - df.loc[i, '行权价']
            # 合成价值(多头)
            #mergeValue = priceGap + interValue - 0.0003 - 0.0002
            # 合成价值(空头)
            mergeValue = priceGap + interValue + 0.0003 + 0.0007  # 加上滑点和手续费
            # print("行权价:"+str(df.loc[index, '行权价'])+"价差："+format(priceGap, '.4')+"隐含价值："+format(interValue, '.4'))
            df.loc[i, '合成价值'] = format(mergeValue, '.4')
            discount = mergeValue / float(eftPrice)
            df.loc[i, '折价率'] = format((discount), '.3%')
            df.loc[i, '剩余天数'] = (expDate - today).days
            yearlyDiscount = (discount / df.loc[i, '剩余天数']) * 365
            df.loc[i, '年化折价率'] = format((yearlyDiscount), '.3%')
        else:
            df.loc[i, '合约类型'] = "认沽"
    # df.to_excel("华夏上50ETF期权.xlsx")
    print(df)
    return df


if __name__ == '__main__':
    # option_sse_list_sina_df = ak.option_sse_list_sina(symbol="50ETF", exchange="null")
    # print(option_sse_list_sina_df)

    # sz50_df = ak.option_finance_board(symbol="华夏上证50ETF期权", end_month="2305")
    # hs300_df = ak.option_finance_board(symbol="嘉实沪深300ETF期权", end_month="2303")
    # zz500_df = ak.option_finance_board(symbol="南方中证500ETF", end_month="2305")
    # print(zz500_df)

    getMergeOption('华夏上证50ETF期权', 'sh510050', '2023-06-28')
