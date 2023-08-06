#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019-2020 wesley wu

try: import simplejson as json
except ImportError: import json


class RedBirdObject(object):
    """Base RedBird Response Object."""

    def __repr__(self):
        return "{clazz}::{obj}".format(clazz=self.__class__.__name__, obj=self.to_json())

    def __eq__(self, other):
        try:
            return self.__dict__ == other.__dict__
        except Exception:
            return False

    def __hash__(self):
        # Technically this class shouldn't be hashable because it often
        # contains mutable fields, but in practice this class is used more
        # like a record or namedtuple.
        return hash(self.to_json())

    def json_repr(self, minimal=False):
        """Construct a JSON-friendly representation of the object.

        :param bool minimal: Construct a minimal representation of the object (ignore nulls and empty collections)

        :rtype: dict
        """
        if minimal:
            return {k: v for k, v in vars(self).items() if (v or v is False or v == 0)}
        else:
            return {k: v for k, v in vars(self).items()}

    @classmethod
    def from_json(cls, attributes):
        """从返回的Json数据中构建指定的对象实例.

        :param dict attributes: object attributes from parsed response
        """
        return cls(**{k: v for k, v in attributes.items()})

    def to_json(self):
        """Encode an object as a JSON string.

        :param bool minimal: Construct a minimal representation of the object (ignore nulls and empty collections)

        :rtype: str
        """
        return json.dumps(self.json_repr(), sort_keys=True)


class obj(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, obj(b) if isinstance(b, dict) else b)


class CommonResponse(RedBirdObject):
    """
    通用的回复对象
    """
    def __init__(self, content):
        """
        通用的对象初始化
        :param content:返回的内容
        """
        self.content = content


class Controller(RedBirdObject):
    """
    控制器查询的回复对象
    """
    def __init__(self, controllerId, ipPort):
        """
        控制器的对象初始化
        :param controllerId:控制器Id
        :param ipPort:IP以及端口
        """
        self.controllerId = controllerId
        self.ipPort = ipPort


class Controllers(RedBirdObject):
    """
    控制器列表
    """
    def __init__(self, controllers=None):
        """
        控制器列表对象初始化
        :param controllers:控制器列表
        """
        self.controllers = controllers;


class TraderStatus(RedBirdObject):
    """
    交易软件的运行状态的回复对象
    """
    def __init__(self, status, processID):
        """
        交易软件的运行状态的对象初始化
        :param status:运行状态
        :param processID:进程Id
        """
        self.status = status
        self.processID = processID


class ActiveAccount(RedBirdObject):
    """
    交易软件的当前账号
    """
    def __init__(self, account):
        """
        交易软件的当前账号对象初始化
        :param account: 当前实时在线的用户名称
        """
        self.account = account


class Account(RedBirdObject):
    """
    账号
    """
    def __init__(self, id=None, parentId=None, brokerages=None, accountNo=None, weightInBuy=None, weightInSell=None,
                maximumBuyPerOrder=None, maximumSellPerOrder=None, priorityInBuy=None, priorityInSell=None, scaleFactorInBuy=None,
                scaleFactorInSell=None, matchKeywords=None, isActive=None, controllerId=None):

        """
        账号信息对象初始化
        :param id: 账号的Id
        :param parentId:账号所属的母账号的Id,适用于子账号
        :param brokerages:开户的证券公司
        :param accountNo:客户号或者资金账号
        :param weightInBuy:在所属的账号组内进行买入时所占的权重比例
        :param weightInSell:在所属的账号组内进行卖出时所占的权重比例
        :param maximumBuyPerOrder:每笔买入订单最大的限额,超过这个限额系统将会自动将该订单拆分成小的订单
        :param maximumSellPerOrder:每笔卖出订单最大的限额,超过这个限额系统将会自动将该订单拆分成小的订单
        :param priorityInBuy:在所属的账号组内进行买入的订单拆分时所处的优先级,数值越小优先级越高
        :param priorityInSell:在所属的账号组内进行买出的订单拆分时时所处的优先级,数值越小优先级越高
        :param scaleFactorInBuy:在所属的账号组内进行买入的订单跟单时订单数量扩大的比例
        :param scaleFactorInSell:在所属的账号组内进行买出的订单跟单时订单数量扩大的比例
        :param matchKeywords:用于匹配该账号在交易软件内的名称和本系统中的配置
        :param isActive:该账号是否实时在线
        :param controllerId:该账号关联的控制器Id
        """
        self.id = id
        self.parentId = parentId
        self.brokerages = brokerages
        self.accountNo = accountNo
        self.weightInBuy = weightInBuy
        self.weightInSell = weightInSell
        self.maximumBuyPerOrder = maximumBuyPerOrder
        self.maximumSellPerOrder = maximumSellPerOrder
        self.priorityInBuy = priorityInBuy
        self.priorityInSell = priorityInSell
        self.scaleFactorInBuy = scaleFactorInBuy
        self.scaleFactorInSell = scaleFactorInSell
        self.matchKeywords = matchKeywords
        self.isActive = isActive
        self.controllerId = controllerId


