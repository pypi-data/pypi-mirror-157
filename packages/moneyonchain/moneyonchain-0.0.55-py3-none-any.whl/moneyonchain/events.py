"""
                    GNU AFFERO GENERAL PUBLIC LICENSE
                       Version 3, 19 November 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

 THIS IS A PART OF MONEY ON CHAIN PACKAGE
 by Martin Mulone (martin.mulone@moneyonchain.com)

"""

import logging
from web3 import Web3
from web3.exceptions import BlockNotFound
import datetime

from rich.console import Console
from rich.table import Table


class BaseEvent(object):
    name = "BaseEvent"
    hours_delta = 0

    @staticmethod
    def columns():
        columns = []
        return columns

    def print_row(self):
        print('\t'.join(self.columns()))
        print('\t'.join(str(v) for v in self.row()))

    def print_table(self, info_table=None):

        console = Console()

        d_info_table = dict(
            title='Event: {0}'.format(self.name),
            header_style='bold magenta',
            show_header=True
        )
        if info_table:
            d_info_table = info_table

        table = Table(show_header=d_info_table['show_header'],
                      header_style=d_info_table['header_style'],
                      title=d_info_table['title'])

        for col in self.columns():
            table.add_column(col, no_wrap=True)

        rows = [str(v) for v in self.row()]

        table.add_row(*rows)

        console.print(table)


class MoCExchangeRiskProMint(BaseEvent):

    name = "RiskProMint"

    def __init__(self, connection_manager, event):

        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt #dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None
        self.account = event['args']['account']
        self.amount = event['args']['amount']
        self.reserveTotal = event['args']['reserveTotal']
        self.commission = event['args']['commission']
        self.reservePrice = event['args']['reservePrice']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'Account', 'Amount', 'reserveTotal', 'commission', 'reservePrice']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['account'] = self.account
        d_event['amount'] = Web3.fromWei(self.amount, 'ether')
        d_event['reserveTotal'] = Web3.fromWei(self.reserveTotal, 'ether')
        d_event['commission'] = Web3.fromWei(self.commission, 'ether')
        d_event['reservePrice'] = Web3.fromWei(self.reservePrice, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['account'],
                format(float(d_event['amount']), '.18f'),
                format(float(d_event['reserveTotal']), '.18f'),
                format(float(d_event['commission']), '.18f'),
                format(float(d_event['reservePrice']), '.18f')]


class MoCExchangeRiskProWithDiscountMint(BaseEvent):
    name = "RiskProWithDiscountMint"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt  # dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None
        self.riskProTecPrice = event['args']['riskProTecPrice']
        self.riskProDiscountPrice = event['args']['riskProDiscountPrice']
        self.amount = event['args']['amount']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'riskProTecPrice', 'riskProDiscountPrice', 'amount']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['riskProTecPrice'] = Web3.fromWei(self.riskProTecPrice, 'ether')
        d_event['riskProDiscountPrice'] = Web3.fromWei(self.riskProDiscountPrice, 'ether')
        d_event['amount'] = Web3.fromWei(self.amount, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                format(float(d_event['riskProTecPrice']), '.18f'),
                format(float(d_event['riskProDiscountPrice']), '.18f'),
                format(float(d_event['amount']), '.18f')]


class MoCExchangeRiskProRedeem(BaseEvent):
    name = "RiskProRedeem"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt  #dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None
        self.account = event['args']['account']
        self.amount = event['args']['amount']
        self.reserveTotal = event['args']['reserveTotal']
        self.commission = event['args']['commission']
        self.reservePrice = event['args']['reservePrice']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'Account', 'amount', 'reserveTotal', 'commission', 'reservePrice']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['account'] = self.account
        d_event['amount'] = Web3.fromWei(self.amount, 'ether')
        d_event['reserveTotal'] = Web3.fromWei(self.reserveTotal, 'ether')
        d_event['commission'] = Web3.fromWei(self.commission, 'ether')
        d_event['reservePrice'] = Web3.fromWei(self.reservePrice, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['account'],
                format(float(d_event['amount']), '.18f'),
                format(float(d_event['reserveTotal']), '.18f'),
                format(float(d_event['commission']), '.18f'),
                format(float(d_event['reservePrice']), '.18f')]


