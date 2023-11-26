import akshare as ak
import pandas as pd


def get_bonds_future():
    futures_zh_spot_df1 = ak.futures_zh_spot(symbol='T2312', market="CFFEX", adjust='0')
    futures_zh_spot_df2 = ak.futures_zh_spot(symbol='T2403', market="CFFEX", adjust='0')
    futures_zh_spot_df3 = ak.futures_zh_spot(symbol='T2406', market="CFFEX", adjust='0')
    df = pd.concat([futures_zh_spot_df1, futures_zh_spot_df2, futures_zh_spot_df3])
    print(df.columns)
    df = df[['symbol', 'current_price']]
    df['pct_change'] = df['current_price'].pct_change() * 100 * 4
    print(df)


if __name__ == '__main__':
    # print_hi('PyCharm')
    # get_bonds_future()

    stock_zh_index_spot_df = ak.stock_zh_index_spot()
    print(stock_zh_index_spot_df.columns)
    # print(stock_zh_index_spot_df[['代码', '名称', '最新价']])
    print(stock_zh_index_spot_df['名称'].values)
    print(stock_zh_index_spot_df[stock_zh_index_spot_df['名称']=='国债指数'])
