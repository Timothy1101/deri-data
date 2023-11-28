import akshare as ak
import pandas as pd

COMMODITY_HEADS = ('合约名称', '当前价格', '买价',
                   '卖价', '买量', '卖量', '滑点',
                   '换月变化率', '换月价差',
                   '累计价差', '累计变化率', '月份差', '累计年化')

def get_date(start_year, start_month, symbol):
    end_year = int(symbol[-4:-2])
    end_month = int(symbol[-2:])
    res = (end_year - start_year) * 12 + (end_month - start_month)
    print('Difference between dates in months:', res)
    return res

def get_commodity_list_by_exchange(ex_name):
    futures_df_dalian = ak.futures_comm_info(symbol=ex_name)
    if ex_name == '郑州商品交易所':
        futures_df_dalian['代码'] = futures_df_dalian['合约代码'].apply(lambda x: re.sub(r"\d{3}", '', x))
        futures_df_dalian['名称'] = futures_df_dalian['合约名称'].apply(lambda x: re.sub(r"\d{3}", '', x))
    else:
        futures_df_dalian['代码'] = futures_df_dalian['合约代码'].apply(lambda x: re.sub(r"\d{4}", '', x))
        futures_df_dalian['名称'] = futures_df_dalian['合约名称'].apply(lambda x: re.sub(r"\d{4}", '', x))
    return tuple(futures_df_dalian['名称'].unique())

def get_future_symbols(name, ex_code):
    if ex_code == 'SHFE':
        df = ak.futures_comm_info(symbol="上海期货交易所")
        # df['代码'] = df['合约代码'].apply(lambda x: re.sub(r"\d{4}", '', x))
        df['名称'] = df['合约名称'].apply(lambda x: re.sub(r"\d{4}", '', x))
        df = df[df['名称'] == name]
        return list(df['合约代码'].values)
    elif ex_code == 'DCE':
        df = ak.futures_comm_info(symbol="大连商品交易所")
        # df['代码'] = df['合约代码'].apply(lambda x: re.sub(r"\d{4}", '', x))
        df['名称'] = df['合约名称'].apply(lambda x: re.sub(r"\d{4}", '', x))
        df = df[df['名称'] == name]
        return list(df['合约代码'].values)
    elif ex_code == 'GFEX':
        df = ak.futures_comm_info(symbol="广州期货交易所")
        # df['代码'] = df['合约代码'].apply(lambda x: re.sub(r"\d{4}", '', x))
        df['名称'] = df['合约名称'].apply(lambda x: re.sub(r"\d{4}", '', x))
        df = df[df['名称'] == name]
        return list(df['合约代码'].values)
    elif ex_code == 'CZCE':
        df = ak.futures_comm_info(symbol="郑州商品交易所")
        # df['代码'] = df['合约代码'].apply(lambda x: re.sub(r"\d{4}", '', x))
        df['名称'] = df['合约名称'].apply(lambda x: re.sub(r"\d{3}", '', x))
        df = df[df['名称'] == name]
        return list(df['合约代码'].values)


def get_future_price_table(symbols, ex_code):
    df_all = pd.DataFrame()
    for s in symbols:
        s = s.upper()
        if ex_code == 'CZCE':
            s = s[:-3] + '2' + s[-3:]
        df = ak.futures_zh_spot(symbol=s, market="CF", adjust='0')
        df_all = pd.concat([df_all, df])
    print(df_all.columns)

    df_all.sort_values(by='symbol', inplace=True)

    # df_all = df_all[['symbol', 'current_price']]
    df_all['pct_change'] = df_all['current_price'].pct_change()
    df_all['price_change'] = df_all['current_price'] - df_all['current_price'] / (1 + df_all['pct_change'])
    # df_all['pct_change_annual'] = df_all['pct_change'] * 100 * 4
    df_all['pct_change'] = df_all['pct_change'].apply(lambda x: format(x, '.2%'))
    # df_all['price_change'] = df_all['price_change'].apply(lambda x: format(x, '.4'))
    df_all['price_change'] = df_all['price_change'].round(2)

    df_all['total_change'] = df_all['current_price'] - df_all.iloc[0, 5]
    df_all['total_pct_change'] = df_all['total_change'] / df_all.iloc[0, 5]

    df_all['total_change'] = df_all['total_change'].round(2)

    df_all['spread'] = df_all['ask_price'] - df_all['bid_price']
    df_all['spread_per'] = df_all['spread'] / df_all['current_price']
    df_all['spread_per'] = df_all['spread_per'].apply(lambda x: round(x*100, 2))
    df_all['spread_with_per'] = df_all["spread"].map(str) + ' (' + df_all["spread_per"].map(str) + '%)'

    # df_all['total_change'] = df_all['total_change'].apply(lambda x: format(x, '.2'))

    show_columns = ['symbol', 'current_price', 'bid_price',
                    'ask_price', 'buy_vol', 'sell_vol', 'spread_with_per',
                    'pct_change', 'price_change',
                    'total_change', 'total_pct_change']
    # print(df[show_columns])
    comm_heads = COMMODITY_HEADS

    df_all = df_all[show_columns]

    # df_all['date'] = df_all['symbol'].apply(lambda x: get_date(x[-4:-2], x[-2:]))
    # df_all['date'] = df_all['date'].astype(int)
    start_year = int(df_all.iloc[0, 0][-4:-2])
    start_month = int(df_all.iloc[0, 0][-2:])
    print(start_year, start_month)
    df_all['nb_months'] = df_all['symbol'].apply(lambda x: get_date(start_year, start_month, x))

    df_all['total_change_annual'] = (df_all['total_pct_change'] / df_all['nb_months']) * 12

    df_all['total_pct_change'] = df_all['total_pct_change'].apply(lambda x: format(x, '.2%'))
    df_all['total_change_annual'] = df_all['total_change_annual'].apply(lambda x: format(x, '.2%'))

    df_all.rename(columns={'symbol': comm_heads[0],
                           'current_price': comm_heads[1],
                           'bid_price': comm_heads[2],
                           'ask_price': comm_heads[3],
                           'buy_vol': comm_heads[4],
                           'sell_vol': comm_heads[5],
                           'spread_with_per': comm_heads[6],
                           'pct_change': comm_heads[7],
                           'price_change': comm_heads[8],
                           'total_change': comm_heads[9],
                           'total_pct_change': comm_heads[10],
                           'nb_months': comm_heads[11],
                           'total_change_annual': comm_heads[12]},
                  inplace=True)
    return df_all


import re

if __name__ == '__main__':
    get_commodity_list_by_exchange('大连商品交易所')