class MoCExchangeStableTokenMint(BaseEvent):
    name = "StableTokenMint"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt  #dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None
        self.account = event['args']['account']
        self.amount = event['args']['amount']
        self.reserveTotal = event['args']['reserveTotal']
        self.commission = event['args']['commission']
        self.reservePrice = event['args']['reservePrice']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'Account', 'amount', 'reserveTotal', 'commission', 'reservePrice']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['account'] = self.account
        d_event['amount'] = Web3.fromWei(self.amount, 'ether')
        d_event['reserveTotal'] = Web3.fromWei(self.reserveTotal, 'ether')
        d_event['commission'] = Web3.fromWei(self.commission, 'ether')
        d_event['reservePrice'] = Web3.fromWei(self.reservePrice, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['account'],
                format(float(d_event['amount']), '.18f'),
                format(float(d_event['reserveTotal']), '.18f'),
                format(float(d_event['commission']), '.18f'),
                format(float(d_event['reservePrice']), '.18f')]


class MoCExchangeStableTokenRedeem(BaseEvent):
    name = "StableTokenRedeem"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt #  dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None
        self.account = event['args']['account']
        self.amount = event['args']['amount']
        self.reserveTotal = event['args']['reserveTotal']
        self.commission = event['args']['commission']
        self.reservePrice = event['args']['reservePrice']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'Account', 'amount', 'reserveTotal', 'commission', 'reservePrice']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['account'] = self.account
        d_event['amount'] = Web3.fromWei(self.amount, 'ether')
        d_event['reserveTotal'] = Web3.fromWei(self.reserveTotal, 'ether')
        d_event['commission'] = Web3.fromWei(self.commission, 'ether')
        d_event['reservePrice'] = Web3.fromWei(self.reservePrice, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['account'],
                format(float(d_event['amount']), '.18f'),
                format(float(d_event['reserveTotal']), '.18f'),
                format(float(d_event['commission']), '.18f'),
                format(float(d_event['reservePrice']), '.18f')]


class MoCExchangeFreeStableTokenRedeem(BaseEvent):
    name = "FreeStableTokenRedeem"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt  # dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None
        self.account = event['args']['account']
        self.amount = event['args']['amount']
        self.reserveTotal = event['args']['reserveTotal']
        self.commission = event['args']['commission']
        self.interests = event['args']['interests']
        self.reservePrice = event['args']['reservePrice']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'Account', 'Amount', 'ReserveTotal', 'Commission', 'Interests', 'ReservePrice']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['account'] = self.account
        d_event['amount'] = Web3.fromWei(self.amount, 'ether')
        d_event['reserveTotal'] = Web3.fromWei(self.reserveTotal, 'ether')
        d_event['commission'] = Web3.fromWei(self.commission, 'ether')
        d_event['interests'] = Web3.fromWei(self.interests, 'ether')
        d_event['reservePrice'] = Web3.fromWei(self.reservePrice, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['account'],
                format(float(d_event['amount']), '.18f'),
                format(float(d_event['reserveTotal']), '.18f'),
                format(float(d_event['commission']), '.18f'),
                format(float(d_event['interests']), '.18f'),
                format(float(d_event['reservePrice']), '.18f')]


