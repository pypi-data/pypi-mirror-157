#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019-2020 wesley wu

# 导入Api的响应回复的对象
from .apiresponses import *
# 导入Api的请求对象
from .tradingapi import TradingApi


class RFTradingApi(TradingApi):
    """
    主要的交易Api,和RedFox服务端进行交互.
    RedFox要配置成Standalone模式
    Interact the RedFox REST API.
    """

    # =================
    # 以下是交易函数
    # =================

    def post_open_trader(self):
        """
        打开控制器关联的交易软件
        :return: 返回一个CommonResponse, content的内容是:结果说明,或者RUNNING,STARTING,STOPPED
        """
        json_resp_obj = self.trading_client.post('/trader/open')
        return self._json_object_to_class_object(json_resp_obj, CommonResponse, is_list=False)

    def post_login_trader(self, login_trader_req):
        """
        登录交易控制器关联的交易软件
        :param login_trader_req: 账户登录的请求对象
        :return: 返回一个CommonResponse, content的内容是登录的结果
        """
        data = json.dumps(login_trader_req.__dict__)
        json_resp_obj = self.trading_client.post('/trader/login', None, data=data)
        return self._json_object_to_class_object(json_resp_obj, CommonResponse, is_list=False)

    def delete_close_trader(self):
        """
        停止控制器关联的交易软件
        :return: 返回一个CommonResponse, content的内容是关闭后的结果提示
        """
        json_resp_obj = self.trading_client.delete('/trader/close')
        return self._json_object_to_class_object(json_resp_obj, CommonResponse, is_list=False)

    def post_reload_trader(self):
        """
        重启加载控制器关联的交易软件
        :return: 返回一个CommonResponse, content的内容是重启加载的结果提示
        """
        json_resp_obj = self.trading_client.post('/trader/reload')
        return self._json_object_to_class_object(json_resp_obj, CommonResponse, is_list=False)

    def get_trader_status(self):
        """
        查询控制器关联的交易软件的运行状态
        :return: 返回一个CommonResponse, content的内容是:RUNNING,STARTING,STOPPED
        """
        json_resp_obj = self.trading_client.get('/trader/status')
        return self._json_object_to_class_object(json_resp_obj, TraderStatus, is_list=False)

    def get_active_account(self):
        """
        查询交易软件上的登录的账号
        :return: 返回ActiveAccount, account的内容是账号的名称
        """
        json_resp_obj = self.trading_client.get('/accounts/active')
        return self._json_object_to_class_object(json_resp_obj, ActiveAccount, is_list=False)

    def get_accounts(self):
        """
        查询配置的账号信息
        :return: 返回Account对象的列表
        """
        json_resp_obj = self.trading_client.get('/accounts/list')
        final_accts = Accounts(json_resp_obj['accounts'])
        return final_accts

    def post_add_account(self, login_trader_req):
        """
        增加一个证券账号
        :param login_trader_req: 账户登录的请求对象
        :return: 返回一个CommonResponse, content的内容是登录的结果
        """
        data = json.dumps(login_trader_req.__dict__)
        json_resp_obj = self.trading_client.post('/accounts/add', None, data=data)
        return self._json_object_to_class_object(json_resp_obj, CommonResponse, is_list=False)

    def post_set_active_account(self, set_active_account_req):
        """
        增加一个证券账号
        :param set_active_account_req: 设置活跃账号的请求对象
        :return: 返回一个CommonResponse, content的内容是登录的结果
        """
        data = json.dumps(set_active_account_req.__dict__)
        json_resp_obj = self.trading_client.post('/accounts/setactive', None, data=data)
        return self._json_object_to_class_object(json_resp_obj, CommonResponse, is_list=False)

    def get_account_balance(self):
        """
        查询指定账号的账号余额
        :return: 返回一个AccountBalance
        """
        json_resp_obj = self.trading_client.get('/account/balance')
        return self._json_object_to_class_object(json_resp_obj, AccountBalance, is_list=False)

    def get_account_positions(self):
        """
        查询指定账号的持仓
        :return: 返回一个Positions
        """
        json_resp_obj = self.trading_client.get('/account/positions')
        position_list = self._json_object_to_class_object(json_resp_obj['positions'], Position, is_list=True)
        final_positions = Positions(position_list)
        return final_positions

    def get_account_shareholders(self):
        """
        查询指定账号的持仓
        :return: 返回一个Shareholders
        """
        json_resp_obj = self.trading_client.get('/account/shareholders')
        shareholders_list = self._json_object_to_class_object(json_resp_obj['shareholdersList'], Shareholder, is_list=True)
        final_shareholders = Shareholders(shareholders_list)
        return final_shareholders

    def get_ipo_available_stocks(self):
        """
        查询指定账号的IPO可申购新股
        :return: 返回一个IPOStocks
        """
        json_resp_obj = self.trading_client.get('/ipo/availablestocks')
        stock_list = self._json_object_to_class_object(json_resp_obj['stocks'], IPOStock, is_list=True)
        final_ipo_stocks = IPOStocks(stock_list)
        return final_ipo_stocks

    def get_ipo_equity(self):
        """
        查询指定账号的IPO可申购新股的权益
        :return: 返回一个Equities
        """
        json_resp_obj = self.trading_client.get('/ipo/accountequity')
        equity_list = self._json_object_to_class_object(json_resp_obj['equities'], Equity, is_list=True)
        final_equities = Equities(equity_list)
        return final_equities

    def get_ipo_allocated_stocks(self):
        """
        查询指定账号的IPO的新股中签
        :return: 返回一个IPOStocks
        """
        json_resp_obj = self.trading_client.get('/ipo/allocatedstocks')
        stock_list = self._json_object_to_class_object(json_resp_obj['stocks'], IPOStock, is_list=True)
        final_ipo_stocks = IPOStocks(stock_list)
        return final_ipo_stocks

    def get_ipo_allocated_numbers(self):
        """
        查询指定账号的IPO的新股配号
        :return: 返回一个AllocatedNumbers
        """
        json_resp_obj = self.trading_client.get('/ipo/allocatednumbers')
        alloc_numbs_list = self._json_object_to_class_object(json_resp_obj['allocatedNumbers'], AllocatedNumber,
                                                           is_list=True)
        final_alloc_numbs = AllocatedNumbers(alloc_numbs_list)
        return final_alloc_numbs

    def get_account_all_orders(self):
        """
        查询指定账号的当日委托
        :return: 返回一个Orders
        """
        json_resp_obj = self.trading_client.get('/orders/all')
        orders_list = self._json_object_to_class_object(json_resp_obj['orders'], Order, is_list=True)
        final_orders = Orders(orders_list)
        return final_orders

    def get_account_opened_orders(self):
        """
        查询指定账号的当日可撤订单
        :return: 返回一个Orders
        """
        json_resp_obj = self.trading_client.get('/orders/opened')
        orders_list = self._json_object_to_class_object(json_resp_obj['orders'], Order, is_list=True)
        final_orders = Orders(orders_list)
        return final_orders

    def get_account_filled_orders(self):
        """
        查询指定账号的当日成交订单
        :return: 返回一个Orders
        """
        json_resp_obj = self.trading_client.get('/orders/filled')
        orders_list = self._json_object_to_class_object(json_resp_obj['orders'], Order, is_list=True)
        final_orders = Orders(orders_list)
        return final_orders

    def get_account_history_orders(self):
        """
        查询指定账号的历史订单
        :return: 返回一个Orders
        """
        json_resp_obj = self.trading_client.get('/orders/history')
        orders_list = self._json_object_to_class_object(json_resp_obj['orders'], Order, is_list=True)
        final_orders = Orders(orders_list)
        return final_orders

    def post_place_order(self, placeOrderReq):
        """
        下单
        :param placeOrderReq: 下单的请求
        :return: 返回一个CommonResponse, 内容是Place the order succeed,Failed to place the order
        """
        data = json.dumps(placeOrderReq.__dict__)
        json_resp_obj = self.trading_client.post('/orders/place', None, data=data)
        return self._json_object_to_class_object(json_resp_obj, CommonResponse, is_list=False)

    def cancel_account_all_orders(self):
        """
        撤销指定账号内所有的订单
        :return: 返回一个返回一个CommonResponse, content的内容是撤销的结果
        """
        json_resp_obj = self.trading_client.delete('/orders/all')
        return self._json_object_to_class_object(json_resp_obj, CommonResponse, is_list=False)

    def cancel_account_all_buy_orders(self):
        """
        撤销指定账号内所有的买单
        :return: 返回一个返回一个CommonResponse, content的内容是撤销的结果
        """
        json_resp_obj = self.trading_client.delete('/orders/buy')
        return self._json_object_to_class_object(json_resp_obj, CommonResponse, is_list=False)

    def cancel_account_all_sell_orders(self):
        """
        撤销指定账号内所有的卖单
        :return: 返回一个返回一个CommonResponse, content的内容是撤销的结果
        """
        json_resp_obj = self.trading_client.delete('/orders/sell')
        return self._json_object_to_class_object(json_resp_obj, CommonResponse, is_list=False)

    def cancel_account_all_orders_by_symbol(self, symbol):
        """
        撤销指定账号内所有的指定股票代码的订单
        :param symbol: 股票代码
        :return: 返回一个返回一个CommonResponse, content的内容是撤销的结果
        """
        json_resp_obj = self.trading_client.delete('/orders/symbol/{}/all'.format(symbol))
        return self._json_object_to_class_object(json_resp_obj, CommonResponse, is_list=False)

    def cancel_account_all_buy_orders_by_symbol(self, symbol):
        """
        撤销指定账号内所有的指定股票代码的买单
        :param symbol: 股票代码
        :return: 返回一个返回一个CommonResponse, content的内容是撤销的结果
        """
        json_resp_obj = self.trading_client.delete('/orders/symbol/{}/buy'.format(symbol))
        return self._json_object_to_class_object(json_resp_obj, CommonResponse, is_list=False)

    def cancel_account_all_sell_orders_by_symbol(self, symbol):
        """
        撤销指定账号内所有的指定股票代码的卖单
        :param symbol: 股票代码
        :return: 返回一个返回一个CommonResponse, content的内容是撤销的结果
        """
        json_resp_obj = self.trading_client.delete('/orders/symbol/{}/sell'.format(symbol))
        return self._json_object_to_class_object(json_resp_obj, CommonResponse, is_list=False)

    def cancel_account_orders_by_contract_no(self, contract_no):
        """
        撤销指定账号内所有的指定股票代码的卖单
        :param contract_no: 委托编号/合同号码
        :return: 返回一个返回一个CommonResponse, content的内容是撤销的结果
        """
        json_resp_obj = self.trading_client.delete('/orders/contractno/{}'.format(contract_no))
        return self._json_object_to_class_object(json_resp_obj, CommonResponse, is_list=False)