class Accounts(RedBirdObject):
    """
    账户列表
    """
    def __init__(self, accounts=None):
        """
        账户列表对象初始化
        :param accounts:账户列表
        """
        self.accounts = accounts;


class AccountBalance(RedBirdObject):
    """
    账户余额
    """
    def __init__(self, cashBalance=None, transferableCash=None, availableCash=None, lockedCash=None, marketValue=None,
                 netValue=None, pnl=None):
        """
        账户余额对象初始化
        :param cashBalance:现金余额
        :param transferableCash:可转账余额
        :param availableCash:可用余额
        :param lockedCash:冻结资金
        :param marketValue:市值
        :param netValue:总资产
        :param pnl:损益
        """
        self.cashBalance = cashBalance;
        self.transferableCash = transferableCash;
        self.availableCash = availableCash;
        self.lockedCash = lockedCash;
        self.marketValue = marketValue;
        self.netValue = netValue;
        self.pnl = pnl;


class Position(RedBirdObject):
    """
    账号持仓
    """
    def __init__(self, symbol=None, price=None, quantity=None, closeableQuantity=None, lockedQuantity=None, costPrice=None,
                 marketValue=None, pnl=None, pnlPercentage=None, holdingDays=None):
        """
        账号持仓对象初始化
        :param symbol:股票代码
        :param price:现价
        :param quantity:持仓数量
        :param closeableQuantity:可卖数量
        :param lockedQuantity:冻结的数量
        :param costPrice:成本价
        :param marketValue:市值
        :param pnl:损益
        :param pnlPercentage:损益百分比
        :param holdingDays:持股天数
        """
        self.symbol = symbol
        self.price = price
        self.quantity = quantity
        self.closeableQuantity = closeableQuantity
        self.lockedQuantity = lockedQuantity
        self.costPrice = costPrice
        self.marketValue = marketValue
        self.pnl = pnl
        self.pnlPercentage = pnlPercentage
        self.holdingDays = holdingDays


class Positions(RedBirdObject):
    """
    账号持仓
    """
    def __init__(self, positions=None):
        """
        账号持仓对象初始化
        :param positions:账户持仓列表
        """
        self.positions = positions


class AccountGroup(RedBirdObject):
    """
    账户组
    """
    def __init__(self, id=None,  accounts=None, subAccounts=None):
        """
        账户组对象初始化
        :param id:id
        :param activeAccounts:账号组内实时在线的账号Id列表
        :param activeSubAccounts:账号组内实时在线的子账号Id列表
        """
        self.id = id;
        self.accounts = accounts;
        self.subAccounts = subAccounts;


class AccountGroups(RedBirdObject):
    """
    账户组列表
    """
    def __init__(self, accountGroups=None):
        """
        账户组列表对象初始化
        :param accountGroups:账户组列表
        """
        self.accountGroups = accountGroups;


class AccountGroupBalance(RedBirdObject):
    """
    账户组账户余额
    """
    def __init__(self, activeAccounts=None, activeSubAccounts=None, balance=None):
        """
        账户组账户余额对象初始化
        :activeAccounts:实时在线的账号列表
        :activeSubAccounts:实时在线的子账号列表
        :balance:资金余额
        """
        self.activeAccounts = activeAccounts
        self.activeSubAccounts = activeSubAccounts
        self.balance = balance


class AccountGroupPositions(RedBirdObject):
    """
    账户组持仓
    """
    def __init__(self, activeAccounts=None, activeSubAccounts=None, positions=None):
        """
        账户组持仓对象初始化
        :activeAccounts:实时在线的账号列表
        :activeSubAccounts:实时在线的子账号列表
        :positions:账户组持仓
        """
        self.activeAccounts = activeAccounts
        self.activeSubAccounts = activeSubAccounts
        self.positions = positions