class MoCExchangeRiskProxMint(BaseEvent):
    name = "RiskProxMint"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt  #dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None
        self.bucket = 'X2'
        self.account = event['args']['account']
        self.amount = event['args']['amount']
        self.reserveTotal = event['args']['reserveTotal']
        self.interests = event['args']['interests']
        self.leverage = event['args']['leverage']
        self.commission = event['args']['commission']
        self.reservePrice = event['args']['reservePrice']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'Bucket', 'Account', 'Amount', 'Reserve Total', 'Interests',  'Leverage',  'Commission',  'Reserve Price']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['bucket'] = self.bucket
        d_event['account'] = self.account
        d_event['amount'] = Web3.fromWei(self.amount, 'ether')
        d_event['reserveTotal'] = Web3.fromWei(self.reserveTotal, 'ether')
        d_event['interests'] = Web3.fromWei(self.interests, 'ether')
        d_event['leverage'] = Web3.fromWei(self.leverage, 'ether')
        d_event['commission'] = Web3.fromWei(self.commission, 'ether')
        d_event['reservePrice'] = Web3.fromWei(self.reservePrice, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['bucket'],
                d_event['account'],
                format(float(d_event['amount']), '.18f'),
                format(float(d_event['reserveTotal']), '.18f'),
                format(float(d_event['interests']), '.18f'),
                format(float(d_event['leverage']), '.18f'),
                format(float(d_event['commission']), '.18f'),
                format(float(d_event['reservePrice']), '.18f')]


class MoCExchangeRiskProxRedeem(BaseEvent):
    name = "RiskProxRedeem"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt  #dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None
        self.bucket = 'X2'
        self.account = event['args']['account']
        self.commission = event['args']['commission']
        self.amount = event['args']['amount']
        self.reserveTotal = event['args']['reserveTotal']
        self.interests = event['args']['interests']
        self.leverage = event['args']['leverage']
        self.reservePrice = event['args']['reservePrice']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'Bucket', 'Account', 'Amount', 'Reserve Total', 'Interests',  'Leverage',  'Commission',  'Reserve Price']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['bucket'] = self.bucket
        d_event['account'] = self.account
        d_event['amount'] = Web3.fromWei(self.amount, 'ether')
        d_event['reserveTotal'] = Web3.fromWei(self.reserveTotal, 'ether')
        d_event['interests'] = Web3.fromWei(self.interests, 'ether')
        d_event['leverage'] = Web3.fromWei(self.leverage, 'ether')
        d_event['commission'] = Web3.fromWei(self.commission, 'ether')
        d_event['reservePrice'] = Web3.fromWei(self.reservePrice, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['bucket'],
                d_event['account'],
                format(float(d_event['amount']), '.18f'),
                format(float(d_event['reserveTotal']), '.18f'),
                format(float(d_event['interests']), '.18f'),
                format(float(d_event['leverage']), '.18f'),
                format(float(d_event['commission']), '.18f'),
                format(float(d_event['reservePrice']), '.18f')]


# SETTLEMENT

class MoCSettlementRedeemRequestProcessed(BaseEvent):
    name = "RedeemRequestProcessed"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt  #dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None

        self.redeemer = event['args']['redeemer']
        self.commission = event['args']['commission']
        self.amount = event['args']['amount']

    @staticmethod
    def columns():
        columns = ['Block Nº',  'Timestamp', 'Account', 'Commission', 'Amount']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['redeemer'] = self.redeemer
        d_event['commission'] = Web3.fromWei(self.commission, 'ether')
        d_event['amount'] = Web3.fromWei(self.amount, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['redeemer'],
                format(float(d_event['commission']), '.18f'),
                format(float(d_event['amount']), '.18f')]


class MoCSettlementSettlementRedeemStableToken(BaseEvent):
    name = "SettlementRedeemStableToken"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt  #dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None

        self.queueSize = event['args']['queueSize']
        self.accumCommissions = event['args']['accumCommissions']
        self.reservePrice = event['args']['reservePrice']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'queueSize', 'accumCommissions', 'reservePrice']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['queueSize'] = self.queueSize
        d_event['accumCommissions'] = Web3.fromWei(self.accumCommissions, 'ether')
        d_event['reservePrice'] = Web3.fromWei(self.reservePrice, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['queueSize'],
                format(float(d_event['accumCommissions']), '.18f'),
                format(float(d_event['reservePrice']), '.18f')]


