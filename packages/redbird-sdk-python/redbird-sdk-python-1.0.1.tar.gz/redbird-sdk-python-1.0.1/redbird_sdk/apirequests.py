#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019-2020 wesley wu

from enum import Enum

from .apiresponses import RedBirdObject
from .rb_utils import *


class LoginTraderReq(RedBirdObject):
    """
    登录交易软件的请求对象
    """
    def __init__(self, brokerages, accountNo,tradePasswd, CommPasswd):
        """
        初始化函数
        :param brokerages: 开户券商
        :param accountNo: 登录客户号/资金账号
        :param tradePasswd: 交易密码
        :param CommPasswd: 通讯密码(通达信可不填)
        """
        self.brokerages = brokerages
        self.accountNo = accountNo
        self.tradePasswd = tradePasswd
        self.CommPasswd = CommPasswd


class Side(Enum):
    """
    下单的方向
    """
    BUY = 'BUY'
    SELL = 'SELL'


class OrderType(Enum):
    """
    订单的类型
    """
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'


class PlaceOrderReq(RedBirdObject):
    """
    下订单请求
    """

    def __init__(self, seqid=None, symbol=None, side=None, orderType=None, priceType=1, price=None, quantity=None):
        """
        母订单对象初始化
        :param seqid:客户端自定义的下单号码，避免订单重复
        :param symbol:股票代码
        :param side:买卖方向
        :param orderType:订单类型,LIMIT, MARKET
        :SH：0:五档即成剩余撤单 ； 1：五档即成剩余转限价
        :SZ: 0:对方最优价格 ； 1：本方最优价格； 2：即时成交剩余撤单；3：五档即成剩余撤单； 4：全额成交或撤销
        :param priceType:价格类型,
        :param price:委托价格
        :param quantity:委托数量
        """
        self.seqid = seqid
        self.symbol = symbol
        self.side = side
        self.orderType = orderType
        if self.orderType == OrderType.MARKET.name:
            self.priceType = str_to_int(priceType)
            self.price = -1
        else:
            self.priceType = None
            self.price = str_to_float(price)
        self.quantity = str_to_int(quantity)


class PlaceParentOrderReq(RedBirdObject):
    """
    下母订单请求
    """
    def __init__(self, seqid=None, symbol=None, side=None, orderType=None, priceType=0,  accountGroup=None,
                 account=None, price=None, safePrice=None, quantity=None, safeQuantity=None,
                 smartOrderPolicy=None, startTime=None, expirationTime=None):
        """
        母订单对象初始化
        :param seqid:客户端自定义的下单号码，避免订单重复
        :param symbol:股票代码
        :param side:买卖方向
        :param orderType:订单类型
        :param priceType:价格类型
        :param accountGroup:账号组
        :param account:账号
        :param price:委托价格
        :param safePrice:安全价格上限
        :param quantity:委托数量
        :param safeQuantity:安全数量上限
        :param filledQuantity:成交数量
        :param smartOrderPolicy:智能订单策略
        :param startTime:订单执行时间
        :param expirationTime:订单过期时间
        """
        self.seqid = seqid
        self.symbol = symbol
        self.side = side
        self.orderType = orderType
        self.priceType = str_to_int(priceType)
        self.accountGroup = accountGroup
        self.account = account
        self.price = str_to_float(price)
        self.safePrice = str_to_float(safePrice)
        self.quantity = str_to_int(quantity)
        self.safeQuantity = str_to_int(safeQuantity)
        self.smartOrderPolicy = smartOrderPolicy
        self.startTime = startTime
        self.expirationTime = expirationTime


class SetActiveAccountReq(RedBirdObject):
    """
    在交易软件上设置活跃用户
    """
    def __init__(self, account=None):
        """
        初始化函数
        :param account: 可以定位账号的关键字符串
        """
        self.account = account


class CashTransferReq(RedBirdObject):
    """
    子账号现金转账请求
    """
    def __init__(self, subAccount=None, quantity=None, verify=None,):
        """
        初始化
        :param subAccount:子账号Id
        :param quantity:金额
        :param verify:是否需要校验,,转入时验证母账号,转出时验证子账号
        """
        self.subAccount = subAccount
        self.quantity = str_to_float(quantity)
        self.verify = verify


class StockTransferReq(RedBirdObject):
    """
    子账号股票转账请求
    """
    def __init__(self, subAccount=None, symbol=None, price=None, quantity=None, verify=None,):
        """
        初始化
        :param subAccount:子账号Id
        :param symbol:股票代码
        :param price:转出的价格
        :param quantity:数量
        :param verify:是否需要校验,,转入时验证母账号,转出时验证子账号
        """
        self.subAccount = subAccount
        self.symbol = symbol
        self.price = str_to_float(price)
        self.quantity = str_to_int(quantity)
        self.verify = verify