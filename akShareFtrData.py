# import akshare as ak
from akshare import futures_comm_info
from akshare import futures_zh_spot
from urllib import request
import re
import pandas as pd
import calendar
from datetime import datetime

#获取现货价格
def getMultiStockPrices(codeString):
    response = request.urlopen('http://qt.gtimg.cn/q=s_' + codeString)
    result = response.read().decode('gbk')
    all_indexes = result.split(';')
    all_indexes_price = pd.Series()
    for index in all_indexes:
        index = index.replace("\n", "")
        if index is not None and len(index) > 0:
            index_key_values = index.split('=')
            if len(index_key_values) > 1:
                index_values = re.sub('"', '', index_key_values[1])
                if index_values is not None and len(index_values) > 0:
                    index_name = index_values.split('~')[2]
                    index_price = index_values.split('~')[3]
                    all_indexes_price[index_name] = float(index_price)
    return all_indexes_price

#获取股指期货交割日
def getLastDay(year: int, month: int) -> str:
    c = calendar.Calendar(firstweekday=calendar.SUNDAY)
    monthcal = c.monthdatescalendar(year, month)
    third = [day for week in monthcal for day in week if \
             day.weekday() == calendar.FRIDAY and \
             day.month == month][2]
    return datetime.strptime(str(third), '%Y-%m-%d')
    # return third