class MoCSettlementSettlementCompleted(BaseEvent):
    name = "SettlementCompleted"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt  #dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None
        self.commissionsPayed = event['args']['commissionsPayed']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'commissionsPayed']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['commissionsPayed'] = Web3.fromWei(self.commissionsPayed, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                format(float(d_event['commissionsPayed']), '.18f')]


class MoCSettlementSettlementDeleveraging(BaseEvent):
    name = "SettlementDeleveraging"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt  #dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None

        self.leverage = event['args']['leverage']
        self.riskProxPrice = event['args']['riskProxPrice']
        self.reservePrice = event['args']['reservePrice']
        self.startBlockNumber = event['args']['startBlockNumber']

    @staticmethod
    def columns():
        columns = ['Block Nº',  'Timestamp', 'leverage', 'riskProxPrice', 'reservePrice', 'startBlockNumber']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['leverage'] = Web3.fromWei(self.leverage, 'ether')
        d_event['riskProxPrice'] = Web3.fromWei(self.riskProxPrice, 'ether')
        d_event['reservePrice'] = Web3.fromWei(self.reservePrice, 'ether')
        d_event['startBlockNumber'] = self.startBlockNumber

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                format(float(d_event['leverage']), '.18f'),
                format(float(d_event['riskProxPrice']), '.18f'),
                format(float(d_event['reservePrice']), '.18f'),
                d_event['startBlockNumber']]


class MoCSettlementSettlementStarted(BaseEvent):
    name = "SettlementStarted"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt  #dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None

        self.stableTokenRedeemCount = event['args']['stableTokenRedeemCount']
        self.deleveragingCount = event['args']['deleveragingCount']
        self.riskProxPrice = event['args']['riskProxPrice']
        self.reservePrice = event['args']['reservePrice']

    @staticmethod
    def columns():
        columns = ['Block Nº',  'Timestamp', 'stableTokenRedeemCount', 'deleveragingCount', 'riskProxPrice', 'reservePrice']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['stableTokenRedeemCount'] = self.stableTokenRedeemCount
        d_event['deleveragingCount'] = self.deleveragingCount
        d_event['riskProxPrice'] = Web3.fromWei(self.riskProxPrice, 'ether')
        d_event['reservePrice'] = Web3.fromWei(self.reservePrice, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['stableTokenRedeemCount'],
                d_event['deleveragingCount'],
                format(float(d_event['riskProxPrice']), '.18f'),
                format(float(d_event['reservePrice']), '.18f')]


class MoCSettlementRedeemRequestAlter(BaseEvent):
    name = "RedeemRequestAlter"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt  #dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None

        self.redeemer = event['args']['redeemer']
        self.isAddition = event['args']['isAddition']
        self.delta = event['args']['delta']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp',  'address', 'isAddition', 'delta']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['redeemer'] = self.redeemer
        d_event['isAddition'] = self.isAddition
        d_event['delta'] = Web3.fromWei(self.delta, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['redeemer'],
                d_event['isAddition'],
                format(float(d_event['delta']), '.18f')]


class MoCInrateDailyPay(BaseEvent):
    name = "InrateDailyPay"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            self.timestamp = ts - datetime.timedelta(hours=self.hours_delta)
            #self.timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None

        self.amount = event['args']['amount']
        self.daysToSettlement = event['args']['daysToSettlement']
        self.nReserveBucketC0 = event['args']['nReserveBucketC0']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp',  'Amount', 'daysToSettlement', 'nReserveBucketC0']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['amount'] = Web3.fromWei(self.amount, 'ether')
        d_event['daysToSettlement'] = self.daysToSettlement
        d_event['nReserveBucketC0'] = Web3.fromWei(self.nReserveBucketC0, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                format(float(d_event['amount']), '.18f'),
                d_event['daysToSettlement'],
                format(float(d_event['nReserveBucketC0']), '.18f')]


