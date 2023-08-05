"""
                    GNU AFFERO GENERAL PUBLIC LICENSE
                       Version 3, 19 November 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

 THIS IS A PART OF MONEY ON CHAIN PACKAGE
 by Martin Mulone (martin.mulone@moneyonchain.com)

"""

from web3 import Web3

from moneyonchain.events import BaseEvent


class NewBitcoinTransfer(BaseEvent):

    name = "NewBitcoinTransfer"

    @staticmethod
    def columns():
        columns = ['transferId', 'btcAddress', 'nonce', 'amountSatoshi', 'feeSatoshi', 'rskAddress']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        d_event['timestamp'] = self.timestamp
        d_event['transferId'] = self.event['transferId']
        d_event['btcAddress'] = self.event['btcAddress']
        d_event['nonce'] = self.event['nonce']
        d_event['amountSatoshi'] = self.event['amountSatoshi']
        d_event['feeSatoshi'] = self.event['feeSatoshi']
        d_event['rskAddress'] = self.event['rskAddress']

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['transferId'],
                d_event['btcAddress'],
                d_event['nonce'],
                d_event['amountSatoshi'],
                d_event['feeSatoshi'],
                d_event['rskAddress']
                ]


class BitcoinTransferStatusUpdated(BaseEvent):
    name = "BitcoinTransferStatusUpdated"

    @staticmethod
    def columns():
        columns = ['transferIdº', 'newStatus']
        return columns

    def formatted(self):
        d_event = dict()
        d_event['blockNumber'] = self.blockNumber
        d_event['timestamp'] = self.timestamp
        d_event['transferId'] = self.event['transferId']
        d_event['newStatus'] = self.event['newStatus']

        return d_event

    def row(self):
        d_event = self.formatted()
        return [d_event['blockNumber'],
                d_event['timestamp'],
                d_event['transferId'],
                d_event['newStatus']
                ]