# -------------------------------------------
if __name__ == "__main__":
    print()
    # tradingApi = RFTradingApi("http://localhost:8080/", "xx", "xx");
    # openTraderResp = tradingApi.post_open_trader()
    # closeTraderResp = tradingApi.delete_close_trader()
    # reloadTraderResp = tradingApi.post_reload_trader()
    # traderStatusResp = tradingApi.get_trader_status()
    # print(traderStatusResp)
    # activeAccount = tradingApi.get_active_account()
    # print(activeAccount)
    # print("\u4e2d\u4fe1\u8bc1\u5238-\u6b66*".encode('utf8').decode('utf8'))
    # accts = tradingApi.get_accounts()
    # # print(accts.accounts)
    # activeAcct = tradingApi.get_active_account()
    # print(activeAcct)
    # acct = tradingApi.get_account('Account-0001')
    # print(acct)
    # acctBalance = tradingApi.get_account_balance()
    # print(acctBalance)
    # acctPositions = tradingApi.get_account_positions()
    # print(acctPositions.positions)
    # shareholders = tradingApi.get_account_shareholders()
    # print(shareholders.shareholders)
    # ipoAvailStocks = tradingApi.get_ipo_available_stocks()
    # ipoAllocStocts = tradingApi.get_ipo_allocated_stocks()
    # ipoAllocNumbs = tradingApi.get_ipo_allocated_numbers()
    # iallOrders = tradingApi.get_account_all_orders()
    # iprint(allOrders)
    # openedOrders = tradingApi.get_account_opened_orders()
    # print(openedOrders)
    # filledOrders = tradingApi.get_account_filled_orders()
    # print(filledOrders)
    # hisOrders = tradingApi.get_account_history_orders()
    # print(hisOrders)
    # cancelAllOrdersResp = tradingApi.cancel_account_all_orders()
    # print(cancelAllOrdersResp)
    # cancelAllBuyOrdersResp = tradingApi.cancel_account_all_buy_orders()
    # print(cancelAllBuyOrdersResp)
    # cancelAllSellOrdersResp = tradingApi.cancel_account_all_sell_orders()
    # print(cancelAllSellOrdersResp)
    # cancelAllOrdersBySymbolResp = tradingApi.cancel_account_all_orders_by_symbol("600022")
    # print(cancelAllOrdersBySymbolResp)
    # cancelAllBuyOrdersBySymbolResp = tradingApi.cancel_account_all_buy_orders_by_symbol("600022")
    # print(cancelAllBuyOrdersBySymbolResp)
    # cancelAllSellOrdersBySymbolResp = tradingApi.cancel_account_all_sell_orders_by_symbol("600022")
    # print(cancelAllSellOrdersBySymbolResp)
    # cancelAllOrdersByContractNoResp = tradingApi.cancel_account_orders_by_contract_no("600022")
    # print(cancelAllOrdersByContractNoResp)