class MoCInrateRiskProHoldersInterestPay(BaseEvent):
    name = "RiskProHoldersInterestPay"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            self.timestamp = ts - datetime.timedelta(hours=self.hours_delta)
            # self.timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None

        self.amount = event['args']['amount']
        self.nReserveBucketC0BeforePay = event['args']['nReserveBucketC0BeforePay']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp',  'Amount', 'nReserveBucketC0BeforePay']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['amount'] = Web3.fromWei(self.amount, 'ether')
        d_event['nReserveBucketC0BeforePay'] = Web3.fromWei(self.nReserveBucketC0BeforePay, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                format(float(d_event['amount']), '.18f'),
                format(float(d_event['nReserveBucketC0BeforePay']), '.18f')]


class ERC20Transfer(BaseEvent):
    name = "Transfer"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt  #dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None

        self.value = event['args']['value']
        self.e_from = event['args']['from']
        self.e_to = event['args']['to']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp',  'Value', 'From', 'To']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['value'] = Web3.fromWei(self.value, 'ether')
        d_event['e_from'] = Web3.fromWei(self.e_from, 'ether')
        d_event['e_to'] = Web3.fromWei(self.e_to, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                format(float(d_event['value']), '.18f'),
                d_event['e_from'],
                d_event['e_to']]


class ERC20Approval(BaseEvent):
    name = "Approval"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            self.timestamp = ts - datetime.timedelta(hours=self.hours_delta)
        except BlockNotFound:
            self.timestamp = None

        self.owner = event['args']['owner']
        self.spender = event['args']['spender']
        self.value = event['args']['value']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp',  'owner', 'spender', 'value']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['owner'] = self.owner
        d_event['spender'] = self.spender
        d_event['value'] = Web3.fromWei(self.value, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['owner'],
                d_event['spender'],
                format(float(d_event['value']), '.18f')]


class MoCBucketLiquidation(BaseEvent):
    name = "BucketLiquidation"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt #dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None

        self.bucket = event['args']['bucket']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp',  'bucket']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['bucket'] = self.bucket

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['bucket']
                ]


class MoCStateStateTransition(BaseEvent):
    name = "StateTransition"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt  #dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None

        self.newState = event['args']['newState']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'newState']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['newState'] = self.newState

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['newState']
                ]

# DEX Events

# MoCDecentralizedExchange.sol


class DEXNewOrderAddedToPendingQueue(BaseEvent):

    name = "NewOrderAddedToPendingQueue"

    def __init__(self, connection_manager, event):

        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            dt = ts - datetime.timedelta(hours=self.hours_delta)
            self.timestamp = dt #dt.strftime("%Y-%m-%d %H:%M:%S")
        except BlockNotFound:
            self.timestamp = None
        self.id = event['args']['id']
        self.notIndexedArgumentSoTheThingDoesntBreak = event['args']['notIndexedArgumentSoTheThingDoesntBreak']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'id', 'notIndexedArgumentSoTheThingDoesntBreak']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['id'] = self.id
        d_event['notIndexedArgumentSoTheThingDoesntBreak'] = self.notIndexedArgumentSoTheThingDoesntBreak

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['id'],
                d_event['notIndexedArgumentSoTheThingDoesntBreak']]


class DEXBuyerMatch(BaseEvent):
    name = "BuyerMatch"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            self.timestamp = ts - datetime.timedelta(hours=self.hours_delta)
        except BlockNotFound:
            self.timestamp = None

        self.orderId = event['args']['orderId']
        self.amountSent = event['args']['amountSent']
        self.commission = event['args']['commission']
        self.change = event['args']['change']
        self.received = event['args']['received']
        self.remainingAmount = event['args']['remainingAmount']
        self.matchPrice = event['args']['matchPrice']
        self.tickNumber = event['args']['tickNumber']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp',  'orderId', 'amountSent', 'commission', 'change', 'received',
                   'remainingAmount', 'matchPrice', 'tickNumber']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['orderId'] = self.orderId
        d_event['amountSent'] = Web3.fromWei(self.amountSent, 'ether')
        d_event['commission'] = Web3.fromWei(self.commission, 'ether')
        d_event['change'] = Web3.fromWei(self.change, 'ether')
        d_event['received'] = Web3.fromWei(self.received, 'ether')
        d_event['remainingAmount'] = Web3.fromWei(self.remainingAmount, 'ether')
        d_event['matchPrice'] = Web3.fromWei(self.matchPrice, 'ether')
        d_event['tickNumber'] = self.tickNumber

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['orderId'],
                format(float(d_event['amountSent']), '.18f'),
                format(float(d_event['commission']), '.18f'),
                format(float(d_event['change']), '.18f'),
                format(float(d_event['received']), '.18f'),
                format(float(d_event['remainingAmount']), '.18f'),
                format(float(d_event['matchPrice']), '.18f'),
                d_event['tickNumber']
                ]


