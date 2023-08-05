"""
                    GNU AFFERO GENERAL PUBLIC LICENSE
                       Version 3, 19 November 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

 THIS IS A PART OF MONEY ON CHAIN PACKAGE
 by Martin Mulone (martin.mulone@moneyonchain.com)

"""

import os
import logging
from web3 import Web3
from web3.types import BlockIdentifier
from decimal import Decimal

from moneyonchain.contract import Contract


class ERC20Token(Contract):

    log = logging.getLogger()
    precision = 10 ** 18

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

    def name(self):
        return self.sc.functions.name().call()

    def symbol(self):
        return self.sc.functions.symbol().call()

    def total_supply(self, formatted=True,
                     block_identifier: BlockIdentifier = 'latest'):

        total = self.sc.functions.totalSupply().call(block_identifier=block_identifier)
        if formatted:
            total = Web3.fromWei(total, 'ether')
        return total

    def balance_of(self, account_address, formatted=True,
                   block_identifier: BlockIdentifier = 'latest'):

        account_address = Web3.toChecksumAddress(account_address)

        balance = self.sc.functions.balanceOf(account_address).call(
            block_identifier=block_identifier)
        if formatted:
            balance = Web3.fromWei(balance, 'ether')
        return balance

    def allowance(self,
                  account_address,
                  contract_address,
                  formatted=True,
                  block_identifier: BlockIdentifier = 'latest'):

        account_address = Web3.toChecksumAddress(account_address)
        contract_address = Web3.toChecksumAddress(contract_address)

        balance = self.sc.functions.allowance(account_address, contract_address).call(
            block_identifier=block_identifier)
        if formatted:
            balance = Web3.fromWei(balance, 'ether')
        return balance

    def approve(self,
                contract_address,
                amount,
                gas_limit=3500000,
                wait_timeout=240,
                default_account=None,
                wait_receipt=True,
                poll_latency=0.5):
        """Set allowance """

        tx_receipt = None
        sc_amount = int(Decimal(amount) * self.precision)
        sc_address = Web3.toChecksumAddress(contract_address)

        tx_hash = self.connection_manager.fnx_transaction(self.sc,
                                                          'approve',
                                                          sc_address,
                                                          sc_amount,
                                                          default_account=default_account,
                                                          gas_limit=gas_limit)
        if wait_receipt:
            # wait to transaction be mined
            tx_receipt = self.connection_manager.wait_for_transaction_receipt(
                tx_hash,
                timeout=wait_timeout,
                poll_latency=poll_latency)

            self.log.info("Successfully aprove in Block  [{0}] Hash: [{1}] Gas used: [{2}] From: [{3}]".format(
                            tx_receipt['blockNumber'],
                            Web3.toHex(tx_receipt['transactionHash']),
                            tx_receipt['gasUsed'],
                            tx_receipt['from']))

        return tx_hash, tx_receipt


class DoCToken(ERC20Token):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi/DocToken.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi/DocToken.bin'))

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        if not contract_address:
            # load from connection manager
            network = connection_manager.network
            contract_address = connection_manager.options['networks'][network]['addresses']['DoCToken']

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

        # finally load the contract
        self.load_contract()


class BProToken(ERC20Token):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi/BProToken.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi/BProToken.bin'))

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        if not contract_address:
            # load from connection manager
            network = connection_manager.network
            contract_address = connection_manager.options['networks'][network]['addresses']['BProToken']

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

        # finally load the contract
        self.load_contract()


class RIFDoC(ERC20Token):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_rdoc/StableToken.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_rdoc/StableToken.bin'))

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        if not contract_address:
            # load from connection manager
            network = connection_manager.network
            contract_address = connection_manager.options['networks'][network]['addresses']['DoCToken']

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

        # finally load the contract
        self.load_contract()


