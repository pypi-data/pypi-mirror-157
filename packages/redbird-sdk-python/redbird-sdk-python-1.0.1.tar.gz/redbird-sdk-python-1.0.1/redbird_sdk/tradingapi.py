#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019-2020 wesley wu

# 导入Rest Client
from .restclient import RestClient
# 导入Api的响应回复的对象
from .apiresponses import *


class TradingApi:
    """
    主要的交易Api,和RedBird服务端进行交互.
    Interact the RedBird REST API.
    """

    def __init__(self, api_Url = None, username=None, password=None,):
        """
        创建RedBirdClient的实例.
        :param str api_Url: url address, "http://x.x.x.x"
        :param str username: Basic auth username
        :param str password: Basic auth password
        """
        self.trading_client = RestClient(api_Url, username, password)

    @staticmethod
    def _json_object_to_class_object(response, clazz, is_list=False, resource_name=None):
        """
        解析RedBird的返回数据,并转换成相应的对象或者对象的列表
        Parse a redbird response into an object or list of objects.
        :param  response: response.json()['data']
        """
        if is_list:
            return [clazz.from_json(resource) for resource in response]
        else:
            return clazz.from_json(response)

    ###
    # 以下是交易函数
    ###
    def get_all_controllers(self):
        """
        查询所有的交易软件控制器
        :return: 返回controllers对象
        """
        jsonRespObj = self.trading_client.get('/controllers/all')
        controllerList = self._json_object_to_class_object(jsonRespObj['controllers'], Controller, is_list=True)
        finalControllers = Controllers(controllerList)
        return finalControllers

    def post_open_trader(self, controllerId):
        """
        打开控制器关联的交易软件
        :param controllerId: 控制器的Id
        :return: 返回一个CommonResponse, content的内容是:结果说明,或者RUNNING,STARTING,STOPPED
        """
        jsonRespObj = self.trading_client.post('/controller/{}/opentrader'.format(controllerId))
        return self._json_object_to_class_object(jsonRespObj, CommonResponse, is_list=False)

    def post_login_trader(self, controllerId, loginTraderReq):
        """
        登录交易控制器关联的交易软件
        :param controllerId: 控制器Id
        :param loginTraderReq: 账户登录的请求对象
        :return: 返回一个CommonResponse, content的内容是登录的结果
        """
        data = json.dumps(loginTraderReq.__dict__)
        jsonRespObj = self.trading_client.post('/controller/{}/logintrader'.format(controllerId), None, data = data)
        return self._json_object_to_class_object(jsonRespObj, CommonResponse, is_list=False)

    def get_trader_status(self, controllerId):
        """
        查询控制器关联的交易软件的运行状态
        :param controllerId: 控制器Id
        :return: 返回一个CommonResponse, content的内容是:RUNNING,STARTING,STOPPED
        """
        jsonRespObj = self.trading_client.get('/controller/{}/traderstatus'.format(controllerId))
        return self._json_object_to_class_object(jsonRespObj, TraderStatus, is_list=False)

    def deleteCloseTrader(self, controllerId):
        """
        停止控制器关联的交易软件
        :param controllerId: 控制器Id
        :return: 返回一个CommonResponse, content的内容是关闭后的结果提示
        """
        jsonRespObj = self.trading_client.delete('/controller/{}/closetrader'.format(controllerId))
        return self._json_object_to_class_object(jsonRespObj, CommonResponse, is_list=False)

    def post_reload_trader(self, controllerId):
        """
        重启加载控制器关联的交易软件
        :param controllerId: 控制器Id
        :return: 返回一个CommonResponse, content的内容是重启加载的结果提示
        """
        jsonRespObj = self.trading_client.post('/controller/{}/reloadtrader'.format(controllerId))
        return self._json_object_to_class_object(jsonRespObj, CommonResponse, is_list=False)

    def get_active_account_in_trader(self, controllerId):
        """
        查询交易软件上的登录的账号
        :param controllerId: 控制器Id
        :return: 返回ActiveAccountInTrader, account的内容是账号的名称
        """
        jsonRespObj = self.trading_client.get('/controller/{}/trader/activeaccount'.format(controllerId))
        return self._json_object_to_class_object(jsonRespObj, ActiveAccount, is_list=False)

    def get_accounts(self):
        """
        查询配置的账号信息
        :return: 返回Account对象的列表
        """
        jsonRespObj = self.trading_client.get('/accounts/all')
        acctList = self._json_object_to_class_object(jsonRespObj['accounts'], Account, is_list=True)
        finalAccts = Accounts(acctList)
        return finalAccts


    def get_active_accounts(self):
        """
        查询当前实时在线的账号信息
        :return: 返回Account对象的列表
        """
        jsonRespObj = self.trading_client.get('/accounts/active')
        acctList = self._json_object_to_class_object(jsonRespObj['accounts'], Account, is_list=True)
        finalAccts = Accounts(acctList)
        return finalAccts

    def get_account(self, acctId):
        """
        查询指定账号的配置信息
        :param acctId: 账号Id
        :return: 返回一个Account
        """
        jsonRespObj = self.trading_client.get('/account/{}'.format(acctId))
        return self._json_object_to_class_object(jsonRespObj, Account, is_list=False)

    def get_account_balance(self, acctId):
        """
        查询指定账号的账号余额
        :param acctId: 账号Id
        :return: 返回一个AccountBalance
        """
        jsonRespObj = self.trading_client.get('/account/{}/balance'.format(acctId))
        return self._json_object_to_class_object(jsonRespObj, AccountBalance, is_list=False)

    def get_account_positions(self, acctId):
        """
        查询指定账号的持仓
        :param acctId: 账号Id
        :return: 返回一个Positions
        """
        jsonRespObj = self.trading_client.get('/account/{}/positions'.format(acctId))
        positionList = self._json_object_to_class_object(jsonRespObj['positions'], Position, is_list=True)
        finalPositions = Positions(positionList)
        return finalPositions

    def get_account_shareholders(self, acctId):
        """
        查询指定账号的持仓
        :param acctId: 账号Id
        :return: 返回一个Shareholders
        """
        jsonRespObj = self.trading_client.get('/account/{}/shareholders'.format(acctId))
        shareholdersList = self._json_object_to_class_object(jsonRespObj['shareholdersList'], Shareholder, is_list=True)
        finalShareholders = Shareholders(shareholdersList)
        return finalShareholders

    def get_account_groups(self):
        """
        查询账号组信息
        :return: 返回AccountGroup对象的列表
        """
        jsonRespObj = self.trading_client.get('/accountgroups/all')
        acctGroupList = self._json_object_to_class_object(jsonRespObj['accountGroups'], AccountGroup, is_list=True)
        finalAcctGroups = AccountGroups(acctGroupList)
        return finalAcctGroups

    def get_account_group(self, acctGroupId):
        """
        查询指定账号组信息
        :param acctGroupId: 账号Id
        :return: 返回AccountGroup对象
        """
        jsonRespObj = self.trading_client.get('/accountgroup/{}'.format(acctGroupId))
        return self._json_object_to_class_object(jsonRespObj, AccountGroup, is_list=False)

    def get_account_group_active_accounts(self, acctGroupId):
        """
        查询指定账号组内当前实时在线的账号
        :param acctGroupId: 账号Id
        :return: 返回Accounts对象
        """
        jsonRespObj = self.trading_client.get('/accountgroup/{}/activeaccounts'.format(acctGroupId))
        acctList = self._json_object_to_class_object(jsonRespObj['accounts'], Account, is_list=True)
        finalAccts = Accounts(acctList)
        return finalAccts

    def get_account_group_balance(self, acctGroupId):
        """
        查询指定账号组的账号余额
        :param acctId: 账号组Id
        :return: 返回一个AccountGroupBalance
        """
        jsonRespObj = self.trading_client.get('/accountgroup/{}/balance'.format(acctGroupId))
        acctBalance = self._json_object_to_class_object(jsonRespObj['balance'], AccountBalance, is_list=False)
        finalAcctGroupBalance = AccountGroupBalance(jsonRespObj['activeAccounts'], jsonRespObj['activeSubAccounts'],acctBalance);
        return finalAcctGroupBalance

    def get_account_group_positions(self, acctGroupId):
        """
        查询指定账号组的持仓
        :param acctId: 账号组Id
        :return: 返回一个AccountGroupPositions
        """
        jsonRespObj = self.trading_client.get('/accountgroup/{}/positions'.format(acctGroupId))
        positionList = self._json_object_to_class_object(jsonRespObj['positions'], Position, is_list=True)
        acctGroupPositions = AccountGroupPositions(jsonRespObj['activeAccounts'], jsonRespObj['activeSubAccounts'], positionList );
        return acctGroupPositions

    def post_cash_transfer_in(self, cashTransferReq):
        """
        向账号转入资金
        :param cashTransferReq: 资金转入的请求对象
        :return: 返回一个CommonResponse, content的内容是转账的结果
        """
        data = json.dumps(cashTransferReq.__dict__)
        jsonRespObj = self.trading_client.post('/transfer/cash/in', None, data = data)
        return self._json_object_to_class_object(jsonRespObj, CommonResponse, is_list=False)

    def post_cash_transfer_out(self, cashTransferReq):
        """
        从账号转出资金
        :param cashTransferReq: 资金转出的请求对象
        :return: 返回一个CommonResponse, content的内容是转账的结果
        """
        data = json.dumps(cashTransferReq.__dict__)
        jsonRespObj = self.trading_client.post('/transfer/cash/out', None, data = data)
        return self._json_object_to_class_object(jsonRespObj, CommonResponse, is_list=False)

    def post_stock_transfer_in(self, stockTransferReq):
        """
        向账号转入股票
        :param stockTransferReq: 股票转入的请求对象
        :return: 返回一个CommonResponse, content的内容是转账的结果
        """
        data = json.dumps(stockTransferReq.__dict__)
        jsonRespObj = self.trading_client.post('/transfer/stock/in', None, data = data)
        return self._json_object_to_class_object(jsonRespObj, CommonResponse, is_list=False)

    def post_stock_transfer_out(self, stockTransferReq):
        """
        从账号转出股票
        :param stockTransferReq: 股票转出的请求对象
        :return: 返回一个CommonResponse, content的内容是转账的结果
        """
        data = json.dumps(stockTransferReq.__dict__)
        jsonRespObj = self.trading_client.post('/transfer/stock/out', None, data = data)
        return self._json_object_to_class_object(jsonRespObj, CommonResponse, is_list=False)

    def get_smart_order_policies(self):
        """
        查询智能下单策略
        :return: 返回一个SmartOrderPolicies
        """
        jsonRespObj = self.trading_client.get('/smartorderpolicies/all')
        sopList = self._json_object_to_class_object(jsonRespObj['smartOrderPolicies'], SmartOrderPolicy, is_list=True)
        formattedSopList = []
        for sop in sopList:
            qtyPolicy = QuantityPolicy()
            qtyPolicy.__dict__.update(sop.quantityPolicy)
            pricePolicy = PricePolicy()
            pricePolicy.__dict__.update(sop.pricePolicy)
            schPolicy = SchedulePolicy()
            schPolicy.__dict__.update(sop.schedulePolicy)
            newSop = SmartOrderPolicy(sop.id, pricePolicy, qtyPolicy, schPolicy)
            formattedSopList.append(newSop)
        finalSops = SmartOrderPolicies(formattedSopList)
        return finalSops


    def get_smart_order_policy(self, smartOrderPolicyId):
        """
        查询特定的智能下单策略
        :param smartOrderPolicyId: 特定的智能下单策略的Id
        :return: 返回一个SmartOrderPolicy
        """
        jsonRespObj = self.trading_client.get('/smartorderpolicy/{}'.format(smartOrderPolicyId))
        sop = self._json_object_to_class_object(jsonRespObj, SmartOrderPolicy, is_list=False)
        qtyPolicy = QuantityPolicy()
        qtyPolicy.__dict__.update(sop.quantityPolicy)
        pricePolicy = PricePolicy()
        pricePolicy.__dict__.update(sop.pricePolicy)
        schPolicy = SchedulePolicy()
        schPolicy.__dict__.update(sop.schedulePolicy)
        finalSop = SmartOrderPolicy(sop.id, pricePolicy, qtyPolicy, schPolicy)
        return finalSop

    def get_ipo_account_available_stocks(self, acctId):
        """
        查询指定账号的IPO可申购新股
        :param acctId: 账号Id
        :return: 返回一个IPOStocks
        """
        jsonRespObj = self.trading_client.get('/ipo/account/{}/availablestocks'.format(acctId))
        stockList = self._json_object_to_class_object(jsonRespObj['stocks'], IPOStock, is_list=True)
        finalIpoStocks = IPOStocks(stockList)
        return finalIpoStocks

    def get_ipo_account_equity(self, acctId):
        """
        查询指定账号的IPO可申购新股的权益
        :param acctId: 账号Id
        :return: 返回一个Equities
        """
        jsonRespObj = self.trading_client.get('/ipo/account/{}/equities'.format(acctId))
        equityList = self._json_object_to_class_object(jsonRespObj['equities'], Equity, is_list=True)
        finalEquities = Equities(equityList)
        return finalEquities

    def get_ipo_allocated_stocks(self, acctId):
        """
        查询指定账号的IPO的新股中签
        :param acctId: 账号Id
        :return: 返回一个IPOStocks
        """
        jsonRespObj = self.trading_client.get('/ipo/account/{}/allocatedstocks'.format(acctId))
        stockList = self._json_object_to_class_object(jsonRespObj['stocks'], IPOStock, is_list=True)
        finalIpoStocks = IPOStocks(stockList)
        return finalIpoStocks

    def get_ipo_allocated_numbers(self, acctId):
        """
        查询指定账号的IPO的新股配号
        :param acctId: 账号Id
        :return: 返回一个AllocatedNumbers
        """
        jsonRespObj = self.trading_client.get('/ipo/account/{}/allocatednumbers'.format(acctId))
        allocNumbsList = self._json_object_to_class_object(jsonRespObj['allocatedNumbers'], AllocatedNumber, is_list=True)
        finalAllocNumbs = AllocatedNumbers(allocNumbsList)
        return finalAllocNumbs

    def get_account_parent_orders(self, acctId):
        """
        查询账号/子账号的订单
        :param acctId: 账号Id
        :return: 返回一个ParentOrders
        """
        jsonRespObj = self.trading_client.get('/orders/account/{}/created'.format(acctId))
        pOrdersList = self._json_object_to_class_object(jsonRespObj['parentOrders'], ParentOrder, is_list=True)
        formattedPoList = []
        for pOrder in pOrdersList:
            chdOrderObjs = self._json_object_to_class_object(pOrder.childOrders, ChildOrder, is_list=True)
            pOrder.childOrders = chdOrderObjs
            formattedPoList.append(pOrder)
        finalPOs = ParentOrders(formattedPoList)
        return finalPOs

    def get_account_parent_orders_with_date_ranges(self, acctId, startDate, endDate):
        """
        查询账号/子账号的订单
        :param acctId: 账号Id
        :param startDate: 启始时间,格式：20180801
        :param endDate: 结束时间,格式：20180805
        :return: 返回一个ParentOrders
        """
        jsonRespObj = self.trading_client.get('/orders/account/{}/created/startdate/{}/enddate/{}'.format(acctId, startDate, endDate))
        pOrdersList = self._json_object_to_class_object(jsonRespObj['parentOrders'], ParentOrder, is_list=True)
        formattedPoList = []
        for pOrder in pOrdersList:
            chdOrderObjs = self._json_object_to_class_object(pOrder.childOrders, ChildOrder, is_list=True)
            pOrder.childOrders = chdOrderObjs
            formattedPoList.append(pOrder)
        finalPOs = ParentOrders(formattedPoList)
        return finalPOs

    def get_account_group_parent_orders(self, acctGroupId):
        """
        查询账号/子账号的订单
        :param acctGroupId: 账号组Id
        :return: 返回一个ParentOrders
        """
        jsonRespObj = self.trading_client.get('/orders/accountgroup/{}/created'.format(acctGroupId))
        pOrdersList = self._json_object_to_class_object(jsonRespObj['parentOrders'], ParentOrder, is_list=True)
        formattedPoList = []
        for pOrder in pOrdersList:
            chdOrderObjs = self._json_object_to_class_object(pOrder.childOrders, ChildOrder, is_list=True)
            pOrder.childOrders = chdOrderObjs
            formattedPoList.append(pOrder)
        finalPOs = ParentOrders(formattedPoList)
        return finalPOs

    def get_account_group_parent_orders_with_date_ranges(self, acctGroupId, startDate, endDate):
        """
        查询账号/子账号的订单
        :param acctGroupId: 账号组Id
        :param startDate: 启始时间,格式：20180801
        :param endDate: 结束时间,格式：20180805
        :return: 返回一个ParentOrders
        """
        jsonRespObj = self.trading_client.get('/orders/accountgroup/{}/created/startdate/{}/enddate/{}'.format(acctGroupId, startDate, endDate))
        pOrdersList = self._json_object_to_class_object(jsonRespObj['parentOrders'], ParentOrder, is_list=True)
        formattedPoList = []
        for pOrder in pOrdersList:
            chdOrderObjs = self._json_object_to_class_object(pOrder.childOrders, ChildOrder, is_list=True)
            pOrder.childOrders = chdOrderObjs
            formattedPoList.append(pOrder)
        finalPOs = ParentOrders(formattedPoList)
        return finalPOs

    def get_account_all_orders(self, acctId):
        """
        查询指定账号的当日委托
        :param acctId: 账号Id
        :return: 返回一个Orders
        """
        jsonRespObj = self.trading_client.get('/orders/account/{}/all'.format(acctId))
        ordersList = self._json_object_to_class_object(jsonRespObj['orders'], Order, is_list=True)
        finalOrders = Orders(ordersList)
        return finalOrders

    def get_account_opened_orders(self, acctId):
        """
        查询指定账号的当日可撤订单
        :param acctId: 账号Id
        :return: 返回一个Orders
        """
        jsonRespObj = self.trading_client.get('/orders/account/{}/opened'.format(acctId))
        ordersList = self._json_object_to_class_object(jsonRespObj['orders'], Order, is_list=True)
        finalOrders = Orders(ordersList)
        return finalOrders

    def get_account_filled_orders(self, acctId):
        """
        查询指定账号的当日成交订单
        :param acctId: 账号Id
        :return: 返回一个Orders
        """
        jsonRespObj = self.trading_client.get('/orders/account/{}/filled'.format(acctId))
        ordersList = self._json_object_to_class_object(jsonRespObj['orders'], Order, is_list=True)
        finalOrders = Orders(ordersList)
        return finalOrders

    def get_account_history_orders(self, acctId):
        """
        查询指定账号的历史订单
        :param acctId: 账号Id
        :return: 返回一个Orders
        """
        jsonRespObj = self.trading_client.get('/orders/account/{}/history'.format(acctId))
        ordersList = self._json_object_to_class_object(jsonRespObj['orders'], Order, is_list=True)
        finalOrders = Orders(ordersList)
        return finalOrders

    def post_place_parent_order(self, placeParentOrderReq):
        """
        下母单
        :param placeParentOrderReq: 下母单的请求
        :return: 返回一个PlaceOrderResponse, orderId的内容是订单Id
        """
        data = json.dumps(placeParentOrderReq.__dict__)
        jsonRespObj = self.trading_client.post('/order/placeorder', None, data = data)
        return self._json_object_to_class_object(jsonRespObj, ParentOrderResponse, is_list=False)

    def post_parent_order_execution_plan(self, placeParentOrderReq):
        """
        查看母单的执行计划
        :param placeParentOrderReq: 下母单的请求
        :return: 返回一个CommonResponse, content的内容是执行计划
        """
        data = json.dumps(placeParentOrderReq.__dict__)
        jsonRespObj = self.trading_client.post('/order/executionplan', None, data = data)
        return self._json_object_to_class_object(jsonRespObj, CommonResponse, is_list=False)

    def get_parent_order_status(self, orderId):
        """
        查询指定订单的状态
        :param acctId: 订单Id
        :return: 返回一个ParentOrder
        """
        jsonRespObj = self.trading_client.get('/order/{}/status'.format(orderId))
        pOrder = self._json_object_to_class_object(jsonRespObj, ParentOrder, is_list=False)
        chdOrderObjs = self._json_object_to_class_object(pOrder.childOrders, ChildOrder, is_list=True)
        pOrder.childOrders = chdOrderObjs
        return pOrder

    def cancel_parent_order(self, orderId):
        """
        撤销指定的订单
        :param acctId: 订单Id
        :return: 返回一个ParentOrderResponse
        """
        jsonRespObj = self.trading_client.delete('/order/{}'.format(orderId))
        return self._json_object_to_class_object(jsonRespObj, ParentOrderResponse, is_list=False)


    def cancel_account_all_orders(self, acctId):
        """
        撤销指定账号内所有的订单
        :param acctId: 账号Id
        :return: 返回一个返回一个CommonResponse, content的内容是撤销的结果
        """
        jsonRespObj = self.trading_client.delete('/orders/account/{}/all'.format(acctId))
        return self._json_object_to_class_object(jsonRespObj, CommonResponse, is_list=False)

    def cancel_account_all_buy_orders(self, acctId):
        """
        撤销指定账号内所有的买单
        :param acctId: 账号Id
        :return: 返回一个返回一个CommonResponse, content的内容是撤销的结果
        """
        jsonRespObj = self.trading_client.delete('/orders/account/{}/buy'.format(acctId))
        return self._json_object_to_class_object(jsonRespObj, CommonResponse, is_list=False)

    def cancel_account_all_sell_orders(self, acctId):
        """
        撤销指定账号内所有的卖单
        :param acctId: 账号Id
        :return: 返回一个返回一个CommonResponse, content的内容是撤销的结果
        """
        jsonRespObj = self.trading_client.delete('/orders/account/{}/sell'.format(acctId))
        return self._json_object_to_class_object(jsonRespObj, CommonResponse, is_list=False)

    def cancel_account_all_orders_by_symbol(self, acctId, symbol):
        """
        撤销指定账号内所有的指定股票代码的订单
        :param acctId: 账号Id
        :param symbol: 股票代码
        :return: 返回一个返回一个CommonResponse, content的内容是撤销的结果
        """
        jsonRespObj = self.trading_client.delete('/orders/account/{}/symbol/{}/all'.format(acctId, symbol))
        return self._json_object_to_class_object(jsonRespObj, CommonResponse, is_list=False)

    def cancel_account_all_buy_orders_by_symbol(self, acctId, symbol):
        """
        撤销指定账号内所有的指定股票代码的买单
        :param acctId: 账号Id
        :param symbol: 股票代码
        :return: 返回一个返回一个CommonResponse, content的内容是撤销的结果
        """
        jsonRespObj = self.trading_client.delete('/orders/account/{}/symbol/{}/buy'.format(acctId, symbol))
        return self._json_object_to_class_object(jsonRespObj, CommonResponse, is_list=False)

    def cancel_account_all_sell_orders_by_symbol(self, acctId, symbol):
        """
        撤销指定账号内所有的指定股票代码的卖单
        :param acctId: 账号Id
        :param symbol: 股票代码
        :return: 返回一个返回一个CommonResponse, content的内容是撤销的结果
        """
        jsonRespObj = self.trading_client.delete('/orders/account/{}/symbol/{}/sell'.format(acctId, symbol))
        return self._json_object_to_class_object(jsonRespObj, CommonResponse, is_list=False)

    def cancel_account_orders_by_contract_no(self, acctId, contractNo):
        """
        撤销指定账号内所有的指定股票代码的卖单
        :param acctId: 账号Id
        :param contractNo: 委托编号/合同号码
        :return: 返回一个返回一个CommonResponse, content的内容是撤销的结果
        """
        jsonRespObj = self.trading_client.delete('/orders/account/{}/contractno/{}'.format(acctId, contractNo))
        return self._json_object_to_class_object(jsonRespObj, CommonResponse, is_list=False)