class DEXSellerMatch(BaseEvent):
    name = "SellerMatch"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            self.timestamp = ts - datetime.timedelta(hours=self.hours_delta)
        except BlockNotFound:
            self.timestamp = None

        self.orderId = event['args']['orderId']
        self.amountSent = event['args']['amountSent']
        self.commission = event['args']['commission']
        self.received = event['args']['received']
        self.surplus = event['args']['surplus']
        self.remainingAmount = event['args']['remainingAmount']
        self.matchPrice = event['args']['matchPrice']
        self.tickNumber = event['args']['tickNumber']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp',  'orderId', 'amountSent', 'commission', 'received', 'surplus',
                   'remainingAmount', 'matchPrice', 'tickNumber']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['orderId'] = self.orderId
        d_event['amountSent'] = Web3.fromWei(self.amountSent, 'ether')
        d_event['commission'] = Web3.fromWei(self.commission, 'ether')
        d_event['received'] = Web3.fromWei(self.received, 'ether')
        d_event['surplus'] = Web3.fromWei(self.surplus, 'ether')
        d_event['remainingAmount'] = Web3.fromWei(self.remainingAmount, 'ether')
        d_event['matchPrice'] = Web3.fromWei(self.matchPrice, 'ether')
        d_event['tickNumber'] = self.tickNumber

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['orderId'],
                format(float(d_event['amountSent']), '.18f'),
                format(float(d_event['commission']), '.18f'),
                format(float(d_event['received']), '.18f'),
                format(float(d_event['surplus']), '.18f'),
                format(float(d_event['remainingAmount']), '.18f'),
                format(float(d_event['matchPrice']), '.18f'),
                d_event['tickNumber']
                ]


class DEXExpiredOrderProcessed(BaseEvent):
    name = "ExpiredOrderProcessed"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            self.timestamp = ts - datetime.timedelta(hours=self.hours_delta)
        except BlockNotFound:
            self.timestamp = None

        self.orderId = event['args']['orderId']
        self.owner = event['args']['owner']
        self.returnedAmount = event['args']['returnedAmount']
        self.commission = event['args']['commission']
        self.returnedCommission = event['args']['returnedCommission']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp',  'orderId', 'owner', 'returnedAmount', 'commission', 'returnedCommission']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['orderId'] = self.orderId
        d_event['owner'] = self.owner
        d_event['returnedAmount'] = Web3.fromWei(self.returnedAmount, 'ether')
        d_event['commission'] = Web3.fromWei(self.commission, 'ether')
        d_event['returnedCommission'] = Web3.fromWei(self.returnedCommission, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['orderId'],
                d_event['owner'],
                format(float(d_event['returnedAmount']), '.18f'),
                format(float(d_event['commission']), '.18f'),
                format(float(d_event['returnedCommission']), '.18f')
                ]


class DEXTickStart(BaseEvent):
    name = "TickStart"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            self.timestamp = ts - datetime.timedelta(hours=self.hours_delta)
        except BlockNotFound:
            self.timestamp = None

        self.baseTokenAddress = event['args']['baseTokenAddress']
        self.secondaryTokenAddress = event['args']['secondaryTokenAddress']
        self.number = event['args']['number']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'baseTokenAddress', 'secondaryTokenAddress', 'number']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['baseTokenAddress'] = self.baseTokenAddress
        d_event['secondaryTokenAddress'] = self.secondaryTokenAddress
        d_event['number'] = self.number

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['baseTokenAddress'],
                d_event['secondaryTokenAddress'],
                d_event['number']
                ]