class Order(RedBirdObject):
    """
    订单
    """
    def __init__(self, symbol=None, name=None, price=None, side=None, quantity=None, addTime=None,
                 filledQuantity=None, filledPrice=None, filledTime=None, status=None, settlementFund=None,
                 contractNo=None):
        """
        订单对象初始化
        :param symbol:股票代号
        :param name:股票名称
        :param price:股票价格
        :param side:买卖方向
        :param quantity:委托数量
        :param addTime:委托时间
        :param filledQuantity:成交数量
        :param filledPrice:成交价格
        :param filledTime:成交时间
        :param status:订单状态
        :param settlementFund:清算金额
        :param contractNo:委托编号、申请编号
        """
        self.symbol = symbol
        self.name = name
        self.price = price
        self.side = side
        self.quantity = quantity
        self.addTime = addTime
        self.filledQuantity = filledQuantity
        self.filledPrice = filledPrice
        self.filledTime = filledTime
        self.status = status
        self.settlementFund = settlementFund
        self.contractNo = contractNo


class Orders(RedBirdObject):
    """
    订单列表
    """
    def __init__(self, orders=None):
        """
        订单列表对象初始化
        :param orders:订单列表
        """
        self.orders = orders


class ChildOrder(RedBirdObject):
    """
    子订单
    """
    def __init__(self, id=None, parentId=None, account=None, subAccount=None, symbol=None, name=None, price=None, side=None,
                 quantity=None, addTime=None,filledQuantity=None, filledPrice=None, filledTime=None, status=None,
                 contractNo=None, shareholderNo = None, createdTime = None, updatedTime = None, error = None ):
        """
        子订单对象初始化
        :param id:子订单Id
        :param parentId:母订单Id
        :param account:账号Id
        :param subAccount:子账号Id
        :param symbol:股票代码
        :param name:股票名称
        :param price:股票价格
        :param side:买卖方向
        :param quantity:委托数量
        :param addTime:委托时间
        :param filledQuantity:成交数量
        :param filledPrice:成交价格
        :param filledTime:成交时间
        :param status:订单状态
        :param contractNo:委托编号
        :param shareholderNo:股东代码
        :param createdTime:订单创建时间
        :param updatedTime:订单状态更新时间
        :param error:订单的错误信息
        """
        self.id = id
        self.parentId = parentId
        self.account = account
        self.subAccount = subAccount
        self.symbol = symbol
        self.name = name
        self.price = price
        self.side = side
        self.quantity = quantity
        self.addTime = addTime
        self.filledQuantity = filledQuantity
        self.filledPrice = filledPrice
        self.filledTime = filledTime
        self.status = status
        self.contractNo = contractNo
        self.shareholderNo = shareholderNo
        self.createdTime = createdTime
        self.updatedTime = updatedTime
        self.error = error


class ParentOrder(RedBirdObject):
    """
    母订单
    """
    def __init__(self, id=None, seqid=None, symbol=None, side=None, orderType=None, priceType=None,  accountGroup=None,
                 account=None, price=None, safePrice=None,filledPrice=None, quantity=None, safeQuantity=None,
                 filledQuantity=None, smartOrderPolicy=None, startTime=None, expirationTime=None, status=None,
                 createdTime=None, updatedTime = None,  childOrders = None):
        """
        母订单对象初始化
        :param id:母订单Id
        :param seqid:客户端自定义的下单号码，避免订单重复
        :param symbol:股票代码
        :param side:买卖方向
        :param orderType:订单类型
        :param priceType:价格类型
        :param accountGroup:账号组
        :param account:账号
        :param price:委托价格
        :param safePrice:安全价格上限
        :param filledPrice:成交价格
        :param quantity:委托数量
        :param safeQuantity:安全数量上限
        :param filledQuantity:成交数量
        :param smartOrderPolicy:智能订单策略
        :param startTime:订单执行时间
        :param expirationTime:订单过期时间
        :param status:订单状态
        :param createdTime:订单创建时间
        :param updatedTime:订单状态更新时间
        :param childOrders:子订单列表
        """
        self.id = id
        self.seqid = seqid
        self.symbol = symbol
        self.side = side
        self.orderType = orderType
        self.priceType = priceType
        self.accountGroup = accountGroup
        self.account = account
        self.price = price
        self.safePrice = safePrice
        self.filledPrice = filledPrice
        self.quantity = quantity
        self.safeQuantity = safeQuantity
        self.filledQuantity = filledQuantity
        self.smartOrderPolicy = smartOrderPolicy
        self.startTime = startTime
        self.expirationTime = expirationTime
        self.status = status
        self.createdTime = createdTime
        self.updatedTime = updatedTime
        self.childOrders = childOrders