def getFutureList() -> pd.DataFrame:
    # get index prices
    indexPrices = getMultiStockPrices('sz399905,sz399300,sh000016,sh000852')
    print(f'indexPrices:{indexPrices}')
    # get future code list
    futures_comm_info_df = futures_comm_info(symbol='中国金融期货交易所')
    # splitMark = ","
    print(futures_comm_info_df)
    # merger future code to a string by comma
    codeStr = ''
    for i, v in futures_comm_info_df['合约代码'].items():
        if re.match('IC|IF|IH|IM[0-9]{4}$', v):
            codeStr = codeStr + v + ','

    # drop last comma
    futCodesStr = codeStr[:-1]
    print(futCodesStr)

    # get future data from akshare
    futures_zh_spot_df = futures_zh_spot(symbol=futCodesStr, market="CFFEX", adjust='0')
    # print(futures_zh_spot_df)

    # add some columns
    futures_zh_spot_df['index_price'] = 0.0
    futures_zh_spot_df['price_per_index'] = 0
    futures_zh_spot_df['total_cap'] = 0.0
    futures_zh_spot_df['last_day'] = ''
    futures_zh_spot_df['rem_days'] = 0
    futures_zh_spot_df['gap_bt'] = 0.0
    futures_zh_spot_df['days_bt'] = 0

    # 按照代号排序
    futures_zh_spot_df.sort_values(by='symbol', axis=0, ascending=True, inplace=True)
    futures_zh_spot_df.reset_index(inplace=True)

    for index, row in futures_zh_spot_df.iterrows():
        symbolStr = row['symbol']
        print(symbolStr)
        year, month = int('20' + symbolStr[-4:-2]), int(symbolStr[-2:])
        lstDate = getLastDay(year, month)
        # print(lstDate)
        # print(type(lstDate))
        today = datetime.today()
        futures_zh_spot_df.loc[index, 'last_day'] = str(lstDate)[:10]
        futures_zh_spot_df.loc[index, 'rem_days'] = (lstDate - today).days + 1

        # 添加指数行情数据
        if re.match('中证500指数期货[0-9]{4}$', symbolStr):
            futures_zh_spot_df.loc[index, 'index_price'] = indexPrices['399905']
            futures_zh_spot_df.loc[index, 'price_per_index'] = 200
        if re.match('沪深300指数期货[0-9]{4}$', symbolStr):
            futures_zh_spot_df.loc[index, 'index_price'] = indexPrices['399300']
            futures_zh_spot_df.loc[index, 'price_per_index'] = 300
        if re.match('上证50指数期货[0-9]{4}$', symbolStr):
            futures_zh_spot_df.loc[index, 'index_price'] = indexPrices['000016']
            futures_zh_spot_df.loc[index, 'price_per_index'] = 300
        if re.match('中证1000指数期货[0-9]{4}$', symbolStr):
            futures_zh_spot_df.loc[index, 'index_price'] = indexPrices['000852']
            futures_zh_spot_df.loc[index, 'price_per_index'] = 200

    # print('----------------futures_zh_spot_df 2-----------------')
    # print(futures_zh_spot_df)
    # print('----------------futures_zh_spot_df 2-----------------')

    #合约总数
    totalContract = len(futures_zh_spot_df)

    #指数种类
    contractType = 4

    #每个指数对应的合约数量
    countPerContract = totalContract/contractType

    for index, row in futures_zh_spot_df.iterrows():
        # gap between 2 contract
        print('-----------start----------------')
        symbol=row['symbol']
        print(f'index:{index} symbol:{symbol}')
        #如果不是最后一个合约，算出移仓到下一个合约的收益率
        if (index + 1) % countPerContract > 0:
            thisPPrice, nextPPrice = futures_zh_spot_df.loc[index, 'current_price'], futures_zh_spot_df.loc[index + 1, 'current_price']
            futures_zh_spot_df.loc[index, 'gap_bt'] = thisPPrice - nextPPrice

            thisRDays = futures_zh_spot_df.loc[index, 'rem_days']
            nextRDays = futures_zh_spot_df.loc[index + 1, 'rem_days']
            print(f'thisRDays:{thisRDays},nextRDays:{nextRDays}')
            futures_zh_spot_df.loc[index, 'days_bt'] = nextRDays - thisRDays
        print('-------------end--------------')


    futures_zh_spot_df['gap'] = futures_zh_spot_df['index_price'] - futures_zh_spot_df['current_price']
    futures_zh_spot_df['dis'] = futures_zh_spot_df['gap'] / futures_zh_spot_df['index_price']
    futures_zh_spot_df['y_dis'] = (futures_zh_spot_df['dis'] / futures_zh_spot_df['rem_days']) * 365

    futures_zh_spot_df['gap'] = futures_zh_spot_df['gap'].apply(lambda x: format(x, '.4'))
    futures_zh_spot_df['dis'] = futures_zh_spot_df['dis'].apply(lambda x: format(x, '.3%'))
    futures_zh_spot_df['y_dis'] = futures_zh_spot_df['y_dis'].apply(lambda x: format(x, '.3%'))

    futures_zh_spot_df['y_move'] = futures_zh_spot_df['gap_bt']/futures_zh_spot_df['index_price'] * (365/futures_zh_spot_df['days_bt'])
    futures_zh_spot_df['y_move'] = futures_zh_spot_df['y_move'].apply(lambda x: format(x, '.3%'))
    futures_zh_spot_df['gap_bt'] = futures_zh_spot_df['gap_bt'].apply(lambda x: format(x, '.2f'))

    futures_zh_spot_df['total_cap'] = futures_zh_spot_df['price_per_index'] * futures_zh_spot_df['current_price']

    # futures_zh_spot_df.sort_values(by='symbol', axis=0, ascending=True, inplace=True)
    futures_zh_spot_df.index = range(len(futures_zh_spot_df))
    return futures_zh_spot_df

if __name__ == "__main__":
    # print(ak.__version__)
    # futures_zh_spot_df = ak.futures_zh_spot(symbol='IC2209', market="FF", adjust='0')
    # futures_comm_info_df = ak.futures_comm_info(symbol='中国金融期货交易所')
    # futures_comm_info_df.to_csv('金融期货.csv',index=None)
    # print(futures_comm_info_df)

    futures_zh_spot_df = futures_zh_spot(symbol='IM2303', market="CFFEX", adjust='0')
    print(futures_zh_spot_df)