class DEXTickEnd(BaseEvent):
    name = "TickEnd"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            self.timestamp = ts - datetime.timedelta(hours=self.hours_delta)
        except BlockNotFound:
            self.timestamp = None

        self.baseTokenAddress = event['args']['baseTokenAddress']
        self.secondaryTokenAddress = event['args']['secondaryTokenAddress']
        self.number = event['args']['number']
        self.nextTickBlock = event['args']['nextTickBlock']
        self.closingPrice = event['args']['closingPrice']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'baseTokenAddress', 'secondaryTokenAddress', 'number',
                   'nextTickBlock', 'closingPrice']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['baseTokenAddress'] = self.baseTokenAddress
        d_event['secondaryTokenAddress'] = self.secondaryTokenAddress
        d_event['number'] = self.number
        d_event['nextTickBlock'] = self.nextTickBlock
        d_event['closingPrice'] = Web3.fromWei(self.closingPrice, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['baseTokenAddress'],
                d_event['secondaryTokenAddress'],
                d_event['number'],
                d_event['nextTickBlock'],
                format(float(d_event['closingPrice']), '.18f')
                ]


class DEXNewOrderInserted(BaseEvent):
    name = "NewOrderInserted"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            self.timestamp = ts - datetime.timedelta(hours=self.hours_delta)
        except BlockNotFound:
            self.timestamp = None

        self.id = event['args']['id']
        self.sender = event['args']['sender']
        self.baseTokenAddress = event['args']['baseTokenAddress']
        self.secondaryTokenAddress = event['args']['secondaryTokenAddress']
        self.exchangeableAmount = event['args']['exchangeableAmount']
        self.reservedCommission = event['args']['reservedCommission']
        self.price = event['args']['price']
        self.multiplyFactor = event['args']['multiplyFactor']
        self.expiresInTick = event['args']['expiresInTick']
        self.isBuy = event['args']['isBuy']
        self.orderType = event['args']['orderType']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'id', 'sender', 'baseTokenAddress',
                   'secondaryTokenAddress', 'exchangeableAmount', 'reservedCommission',
                   'price', 'multiplyFactor', 'expiresInTick', 'isBuy', 'orderType']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['id'] = self.id
        d_event['sender'] = self.sender
        d_event['baseTokenAddress'] = self.baseTokenAddress
        d_event['secondaryTokenAddress'] = self.secondaryTokenAddress
        d_event['exchangeableAmount'] = Web3.fromWei(self.exchangeableAmount, 'ether')
        d_event['reservedCommission'] = Web3.fromWei(self.reservedCommission, 'ether')
        d_event['price'] = Web3.fromWei(self.price, 'ether')
        d_event['multiplyFactor'] = self.multiplyFactor
        d_event['expiresInTick'] = self.expiresInTick
        d_event['isBuy'] = self.isBuy
        d_event['orderType'] = self.orderType

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['id'],
                d_event['sender'],
                d_event['baseTokenAddress'],
                d_event['secondaryTokenAddress'],
                format(float(d_event['exchangeableAmount']), '.18f'),
                format(float(d_event['reservedCommission']), '.18f'),
                format(float(d_event['price']), '.18f'),
                d_event['multiplyFactor'],
                d_event['expiresInTick'],
                d_event['isBuy'],
                d_event['orderType']
                ]


