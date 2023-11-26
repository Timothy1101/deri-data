import tkinter as tk
from tkinter import ttk
from akshare import option_sse_list_sina
from akshare import option_sse_expire_day_sina
from akshare import option_cffex_sz50_list_sina
import share_util as su
from datetime import datetime
import numpy as np
import akShareOptData as ako
import akShareIndexOption as aki
import akShareFtrData as akf
import commodity as cd
from tkinter import messagebox

future_heads = ('名称', '时间', '期指价格', '指数点位', '到期日', '剩余天数', '贴水',
                '贴水率', '年化贴水', '移仓年化', '单点指数价格', '一手市值')

# commodity_heads = ('symbol', 'current_price', 'bid_price',
#        'ask_price', 'buy_vol', 'sell_vol',
#        'last_close', 'pct_change', 'price_change',
#        'total_change', 'total_pct_change')

commodity_heads = ('合约名称', '当前价格', '买价',
                   '卖价', '买量', '卖量', '滑点',
                   '换月变化率', '换月价差',
                   '累计价差', '累计变化率', '月份差', '累计年化')
# commodity_dalian = (
#     '黄大豆1号' '黄大豆2号' '玉米' '玉米淀粉' '苯乙烯' '乙二醇' '纤维板' '铁矿石' '焦炭' '鸡蛋' '焦煤' '塑料'
#     '生猪' '豆粕' '棕榈油' '液化石油气' '聚丙烯' '粳米' 'PVC' '豆油')

etf_opt_heads = ('标的名称', '合约名称', '当前价', '前结价', '涨跌幅', '隐含波动率', '标的价格',
                 '合约单位', '行权价', '合成价值', '折价率', '剩余天数', '年化折价率')
index_opt_heads = ('认购代码', '认购卖价', '认沽买价', '多头合成价值', '多头折价率', '多头年化折价率',
                   '行权价', '认沽代码', '认沽卖价', '认购买价', '空头合成价值', '空头折价率', '空头年化折价率')


def re_format(df):
    df.rename(columns={'symbol': '名称', 'time': '时间', 'current_price': '期指价格',
                       'index_price': '指数点位', 'last_day': '到期日', 'rem_days': '剩余天数',
                       'gap': '贴水', 'dis': '贴水率', 'y_dis': '年化贴水',
                       'y_move': '移仓年化', 'price_per_index': '单点指数价格', 'total_cap': '一手市值'}, inplace=True)

    df = df[['名称', '时间', '期指价格', '指数点位', '到期日', '剩余天数', '贴水', '贴水率', '年化贴水', '移仓年化',
             '单点指数价格', '一手市值']]
    return df


# ETF 期权数据重新排列
def re_format_etf_opt_data(df):
    df = df[['标的名称', '合约名称', '当前价', '前结价', '涨跌幅', '隐含波动率', '标的价格', '合约单位', '行权价',
             '合成价值', '折价率', '剩余天数', '年化折价率']]
    return df


# ETF 指数期权数据重新排列
def re_format_index_opt_data(df):
    df.rename(columns={'call_code': '认购代码', 'call_sell_with_volume': '认购卖价', 'put_buy_with_volume': '认沽买价',
                       'long_mer_value': '多头合成价值', 'long_dis': '多头折价率', 'long_dis_annual': '多头年化折价率',
                       'put_code': '认沽代码', 'put_sell_with_volume': '认沽卖价', 'call_buy_with_volume': '认购买价',
                       'short_mer_value': '空头合成价值', 'short_dis': '空头折价率',
                       'short_dis_annual': '空头年化折价率'},
              inplace=True)
    df = df[['认购代码', '认购卖价', '认沽买价', '多头合成价值', '多头折价率', '多头年化折价率', '行权价',
             '认沽代码', '认沽卖价', '认购买价', '空头合成价值', '空头折价率', '空头年化折价率']]
    return df


# get edt end date list
def get_eft_date_list():
    expDateList = []
    # 获取所有50ETF合约的列表到期月份
    option_sse_list_sina_df1 = option_sse_list_sina(symbol="50ETF", exchange="null")
    for month in option_sse_list_sina_df1:
        # 获取所有50ETF合约到期月份 对应的到期日
        option_sse_expire_day_sina_df = option_sse_expire_day_sina(trade_date=month, symbol="50ETF", exchange="null")
        expDateList.append(option_sse_expire_day_sina_df[0])
    return expDateList