# -------------------------------------------
if __name__ == "__main__":
    print()
    # tradingApi = TradingApi("http://localhost:8080/", "xx", "xx");
    # controllers = tradingApi.getAllController();
    # print(controllers)
    # reloadTraderResp = tradingApi.post_reload_trader('cid-002');
    # loginTraderResponse = tradingApi.post_login_trader('cid-002',loginTraderReq );
    # activeAccountInTrader = tradingApi.get_active_account_in_trader('cid-001');
    # print(activeAccountInTrader)
    # accts = tradingApi.get_accounts();
    # closeTraderResp = tradingApi.deleteCloseTrader('cid-001');
    # print(accts.accounts)
    # activeAccts = tradingApi.get_active_accounts();
    # print(activeAccts.accounts)
    # acct = tradingApi.get_account('Account-0001');
    # print(acct)
    # acctBalance = tradingApi.get_account_balance('Account-0002');
    # print(acctBalance)
    # acctPositions = tradingApi.get_account_positions('Account-0002');
    # print(acctPositions.positions)
    # # shareholders = tradingApi.get_account_shareholders('Account-0002');
    # # print(shareholders.shareholders)
    # acctGroups = tradingApi.get_account_groups();
    # print(acctGroups.accountGroups)
    # acctGroup = tradingApi.get_account_group('AccountGroup-0001');
    # print(acctGroup)
    # acctGroupAA = tradingApi.get_account_group_active_accounts('AccountGroup-0002');
    # print(acctGroupAA.accounts)
    # acctGroupBalance = tradingApi.get_account_group_balance('AccountGroup-0002');
    # print(acctGroupBalance)
    # acctGroupPositions = tradingApi.get_account_group_positions('AccountGroup-0002');
    # print(acctGroupPositions.positions)
    # cashTransferReq = CashTransferReq('SubAccount-0001',100, False)
    # cashTransferResp = tradingApi.post_cash_transfer_in(cashTransferReq);
    # print(cashTransferResp)
    # cashTransferReq = CashTransferReq('SubAccount-0001',100, False)
    # cashTransferResp = tradingApi.post_cash_transfer_out(cashTransferReq);
    # print(cashTransferResp)
    # stockTransferReq = StockTransferReq('SubAccount-0001','600022', 1.90, 100, False)
    # stockTransferResp = tradingApi.post_stock_transfer_in(stockTransferReq);
    # print(stockTransferResp)
    # stockTransferReq = StockTransferReq('SubAccount-0001','600022', 1.90, 100, False)
    # stockTransferResp = tradingApi.post_stock_transfer_out(stockTransferReq);
    # print(stockTransferResp)
    # sops = tradingApi.get_smart_order_policies();
    # sop = tradingApi.get_smart_order_policy('SOP-001');
    # print(sop.id)
    # ipoAvailStocks = tradingApi.get_ipo_account_available_stocks('Account-0002')
    # ipoAllocStocts = tradingApi.get_ipo_allocated_stocks('Account-0002')
    # ipoAllocNumbs = tradingApi.get_ipo_allocated_numbers('Account-0002')
    # acctPOs = tradingApi.get_account_parent_orders('Account-0002')
