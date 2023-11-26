import calendar
from datetime import datetime
from urllib import request
import pandas as pd
import re

# 获取股指期货,估值期权交割日
def getLastDay(year: int, month: int) -> str:
    c = calendar.Calendar(firstweekday=calendar.SUNDAY)
    monthcal = c.monthdatescalendar(year, month)
    third = [day for week in monthcal for day in week if \
             day.weekday() == calendar.FRIDAY and \
             day.month == month][2]
    return datetime.strptime(str(third), '%Y-%m-%d')
    # return third


def getMultiStockPrices(codeString):
    response = request.urlopen('http://qt.gtimg.cn/q=s_' + codeString)
    result = response.read().decode('gbk')
    all_indexes = result.split(';')
    # all_indexes_price = pd.Series()

    all_indexes_price_list = []
    for index in all_indexes:
        index = index.replace("\n", "")
        if index is not None and len(index) > 0:
            index_key_values = index.split('=')
            if len(index_key_values) > 1:
                index_values = re.sub('"', '', index_key_values[1])
                if index_values is not None and len(index_values) > 0:
                    index_name = index_values.split('~')[2]
                    index_price = index_values.split('~')[3]
                    # all_indexes_price[index_name] = float(index_price)
                    all_indexes_price_list.append(float(index_price))
    # return all_indexes_price
    return all_indexes_price_list

if __name__ == '__main__':
    # symbolStr = 'im2208'
    # print(int(symbolStr[2:4]))
    # print(int(symbolStr[4:6]))
    # year, month = int('20' + symbolStr[-4:-2]), int(symbolStr[-2:])
    # lstDate = getLastDay(year, month)
    #
    # # datestr = getLastDay(int(contract[2:4]), int(contract[4:6]))
    # print(lstDate)

    index_prices_list = getMultiStockPrices('sh000300,sh000852')
    print(index_prices_list)