# 得到指数日期
def get_index_date_list():
    expDateList = []
    option_cffex_hs50_list_sina_df = option_cffex_sz50_list_sina()
    hs50_index_contracts = option_cffex_hs50_list_sina_df['上证50指数']
    sz50_index_contracts = np.sort(hs50_index_contracts)
    remainingDaysList = []
    for cc in sz50_index_contracts:
        year, month = int('20' + cc[-4:-2]), int(cc[-2:])
        lstDate = su.getLastDay(year, month)
        expDateList.append(str(lstDate)[:10])
        remaining_days = (lstDate - datetime.today()).days
        print(remaining_days)
        remainingDaysList.append(remaining_days)
    return expDateList


def show_window():
    # 获取股指期货数据 并显示出来
    def get_future_data():
        print('--clean old data---')
        treeview.delete(*treeview.get_children())
        tab1.update()
        # sleep(1)
        print('---get new data---')
        try:
            future_data = akf.getFutureList()
            if future_data is not None and len(future_data) > 0:
                future_data = re_format(future_data)
                for col in future_data.columns:  # 显示列名
                    treeview.heading(col, text=col)
                    if col == '名称':
                        treeview.column(col, width=150, stretch=False, anchor='center')
                    else:
                        treeview.column(col, minwidth=60, width=100, stretch=False, anchor='center')
                for index, row in future_data.iterrows():
                    treeview.insert('', 'end', values=tuple(row))
                treeview.pack(expand=True, fill=tk.BOTH)
                print('success!')
        except:
            messagebox.showinfo("警告", '获取数据失败！')
        # future_data = pd.read_excel('股指期货.xlsx')

    # 获取商品期货数据并展示
    def get_commodity_data(ex_code):
        print(f'---get_commodity_data---for {ex_code}')
        try:
            if ex_code == 'DCE':  # 大连商品交易所
                treeview_commodity_dce.delete(*treeview_commodity_dce.get_children())
                tab_commodity_dce.update()
                commodity_value = commodity_name_dce.get()  # 获取商品期货名称
                s_list = cd.get_future_symbols(commodity_value, ex_code)  # 获取商品对应的合约列表
                commodity_data = cd.get_future_price_table(s_list,ex_code)  # 获取合约对应的价格数据
                if commodity_data is not None and len(commodity_data) > 0:
                    cols = commodity_data.columns
                    for col in cols:
                        treeview_commodity_dce.heading(col, text=col)
                        treeview_commodity_dce.column(col, width=100, stretch=False, anchor='center')
                    for index, row in commodity_data.iterrows():
                        treeview_commodity_dce.insert('', 'end', values=tuple(row))
                    treeview_commodity_dce.pack(expand=True, fill=tk.BOTH)
            elif ex_code == 'SHFE':  # 上海期货交易所
                treeview_commodity_shfe.delete(*treeview_commodity_shfe.get_children())
                tab_commodity_shfe.update()
                commodity_shfe_value = commodity_shfe_name.get()
                s_list = cd.get_future_symbols(commodity_shfe_value, ex_code)
                commodity_data = cd.get_future_price_table(s_list,ex_code)
                print(commodity_data)
                if commodity_data is not None and len(commodity_data) > 0:
                    cols = commodity_data.columns
                    for col in cols:
                        treeview_commodity_shfe.heading(col, text=col)
                        treeview_commodity_shfe.column(col, width=100, stretch=False, anchor='center')
                    for index, row in commodity_data.iterrows():
                        treeview_commodity_shfe.insert('', 'end', values=tuple(row))
                    treeview_commodity_shfe.pack(expand=True, fill=tk.BOTH)
            elif ex_code == 'GFEX':# 广州期货交易所
                treeview_commodity_gfex.delete(*treeview_commodity_gfex.get_children())
                tab_commodity_gfex.update()
                commodity_gfex_value = commodity_gfex_name.get()
                s_list = cd.get_future_symbols(commodity_gfex_value, ex_code)
                commodity_data = cd.get_future_price_table(s_list,ex_code)
                if commodity_data is not None and len(commodity_data) > 0:
                    cols = commodity_data.columns
                    for col in cols:
                        treeview_commodity_gfex.heading(col, text=col)
                        treeview_commodity_gfex.column(col, width=100, stretch=False, anchor='center')
                    for index, row in commodity_data.iterrows():
                        treeview_commodity_gfex.insert('', 'end', values=tuple(row))
                    treeview_commodity_gfex.pack(expand=True, fill=tk.BOTH)
            elif ex_code == 'CZCE':# 郑州商品交易所
                treeview_commodity_czce.delete(*treeview_commodity_czce.get_children())
                tab_commodity_czce.update()
                commodity_czce_value = commodity_czce_name.get()
                s_list = cd.get_future_symbols(commodity_czce_value, ex_code)
                commodity_data = cd.get_future_price_table(s_list,ex_code)
                if commodity_data is not None and len(commodity_data) > 0:
                    cols = commodity_data.columns
                    for col in cols:
                        treeview_commodity_czce.heading(col, text=col)
                        treeview_commodity_czce.column(col, width=100, stretch=False, anchor='center')
                    for index, row in commodity_data.iterrows():
                        treeview_commodity_czce.insert('', 'end', values=tuple(row))
                    treeview_commodity_czce.pack(expand=True, fill=tk.BOTH)
            print('success!')
        except:
            messagebox.showinfo("警告", '获取数据失败！')

    # 获取ETF 合成多头的数值 并显示
    def get_eft_mer_data():
        # clean data first
        treeview2.delete(*treeview2.get_children())
        tab2.update()

        print('--get_eft_mer_data---')
        cen_value = cmb_etf_name.get()
        ced_value = cmb_etf_date.get()

        print(cen_value)
        print(ced_value)

        opt_data, opt_name, edt_code = None, None, None
        if cen_value == "上证50ETF":
            opt_name, edt_code = "华夏上证50ETF期权", "sh510050"
        elif cen_value == "沪深300ETF":
            opt_name, edt_code = "华泰柏瑞沪深300ETF期权", "sh510300"
        try:
            opt_data = ako.getMergeOption(opt_name, edt_code, ced_value)
            print(opt_data)
        except:
            messagebox.showinfo("警告", '获取数据失败！')

        opt_data = re_format_etf_opt_data(opt_data)
        # load data again
        for col in opt_data.columns:  # 显示列名
            treeview2.heading(col, text=col)
            if col == '标的名称' or col == '合约名称':
                treeview2.column(col, width=130, stretch=False, anchor='center')
            else:
                treeview2.column(col, width=85, stretch=False, anchor='center')

        # Define the row colors with a tag
        treeview2.tag_configure("call_row", background="#343a40")
        treeview2.tag_configure("put_row", background="#343a40")

        # # Insert the parent row - using the tag, 'product_row'
        # pizza_row = treeview_products.insert(parent="", index="end", text="Pizza", tag="product_row")
        # # Insert sub-row - using the tag, 'details_row'
        # treeview_products.insert(parent=pizza_row, index="end", values=("Cheese", "$0.89"), tag="details_row")

        for index, row in opt_data.iterrows():  # 显示值
            if index % 2 == 0:
                treeview2.insert('', index="end", values=tuple(row), tag="call_row")
            else:
                treeview2.insert('', 'end', values=tuple(row))
        # pack the Treeview widget
        treeview2.pack(expand=True, fill=tk.BOTH)

    # 获取指数 合成多头的数值
    def get_index_mer_data():
        # clean data first
        treeview3.delete(*treeview3.get_children())
        tab2.update()

        print('--get_index_mer_data---')
        cin_value = cmb_index_name.get()
        cid_value = cmb_index_date.get()
        print(cin_value)
        print(cid_value)

        expDateList = []
        sz50_index_contracts = aki.get_sz50_index_contracts()
        hs300_index_contracts = aki.get_hs300_index_contracts()
        zz1000_index_contracts = aki.get_zz1000_index_contracts()

        remainingDaysList = []
        for cc in sz50_index_contracts:
            year, month = int('20' + cc[-4:-2]), int(cc[-2:])
            lstDate = su.getLastDay(year, month)
            expDateList.append(str(lstDate)[:10])
            remaining_days = (lstDate - datetime.today()).days
            print(remaining_days)
            remainingDaysList.append(remaining_days)

        expDateIndex = 0
        print(cid_value)
        if len(cid_value) > 0:
            expDateIndex = expDateList.index(cid_value)

        index_prices_list = su.getMultiStockPrices('sh000016,sh000300,sh000852')
        remaining_days = remainingDaysList[expDateIndex]

        indexPrice, contactCode, index_code = None, None, None
        index_df = None
        if cin_value == '上证50':
            print('-------------上证50----------------')
            indexPrice = index_prices_list[0]
            contactCode = sz50_index_contracts[expDateIndex]
            index_code = 'sh000016'
        if cin_value == '沪深300':
            contactCode = hs300_index_contracts[expDateIndex]
            indexPrice = index_prices_list[1]
            index_code = 'sh000300'
        if cin_value == '中证1000':
            print('-------------中证1000----------------')
            indexPrice = index_prices_list[2]
            contactCode = zz1000_index_contracts[expDateIndex]
            index_code = 'sh000852'
        try:
            index_df = aki.get_index_option_prices(indexPrice, contactCode, remaining_days, index_code)
            # index_df.to_excel('股指合成期货.xlsx', index=False)
            # index_df = pd.read_excel('股指合成期货.xlsx')
        except:
            messagebox.showinfo("警告", '获取数据失败！')

        index_df['call_buy_with_volume'] = index_df['call_buy'].map(str) + '(' + index_df['call_buy_volume'].map(
            str) + ')'
        index_df['call_sell_with_volume'] = index_df['call_sell'].map(str) + '(' + index_df['call_sell_volume'].map(
            str) + ')'
        index_df['put_buy_with_volume'] = index_df['put_buy'].map(str) + '(' + index_df['put_buy_volume'].map(
            str) + ')'
        index_df['put_sell_with_volume'] = index_df['put_sell'].map(str) + '(' + index_df['put_sell_volume'].map(
            str) + ')'
        index_df = re_format_index_opt_data(index_df)

        for col in index_df.columns:
            treeview3.heading(col, text=col)
            treeview3.column(col, minwidth=60, width=100, stretch=False, anchor='center')
        for index, row in index_df.iterrows():
            treeview3.insert('', 'end', values=tuple(row))
        # pack the Treeview widget
        # treeview3.tag_configure('oddrow', background='orange')
        # treeview3.tag_configure('evenrow', background='purple')
        treeview3.pack(expand=True, fill=tk.BOTH)

    # show
    root = tk.Tk()
    root.title("衍生品套利")
    root.geometry('1200x600')
    s = ttk.Style()
    s.theme_use('clam')
    s.configure('Treeview', rowheight=30)
    s.configure("Treeview", background="black", fieldbackground="black", foreground="white")
    tabControl = ttk.Notebook(root)

    tab1 = ttk.Frame(tabControl)
    tab2 = ttk.Frame(tabControl)
    tab_commodity_dce = ttk.Frame(tabControl)
    tab_commodity_shfe = ttk.Frame(tabControl)
    tab_commodity_gfex = ttk.Frame(tabControl)
    tab_commodity_czce = ttk.Frame(tabControl)
    tab3 = ttk.Frame(tabControl)
    tab4 = ttk.Frame(tabControl)

    # tab 定义
    tabControl.add(tab1, text='股指期货')
    tabControl.add(tab_commodity_dce, text='大连期货交易所')
    tabControl.add(tab_commodity_shfe, text='上海期货交易所')
    tabControl.add(tab_commodity_gfex, text='广州期货交易所')
    tabControl.add(tab_commodity_czce, text='郑州期货交易所')
    tabControl.add(tab2, text='ETF合成期货')
    tabControl.add(tab3, text='指数合成期货')
    tabControl.add(tab4, text='软件说明')

    tabControl.pack(expand=1, fill="both")

    # 股指期货页面
    tk.Button(tab1, text="刷新", bg='#D1EEEE', command=lambda: get_future_data()).pack(anchor='n')
    treeview = ttk.Treeview(tab1, columns=future_heads, show='headings')

    # 商品期货页面(大连商品交易所)
    commodity_name_dce = ttk.Combobox(tab_commodity_dce)
    commodity_name_dce.pack(anchor='n')
    commodity_name_dce['value'] = cd.get_commodity_list_by_exchange('大连商品交易所')
    commodity_name_dce.current(0)
    tk.Button(tab_commodity_dce, text="刷新", bg='#D1EEEE', command=lambda: get_commodity_data('DCE')).pack(anchor='n')
    treeview_commodity_dce = ttk.Treeview(tab_commodity_dce, columns=commodity_heads, show='headings')

    # 商品期货页面(上海期货交易所)
    commodity_shfe_name = ttk.Combobox(tab_commodity_shfe)
    commodity_shfe_name.pack(anchor='n')
    commodity_shfe_name['value'] = cd.get_commodity_list_by_exchange('上海期货交易所')
    commodity_shfe_name.current(0)
    tk.Button(tab_commodity_shfe, text="刷新", bg='#D1EEEE', command=lambda: get_commodity_data('SHFE')).pack(
        anchor='n')
    treeview_commodity_shfe = ttk.Treeview(tab_commodity_shfe, columns=commodity_heads, show='headings')

    # 商品期货页面(广州期货交易所)
    commodity_gfex_name = ttk.Combobox(tab_commodity_gfex)
    commodity_gfex_name.pack(anchor='n')
    commodity_gfex_name['value'] = cd.get_commodity_list_by_exchange('广州期货交易所')
    commodity_gfex_name.current(0)
    tk.Button(tab_commodity_gfex, text="刷新", bg='#D1EEEE', command=lambda: get_commodity_data('GFEX')).pack(
        anchor='n')
    treeview_commodity_gfex = ttk.Treeview(tab_commodity_gfex, columns=commodity_heads, show='headings')

    # 商品期货页面(郑州期货交易所)
    commodity_czce_name = ttk.Combobox(tab_commodity_czce)
    commodity_czce_name.pack(anchor='n')
    commodity_czce_name['value'] = cd.get_commodity_list_by_exchange('郑州商品交易所')
    commodity_czce_name.current(0)
    tk.Button(tab_commodity_czce, text="刷新", bg='#D1EEEE', command=lambda: get_commodity_data('CZCE')).pack(
        anchor='n')
    treeview_commodity_czce = ttk.Treeview(tab_commodity_czce, columns=commodity_heads, show='headings')

    # ETF合成期货页面
    cmb_etf_name = ttk.Combobox(tab2)
    cmb_etf_name.pack(anchor='n')
    cmb_etf_name['value'] = ('上证50ETF', '沪深300ETF')
    cmb_etf_name.current(0)
    cmb_etf_date = ttk.Combobox(tab2, state='readonly')
    cmb_etf_date.pack(anchor='n')
    # cmb_etf_date['value'] = ('2023-05-24', '2023-06-28', '2023-09-27')
    cmb_etf_date['value'] = tuple(get_eft_date_list())
    cmb_etf_date.current(0)
    tk.Button(tab2, text="刷新", bg='#D1EEEE', command=lambda: get_eft_mer_data()).pack(anchor='n')
    treeview2 = ttk.Treeview(tab2, columns=etf_opt_heads, show='headings')

    # 股指合成期货页面
    cmb_index_name = ttk.Combobox(tab3, state='readonly')
    cmb_index_name.pack(anchor='n')
    cmb_index_name['value'] = ('上证50', '沪深300', '中证1000')
    cmb_index_name.current(0)
    cmb_index_date = ttk.Combobox(tab3, state='readonly')
    cmb_index_date.pack(anchor='n')
    # cmb_index_date['value'] = ('2023-05-19', '2023-06-16', '2023-09-15')
    cmb_index_date['value'] = tuple(get_index_date_list())
    cmb_index_date.current(0)
    tk.Button(tab3, text="刷新", bg='#D1EEEE', command=lambda: get_index_mer_data()).pack(anchor='n')
    treeview3 = ttk.Treeview(tab3, columns=index_opt_heads, show='headings')

    # 软件说明的页面
    # my_label = ttk.Label(tab4)
    # with open('describe.txt', 'r', encoding='utf-8') as f:
    #     des_text = f.read()
    #     my_label.config(text=des_text)
    # my_label.pack(anchor='n')
    # run the tkinter event loop
    root.mainloop()


# if __name__ == '__main__':
#     # show_window()
#     # futureList = akftr.getFutureList()
#     # print(futureList.info())
#     show_window()
