# import akshare as ak
from akshare import option_cffex_zz1000_list_sina
from akshare import option_cffex_hs300_list_sina
from akshare import option_cffex_sz50_list_sina

from akshare import option_cffex_sz50_spot_sina
from akshare import option_cffex_hs300_spot_sina
from akshare import option_cffex_zz1000_spot_sina

from akshare import stock_zh_index_spot
# import pandas as pd
import numpy as np

# option_finance_board_df = ak.option_finance_board(symbol="沪深300股指期权", end_month="2208")
# option_finance_board_df = ak.option_finance_board(symbol="中证1000股指期权", end_month="2208")
# print(option_finance_board_df)
from pandas import DataFrame


def get_zz1000_index_contracts():
    option_cffex_zz1000_list_sina_df = option_cffex_zz1000_list_sina()
    zz1000_index_contracts = option_cffex_zz1000_list_sina_df['中证1000指数']
    # print(zz1000_index_contracts)
    return np.sort(zz1000_index_contracts)


def get_hs300_index_contracts():
    option_cffex_hs300_list_sina_df = option_cffex_hs300_list_sina()
    hs300_index_contracts = option_cffex_hs300_list_sina_df['沪深300指数']
    return np.sort(hs300_index_contracts)

def get_sz50_index_contracts():
    option_cffex_hs50_list_sina_df = option_cffex_sz50_list_sina()
    hs50_index_contracts = option_cffex_hs50_list_sina_df['上证50指数']
    return np.sort(hs50_index_contracts)

# def get_index_contracts():
#     option_cffex_hs300_list_sina_df = ak.option_cffex_hs300_list_sina()
#     print(option_cffex_hs300_list_sina_df)
#     option_cffex_zz1000_list_sina_df = ak.option_cffex_zz1000_list_sina()
#     print(option_cffex_zz1000_list_sina_df)

# get three index current price
def get_index_prices():
    stock_zh_index_spot_df = stock_zh_index_spot()
    index_codes = ['sh000016', 'sh000300', 'sh000852']
    stock_zh_index_spot_df = stock_zh_index_spot_df[stock_zh_index_spot_df.代码.isin(index_codes)]
    stock_zh_index_spot_df.reset_index(drop=True, inplace=True)
    print(stock_zh_index_spot_df.loc[0, '最新价'])
    print(stock_zh_index_spot_df.loc[1, '最新价'])
    print(stock_zh_index_spot_df.loc[2, '最新价'])


# get option prices by index_code,contract_code
def get_index_option_data(select_index_code, contract_code):
    if select_index_code == 'sh000016':
        return option_cffex_sz50_spot_sina(symbol=contract_code)
    elif select_index_code == 'sh000300':
        return option_cffex_hs300_spot_sina(symbol=contract_code)
    elif select_index_code == 'sh000852':
        return option_cffex_zz1000_spot_sina(symbol=contract_code)
    else:
        return None


def get_index_option_prices(index_price, contract_code, remaining_days, select_index_code):
    print(f'contract_code:{contract_code}')

    df = get_index_option_data(select_index_code, contract_code)

    df.rename(columns={'看涨合约-买量': 'call_buy_volume',
                       '看涨合约-买价': 'call_buy',
                       '看涨合约-最新价': 'call_buy_price',
                       '看涨合约-卖价': 'call_sell',
                       '看涨合约-卖量': 'call_sell_volume',
                       '看涨合约-持仓量': 'call_sell_volume_exist',
                       '看涨合约-涨跌': 'call_sell_price_chg',
                       '看涨合约-标识': 'call_code'}, inplace=True)

    df.rename(columns={'看跌合约-买量': 'put_buy_volume',
                       '看跌合约-买价': 'put_buy',
                       '看跌合约-最新价': 'put_buy_price',
                       '看跌合约-卖价': 'put_sell',
                       '看跌合约-卖量': 'put_sell_volume',
                       '看跌合约-持仓量': 'put_sell_volume_exist',
                       '看跌合约-涨跌': 'put_sell_price_chg',
                       '看跌合约-标识': 'put_code'}, inplace=True)

    df['opt_value'] = index_price - df['行权价']

    # 合成多头（买入认购+卖出认沽）
    df['long_mer_value'] = df['put_buy'] - df['call_sell'] + df['opt_value'] - (90.0 + 6.0) / 100.0
    df['long_dis'] = df['long_mer_value'] / index_price
    df['long_dis_annual'] = (df['long_dis'] / remaining_days) * 365

    # 合成空头（买入认沽+卖出认购）
    df['short_mer_value'] = df['call_buy'] - df['put_sell'] - df['opt_value'] - (90.0 + 6.0) / 100.0
    df['short_dis'] = df['short_mer_value'] / index_price
    df['short_dis_annual'] = (df['short_dis'] / remaining_days) * 365

    df[u'long_mer_value'] = df[u'long_mer_value'].apply(lambda x: format(x, '.5'))
    df[u'long_dis'] = df[u'long_dis'].apply(lambda x: format(x, '.3%'))
    df[u'long_dis_annual'] = df[u'long_dis_annual'].apply(lambda x: format(x, '.3%'))

    df[u'short_mer_value'] = df[u'short_mer_value'].apply(lambda x: format(x, '.5'))
    df[u'short_dis'] = df[u'short_dis'].apply(lambda x: format(x, '.3%'))
    df[u'short_dis_annual'] = df[u'short_dis_annual'].apply(lambda x: format(x, '.3%'))
    # df = df[heads]

    print(df)
    return df


# option_finance_board_df = option_finance_board(symbol="沪深300股指期权", end_month="2208")
# print(option_finance_board_df.loc[0, :])

# get_zz1000_index_contracts()
# get_hs300_index_contracts()

# get_index_prices()
# option_cffex_zz1000_spot_sina_df = option_cffex_zz1000_spot_sina(symbol="io2208")
# option_cffex_zz1000_spot_sina_df = option_cffex_zz1000_spot_sina(symbol="io2208")
# print(option_cffex_zz1000_spot_sina_df)
# zz1000_df = get_index_option_prices(7090.0027, 'mo2208', 9.0)
# try:
#     df = option_cffex_zz1000_spot_sina(symbol='mo2208')
#     print(df)
# except:
#     print('excption!')
# zz1000_df.to_csv('zz1000_df.csv', index=None)

if __name__ == '__main__':
    print('--main--')
    # print(__version__)
    option_cffex_sz50_list_sina_df = option_cffex_sz50_list_sina()
    option_cffex_sz50_spot_sina_df = option_cffex_sz50_spot_sina()
    print(option_cffex_sz50_list_sina_df)
    print(option_cffex_sz50_spot_sina_df)
    #
    # option_cffex_hs300_list_sina_df = option_cffex_hs300_list_sina()
    # option_cffex_spot_list_sina_df = option_cffex_hs300_spot_sina()
    # print(option_cffex_hs300_list_sina_df)
    # print(option_cffex_spot_list_sina_df)
    #
    # option_cffex_zz1000_list_sina_df = option_cffex_zz1000_list_sina()
    # option_cffex_zz1000_spot_sina_df = option_cffex_zz1000_spot_sina()
    # print(option_cffex_zz1000_list_sina_df)
    # print(option_cffex_zz1000_spot_sina_df)