class DEXOrderCancelled(BaseEvent):
    name = "OrderCancelled"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            self.timestamp = ts - datetime.timedelta(hours=self.hours_delta)
        except BlockNotFound:
            self.timestamp = None

        self.id = event['args']['id']
        self.sender = event['args']['sender']
        self.returnedAmount = event['args']['returnedAmount']
        self.commission = event['args']['commission']
        self.returnedCommission = event['args']['returnedCommission']
        self.isBuy = event['args']['isBuy']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'id', 'sender', 'returnedAmount',
                   'commission', 'returnedCommission', 'isBuy']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['id'] = self.id
        d_event['sender'] = self.sender
        d_event['returnedAmount'] = Web3.fromWei(self.returnedAmount, 'ether')
        d_event['commission'] = Web3.fromWei(self.commission, 'ether')
        d_event['returnedCommission'] = Web3.fromWei(self.returnedCommission, 'ether')
        d_event['isBuy'] = self.isBuy

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['id'],
                d_event['sender'],
                format(float(d_event['returnedAmount']), '.18f'),
                format(float(d_event['commission']), '.18f'),
                format(float(d_event['returnedCommission']), '.18f'),
                d_event['isBuy']
                ]


class DEXTransferFailed(BaseEvent):
    name = "TransferFailed"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            self.timestamp = ts - datetime.timedelta(hours=self.hours_delta)
        except BlockNotFound:
            self.timestamp = None

        self._tokenAddress = event['args']['_tokenAddress']
        self._to = event['args']['_to']
        self._amount = event['args']['_amount']
        self._isRevert = event['args']['_isRevert']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', '_tokenAddress', '_to', '_amount',
                   '_isRevert']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['_tokenAddress'] = self._tokenAddress
        d_event['_to'] = self._to
        d_event['_amount'] = Web3.fromWei(self._amount, 'ether')
        d_event['_isRevert'] = self._isRevert

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['_tokenAddress'],
                d_event['_to'],
                format(float(d_event['_amount']), '.18f'),
                d_event['_isRevert']
                ]


class DEXCommissionWithdrawn(BaseEvent):
    name = "CommissionWithdrawn"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            self.timestamp = ts - datetime.timedelta(hours=self.hours_delta)
        except BlockNotFound:
            self.timestamp = None

        self.token = event['args']['token']
        self.commissionBeneficiary = event['args']['commissionBeneficiary']
        self.withdrawnAmount = event['args']['withdrawnAmount']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'token', 'commissionBeneficiary', 'withdrawnAmount']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['token'] = self.token
        d_event['commissionBeneficiary'] = self.commissionBeneficiary
        d_event['withdrawnAmount'] = Web3.fromWei(self.withdrawnAmount, 'ether')

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['token'],
                d_event['commissionBeneficiary'],
                format(float(d_event['withdrawnAmount']), '.18f')
                ]


class DEXTokenPairDisabled(BaseEvent):
    name = "TokenPairDisabled"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            self.timestamp = ts - datetime.timedelta(hours=self.hours_delta)
        except BlockNotFound:
            self.timestamp = None

        self.baseToken = event['args']['baseToken']
        self.secondaryToken = event['args']['secondaryToken']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'baseToken', 'secondaryToken']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['baseToken'] = self.baseToken
        d_event['secondaryToken'] = self.secondaryToken

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['baseToken'],
                d_event['secondaryToken']
                ]


class DEXTokenPairEnabled(BaseEvent):
    name = "TokenPairEnabled"

    def __init__(self, connection_manager, event):
        self.blockNumber = event['blockNumber']
        try:
            ts = connection_manager.block_timestamp(self.blockNumber)
            self.timestamp = ts - datetime.timedelta(hours=self.hours_delta)
        except BlockNotFound:
            self.timestamp = None

        self.baseToken = event['args']['baseToken']
        self.secondaryToken = event['args']['secondaryToken']

    @staticmethod
    def columns():
        columns = ['Block Nº', 'Timestamp', 'baseToken', 'secondaryToken']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        if self.timestamp:
            d_event['timestamp'] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            d_event['timestamp'] = ''
        d_event['baseToken'] = self.baseToken
        d_event['secondaryToken'] = self.secondaryToken

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['baseToken'],
                d_event['secondaryToken']
                ]