class ParentOrders(RedBirdObject):
    """
    母订单列表对象
    """
    def __init__(self, parentOrders=None):
        """
        母订单列表对象初始化
        :param parentOrders:母订单列表
        """
        self.parentOrders = parentOrders


class ParentOrderResponse(RedBirdObject):
    """
    下母单返回的对象
    """
    def __init__(self, orderId=None):
        """
        母订单列表对象初始化
        :param orderId:母订单Id
        """
        self.orderId = orderId


class IPOStock(RedBirdObject):
    """
    IPO新股
    """
    def __init__(self, symbol=None, name=None, price=None, minimumQuantity=None, maximumQuantity=None, quantity=None
                 , minimumAddition=None, issueDate=None):
        """
        股东权益对象初始化
        :param symbol:股票代码
        :param name:股票名称
        :param price:价格
        :param minimumQuantity:申购下限
        :param maximumQuantity:申购上限
        :param quantity:可申数量
        :param minimumAddition:最低追加
        :param issueDate:发行日期
        """
        self.symbol = symbol
        self.name = name
        self.price = price
        self.minimumQuantity = minimumQuantity
        self.maximumQuantity = maximumQuantity
        self.quantity = quantity
        self.minimumAddition = minimumAddition
        self.issueDate = issueDate


class IPOStocks(RedBirdObject):
    """
    IPO股票列表对象
    """
    def __init__(self, stocks=None):
        """
        母订单列表对象初始化
        :param stocks:母订单列表
        """
        self.stocks = stocks


class AllocatedStock(RedBirdObject):
    """
    IPO新股中签
    """
    def __init__(self, symbol=None, name=None, price=None, filledQuantity=None, filledFund=None,filledDate=None,
                 clearDate=None, status=None, type=None):
        """
        股东权益对象初始化
        :param symbol:股票代码
        :param name:股票名称
        :param price:价格
        :param filledQuantity:中签数量
        :param filledFund:中签资金
        :param filledDate:中签日期
        :param clearDate:清算日期
        :param status:认购状态
        :param type:类型
        """
        self.symbol = symbol
        self.name = name
        self.price = price
        self.filledQuantity = filledQuantity
        self.filledFund = filledFund
        self.filledDate = filledDate
        self.clearDate = clearDate
        self.status = status
        self.type = type


class AllocatedStocks(RedBirdObject):
    """
    IPO新股中签列表
    """
    def __init__(self, stocks=None):
        """
        IPO新股中签列表对象初始化
        :param stocks:中签股票
        """
        self.stocks = stocks


class AllocatedNumber(RedBirdObject):
    """
    IPO新股配号
    """
    def __init__(self, symbol=None, name=None, type=None, filledQuantity=None, orderId=None,startingNo=None,
                 allocNumbers=None, addDate=None, allocDate=None):
        """
        股东权益对象初始化
        :param symbol:股票代码
        :param name:股票名称
        :param type:类型
        :param filledQuantity:成交数量
        :param orderId:委托编号
        :param startingNo:启始编号
        :param allocNumbers:配号数量
        :param addDate:委托日期
        :param allocDate:分配日期
        """
        self.symbol = symbol
        self.name = name
        self.type = type
        self.filledQuantity = filledQuantity
        self.orderId = orderId
        self.startingNo = startingNo
        self.allocNumbers = allocNumbers
        self.addDate = addDate
        self.allocDate = allocDate


class AllocatedNumbers(RedBirdObject):
    """
    IPO新股中签列表
    """
    def __init__(self, stocks=None):
        """
        IPO新股中签列表对象初始化
        :param stocks:中签股票
        """
        self.stocks = stocks


class Shareholder(RedBirdObject):
    """
    股东信息
    """
    def __init__(self, shareholderNo=None, shareholderName=None, fundAccount=None, seatNo=None, shareholderStatus=None,
                 acctType=None, exchange=None):
        """
        股东信息对象初始化
        :param shareholderNo:股东账号
        :param shareholderName:股东姓名
        :param fundAccount:资金账号
        :param seatNo:席位号
        :param shareholderStatus:股东状态
        :param acctType:账号类型
        :param exchange:交易所名称
        """
        self.shareholderNo = shareholderNo
        self.shareholderName = shareholderName
        self.fundAccount = fundAccount
        self.seatNo = seatNo
        self.shareholderStatus = shareholderStatus
        self.acctType = acctType
        self.exchange = exchange