class RIFPro(ERC20Token):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_rdoc/RiskProToken.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_rdoc/RiskProToken.bin'))

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        if not contract_address:
            # load from connection manager
            network = connection_manager.network
            contract_address = connection_manager.options['networks'][network]['addresses']['BProToken']

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

        # finally load the contract
        self.load_contract()


class RIF(ERC20Token):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_rdoc/ReserveToken.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_rdoc/ReserveToken.bin'))

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        if not contract_address:
            # load from connection manager
            network = connection_manager.network
            contract_address = connection_manager.options['networks'][network]['addresses']['ReserveToken']

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

        # finally load the contract
        self.load_contract()


class ReserveToken(ERC20Token):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_rdoc/ReserveToken.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_rdoc/ReserveToken.bin'))

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        if not contract_address:
            # load from connection manager
            network = connection_manager.network
            contract_address = connection_manager.options['networks'][network]['addresses']['ReserveToken']

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

        # finally load the contract
        self.load_contract()


class RiskProToken(ERC20Token):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_rdoc/RiskProToken.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_rdoc/RiskProToken.bin'))

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        if not contract_address:
            # load from connection manager
            network = connection_manager.network
            contract_address = connection_manager.options['networks'][network]['addresses']['BProToken']

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

        # finally load the contract
        self.load_contract()


class StableToken(ERC20Token):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_rdoc/StableToken.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_rdoc/StableToken.bin'))

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        if not contract_address:
            # load from connection manager
            network = connection_manager.network
            contract_address = connection_manager.options['networks'][network]['addresses']['DoCToken']

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

        # finally load the contract
        self.load_contract()


class WRBTC(ERC20Token):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/WRBTC.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/WRBTC.bin'))

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        if not contract_address:
            # load from connection manager
            network = connection_manager.network
            contract_address = connection_manager.options['networks'][network]['addresses']['WRBTCToken']

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

        # finally load the contract
        self.load_contract()

    def deposit(self,
                amount,
                gas_limit=3500000,
                wait_timeout=240,
                default_account=None,
                wait_receipt=True,
                poll_latency=0.5):
        """ Wrap """

        tx_receipt = None
        sc_amount = int(Decimal(amount) * self.precision)

        tx_hash = self.connection_manager.fnx_transaction(self.sc,
                                                          'deposit',
                                                          tx_params={'value': sc_amount},
                                                          default_account=default_account,
                                                          gas_limit=gas_limit)
        if wait_receipt:
            # wait to transaction be mined
            tx_receipt = self.connection_manager.wait_for_transaction_receipt(
                tx_hash,
                timeout=wait_timeout,
                poll_latency=poll_latency)

            self.log.info("Successfully deposit in Block  [{0}] Hash: [{1}] Gas used: [{2}] From: [{3}]".format(
                            tx_receipt['blockNumber'],
                            Web3.toHex(tx_receipt['transactionHash']),
                            tx_receipt['gasUsed'],
                            tx_receipt['from']))

        return tx_hash, tx_receipt

    def withdraw(self,
                 amount,
                 gas_limit=3500000,
                 wait_timeout=240,
                 default_account=None,
                 wait_receipt=True,
                 poll_latency=0.5):
        """ withdraw """

        tx_receipt = None
        sc_amount = int(Decimal(amount) * self.precision)

        tx_hash = self.connection_manager.fnx_transaction(self.sc,
                                                          'withdraw',
                                                          sc_amount,
                                                          default_account=default_account,
                                                          gas_limit=gas_limit)
        if wait_receipt:
            # wait to transaction be mined
            tx_receipt = self.connection_manager.wait_for_transaction_receipt(
                tx_hash,
                timeout=wait_timeout,
                poll_latency=poll_latency)

            self.log.info("Successfully withdraw in Block  [{0}] Hash: [{1}] Gas used: [{2}] From: [{3}]".format(
                            tx_receipt['blockNumber'],
                            Web3.toHex(tx_receipt['transactionHash']),
                            tx_receipt['gasUsed'],
                            tx_receipt['from']))

        return tx_hash, tx_receipt