class Shareholders(RedBirdObject):
    """
    股东信息列表
    """
    def __init__(self, shareholders=None):
        """
        股东信息对象初始化
        :param shareholders:股东信息列表
        """
        self.shareholders = shareholders


class Equity(RedBirdObject):
    """
    股东权益
    """
    def __init__(self, exchange=None, equityNum=None, fundAccount=None, shareholderNo=None):
        """
        股东权益对象初始化
        :param exchange:交易所名称
        :param equityNum:权益数量
        :param fundAccount:资金账号
        :param shareholderNo:股东账号
        """
        self.exchange = exchange
        self.equityNum = equityNum
        self.fundAccount = fundAccount
        self.shareholderNo = shareholderNo


class Equities(RedBirdObject):
    """
    股东权益列表对象
    """
    def __init__(self, equities=None):
        """
        股东权益列表对象初始化
        :param shareholders:股东权益列表
        """
        self.equities = equities



class QuantityPolicy(RedBirdObject):
    """
    智能的数量策略
    """
    def __init__(self, quantityDistributionType=None, copyTypeBetweenAccounts=None, splitTypeBetweenAccounts=None,
                 splitTypeWithinAccount=None, baseQuantityType=None, quantityIncrementType=None,
                 quantityIncrementValue=None):
        """
        智能的数量策略对象初始化
        :param quantityDistributionType:在账号间数量拆分的方式:COPY,SPLIT
        :param copyTypeBetweenAccounts:数量在多个账号之间Copy的模式
        :param splitTypeBetweenAccounts:数量在多个账号之间Split的模式
        :param splitTypeWithinAccount:数量在一个账号内Split的模式
        :param baseQuantityType:基准数量的类型
        :param quantityIncrementType:在基准数量的基础上,数量增加的类型
        :param quantityIncrementValue:在基准数量的基础上,数量增加的值,可+/-
        """
        self.quantityDistributionType = quantityDistributionType;
        self.copyTypeBetweenAccounts = copyTypeBetweenAccounts;
        self.splitTypeBetweenAccounts = splitTypeBetweenAccounts;
        self.splitTypeWithinAccount = splitTypeWithinAccount;
        self.baseQuantityType = baseQuantityType;
        self.quantityIncrementType = quantityIncrementType;
        self.quantityIncrementValue = quantityIncrementValue;


class PricePolicy(RedBirdObject):
    """
    智能的价格策略
    """
    def __init__(self, basePriceType=None, priceIncrementType=None, priceIncrementValue=None):
        """
        智能的价格策略对象初始化
        :param basePriceType:基准价格的类型
        :param priceIncrementType:在基准价格的基础上,价格增加的类型
        :param priceIncrementValue:在基准价格的基础上,价格增加的值,可+/-
        """
        self.basePriceType = basePriceType;
        self.priceIncrementType = priceIncrementType;
        self.priceIncrementValue = priceIncrementValue;


class SchedulePolicy(RedBirdObject):
    """
    智能的调度策略
    """
    def __init__(self, execDelayBtwAccts=None, execIntervalInAcct=None):
        """
        智能的调度策略对象初始化
        :param execDelayBtwAccts:订单在不同账户之间的延迟
        :param execIntervalInAcct:订单在同一账户之间的执行的时间间隔
        """
        self.execDelayBtwAccts = execDelayBtwAccts;
        self.execIntervalInAcct = execIntervalInAcct;


class SmartOrderPolicy(RedBirdObject):
    """
    智能的调度策略
    """
    def __init__(self, id=None, pricePolicy=None, quantityPolicy=None, schedulePolicy=None):
        """
        智能的调度策略对象初始化
        :param id:策略的Id
        :param pricePolicy:智能的价格策略
        :param quantityPolicy:智能的数量策略
        :param schedulePolicy:智能的调度策略
        """
        self.id = id;
        self.pricePolicy = pricePolicy;
        self.quantityPolicy = quantityPolicy;
        self.schedulePolicy = schedulePolicy;


class SmartOrderPolicies(RedBirdObject):
    """
    智能的调度策略的列表对象
    """
    def __init__(self, smartOrderPolicies=None):
        """
        智能的调度策略的列表对象初始化
        :param smartOrderPolicies:智能的调度策略的列表
        """
        self.smartOrderPolicies = smartOrderPolicies
