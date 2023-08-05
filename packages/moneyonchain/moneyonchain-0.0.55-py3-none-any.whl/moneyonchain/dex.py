"""
        GNU AFFERO GENERAL PUBLIC LICENSE
           Version 3, 19 November 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

 THIS IS A PART OF MONEY ON CHAIN
 @2020
 by Martin Mulone (martin.mulone@moneyonchain.com)

"""

import os
import logging
from decimal import Decimal
from web3 import Web3
from web3.types import BlockIdentifier

from moneyonchain.contract import Contract
from moneyonchain.admin import ProxyAdmin

from moneyonchain.events import DEXNewOrderInserted, DEXCommissionWithdrawn, DEXOrderCancelled


class MoCDecentralizedExchange(Contract):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/MoCDecentralizedExchange.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/MoCDecentralizedExchange.bin'))

    mode = 'DEX'
    precision = 10 ** 18

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        if not contract_address:
            # load from connection manager
            network = connection_manager.network
            contract_address = connection_manager.options['networks'][network]['addresses']['dex']

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

        # finally load the contract
        self.load_contract()

    def implementation(self, block_identifier: BlockIdentifier = 'latest'):
        """Implementation of contract"""

        contract_admin = ProxyAdmin(self.connection_manager)
        contract_address = Web3.toChecksumAddress(self.contract_address)

        return contract_admin.implementation(contract_address, block_identifier=block_identifier)

    def paused(self,
               block_identifier: BlockIdentifier = 'latest'):
        """is Paused"""

        result = self.sc.functions.paused().call(
            block_identifier=block_identifier)

        return result

    def min_order_amount(self, formatted: bool = True,
                         block_identifier: BlockIdentifier = 'latest'):
        """Gets min order amount"""

        result = self.sc.functions.minOrderAmount().call(
            block_identifier=block_identifier)
        if formatted:
            result = Web3.fromWei(result, 'ether')

        return result

    def max_order_lifespan(self, block_identifier: BlockIdentifier = 'latest'):
        """Is the maximum lifespan in ticks for an order

        @:return Integer number of max order lifespan in ticks
        """

        result = self.sc.functions.maxOrderLifespan().call(
            block_identifier=block_identifier)

        return result

    def min_multiply_factor(self, formatted: bool = True,
                            block_identifier: BlockIdentifier = 'latest'):
        """ Minimum range avalaible price to be paid   """

        result = self.sc.functions.minMultiplyFactor().call(
            block_identifier=block_identifier)

        if formatted:
            result = Web3.fromWei(result, 'ether')

        return result

    def max_multiply_factor(self, formatted: bool = True,
                            block_identifier: BlockIdentifier = 'latest'):
        """ Maximum range avalaible price to be paid   """

        result = self.sc.functions.maxMultiplyFactor().call(
            block_identifier=block_identifier)

        if formatted:
            result = Web3.fromWei(result, 'ether')

        return result

    def token_pairs(self, block_identifier: BlockIdentifier = 'latest'):
        """ Get the token pairs"""

        result = self.sc.functions.getTokenPairs().call(
            block_identifier=block_identifier)

        return result

    def token_pairs_status(self, base_address, secondary_address,
                           block_identifier: BlockIdentifier = 'latest'):
        """ Get the token pairs"""

        base_address = Web3.toChecksumAddress(base_address)
        secondary_address = Web3.toChecksumAddress(secondary_address)

        result = self.sc.functions.getTokenPairStatus(base_address,
                                                      secondary_address).call(
            block_identifier=block_identifier)

        if result:
            d_status = dict()
            d_status['emergentPrice'] = result[0]
            d_status['lastBuyMatchId'] = result[1]
            d_status['lastBuyMatchAmount'] = result[2]
            d_status['lastSellMatchId'] = result[3]
            d_status['tickNumber'] = result[4]
            d_status['nextTickBlock'] = result[5]
            d_status['lastTickBlock'] = result[6]
            d_status['lastClosingPrice'] = result[7]
            d_status['disabled'] = result[8]
            d_status['EMAPrice'] = result[9]
            d_status['smoothingFactor'] = result[10]
            d_status['marketPrice'] = result[11]

            return d_status

        return result

    def convert_token_to_common_base(self,
                                     token_address,
                                     amount,
                                     base_address,
                                     formatted: bool = True,
                                     block_identifier: BlockIdentifier = 'latest'):
        """
        @dev simple converter from the given token to a common base, in this case, Dollar on Chain
        @param token_address the token address of token to convert into the common base token
        @param amount the amount to convert
        @param base_address the address of the base of the pair in witch the token its going to operate.
        if the the token it is allready the base of the pair, this parameter it is unimportant
        @return convertedAmount the amount converted into the common base token
        """

        token_address = Web3.toChecksumAddress(token_address)
        base_address = Web3.toChecksumAddress(base_address)

        result = self.sc.functions.convertTokenToCommonBase(token_address,
                                                            amount,
                                                            base_address).call(
            block_identifier=block_identifier)

        if formatted:
            result = Web3.fromWei(result, 'ether')

        return result

    def get_price_provider(self, base_address, secondary_address,
                           block_identifier: BlockIdentifier = 'latest'):
        """Returns the price provider of a given pair """

        base_address = Web3.toChecksumAddress(base_address)
        secondary_address = Web3.toChecksumAddress(secondary_address)

        result = self.sc.functions.getPriceProvider(base_address,
                                                    secondary_address).call(
            block_identifier=block_identifier)

        return result

    def next_tick(self, pair, block_identifier: BlockIdentifier = 'latest'):
        """ Next tick """

        result = self.sc.functions.getNextTick(pair[0], pair[1]).call(
            block_identifier=block_identifier)

        return result

    def are_orders_to_expire(self,
                             pair,
                             is_buy_order,
                             block_identifier: BlockIdentifier = 'latest'):
        """ Are orders to expire """

        result = self.sc.functions.areOrdersToExpire(pair[0],
                                                     pair[1],
                                                     is_buy_order).call(
            block_identifier=block_identifier)

        return result

    def emergent_price(self,
                       pair,
                       block_identifier: BlockIdentifier = 'latest'):
        """ Calculates closing price as if the tick closes at this moment.
            emergentPrice: AVG price of the last matched Orders

            return (emergentPrice, lastBuyMatch.id, lastBuyMatch.exchangeableAmount, lastSellMatch.id);
            """

        result = self.sc.functions.getEmergentPrice(pair[0], pair[1]).call(
            block_identifier=block_identifier)

        return result

    def market_price(self,
                     pair,
                     formatted: bool = True,
                     block_identifier: BlockIdentifier = 'latest'):
        """ Get the current market price """

        result = self.sc.functions.getMarketPrice(pair[0], pair[1]).call(
            block_identifier=block_identifier)

        if formatted:
            result = Web3.fromWei(result, 'ether')

        return result

    def run_tick_for_pair(self, pair,
                          gas_limit=3500000,
                          wait_timeout=240,
                          matching_steps=70,
                          default_account=None,
                          wait_receipt=True):
        """Run tick for pair """

        tx_hash = None
        tx_receipt = None

        block_number = self.connection_manager.block_number
        self.log.info('About to run tick for pair {0}'.format(pair))
        next_tick_info = self.next_tick(pair)
        block_of_next_tick = next_tick_info[1]

        self.log.info('BlockOfNextTick {0}, currentBlockNumber {1}'.format(
            block_of_next_tick, block_number))
        self.log.info('Is tick runnable? {0}'.format(
            block_of_next_tick <= block_number))
        if block_of_next_tick <= block_number:

            tx_hash = self.connection_manager.fnx_transaction(self.sc,
                                                              'matchOrders',
                                                              pair[0],
                                                              pair[1],
                                                              matching_steps,
                                                              default_account=default_account,
                                                              gas_limit=gas_limit)

            self.log.info(
                'Transaction hash of tick run {0}'.format(tx_hash.hex()))

            if wait_receipt:
                # wait to transaction be mined
                tx_receipt = self.connection_manager.wait_for_transaction_receipt(tx_hash,
                                                                                  timeout=wait_timeout,
                                                                                  poll_latency=0.5)

                self.log.info(
                    "Tick runned correctly in Block  [{0}] Hash: [{1}] Gas used: [{2}] From: [{3}]".format(
                        tx_receipt['blockNumber'],
                        Web3.toHex(tx_receipt['transactionHash']),
                        tx_receipt['gasUsed'],
                        tx_receipt['from']))

        else:
            self.log.info('Block of next tick has not been reached\n\n')

        return tx_hash, tx_receipt

    def run_orders_expiration_for_pair(self, pair, is_buy_order, order_type,
                                       hint=0,
                                       order_id=0,
                                       gas_limit=3500000,
                                       wait_timeout=240,
                                       matching_steps=70,
                                       default_account=None,
                                       wait_receipt=True):
        """Run order expiration """

        tx_hash = None
        tx_receipt = None

        block_number = self.connection_manager.block_number

        self.log.info('About to expire {0} orders for pair {1} in blockNumber {2}'.format('buy' if is_buy_order else 'sell',
                                                                                          pair, block_number))

        tx_hash = self.connection_manager.fnx_transaction(self.sc,
                                                          'processExpired',
                                                          pair[0],
                                                          pair[1],
                                                          is_buy_order,
                                                          hint,
                                                          order_id,
                                                          matching_steps,
                                                          order_type,
                                                          default_account=default_account,
                                                          gas_limit=gas_limit)

        self.log.info(
            'Transaction hash of {0} orders expiration {1}'.format('buy' if is_buy_order else 'sell',
                                                                   tx_hash.hex()))

        if wait_receipt:
            # wait to transaction be mined
            tx_receipt = self.connection_manager.wait_for_transaction_receipt(tx_hash,
                                                                              timeout=wait_timeout,
                                                                              poll_latency=0.5)

            self.log.info(
                "Orders expiration job finished in block [{0}] Hash: [{1}] Gas used: [{2}] From: [{3}]".format(
                    tx_receipt['blockNumber'],
                    Web3.toHex(tx_receipt['transactionHash']),
                    tx_receipt['gasUsed'],
                    tx_receipt['from']))

        return tx_hash, tx_receipt

    def _insert_sell_limit_order(self,
                                 base_token,
                                 secondary_token,
                                 amount,
                                 price,
                                 lifespan,
                                 gas_limit=3500000,
                                 wait_timeout=240,
                                 default_account=None,
                                 wait_receipt=True,
                                 poll_latency=0.5):
        """ Inserts an order in the sell orderbook of a given pair without a hint
    the pair should not be disabled; the contract should not be paused. Takes the funds
    with a transferFrom """

        tx_hash = None
        tx_receipt = None

        tx_hash = self.connection_manager.fnx_transaction(self.sc,
                                                          'insertSellLimitOrder',
                                                          base_token,
                                                          secondary_token,
                                                          amount,
                                                          price,
                                                          lifespan,
                                                          default_account=default_account,
                                                          gas_limit=gas_limit)

        if wait_receipt:
            # wait to transaction be mined
            tx_receipt = self.connection_manager.wait_for_transaction_receipt(
                tx_hash,
                timeout=wait_timeout,
                poll_latency=poll_latency)

            self.log.info(
                "Successfully inserted sell limit order in Block  [{0}] Hash: [{1}] Gas used: [{2}] From: [{3}]".format(
                    tx_receipt['blockNumber'],
                    Web3.toHex(tx_receipt['transactionHash']),
                    tx_receipt['gasUsed'],
                    tx_receipt['from']))

        return tx_hash, tx_receipt

    def insert_sell_limit_order(self,
                                base_token,
                                secondary_token,
                                amount,
                                price,
                                lifespan,
                                gas_limit=3500000,
                                wait_timeout=240,
                                default_account=None,
                                wait_receipt=True,
                                poll_latency=0.5):
        """ Inserts an order in the sell orderbook of a given pair without a hint
    the pair should not be disabled; the contract should not be paused. Takes the funds
    with a transferFrom """

        base_token = Web3.toChecksumAddress(base_token)
        secondary_token = Web3.toChecksumAddress(secondary_token)
        amount_sc = int(Decimal(amount) * self.precision)
        price_sc = int(Decimal(price) * self.precision)
        lifespan_sc = int(lifespan)

        if self.paused():
            raise Exception("Contract is paused you cannot operate!")

        tx_hash, tx_receipt = self._insert_sell_limit_order(
            base_token,
            secondary_token,
            amount_sc,
            price_sc,
            lifespan_sc,
            gas_limit=gas_limit,
            wait_timeout=wait_timeout,
            default_account=default_account,
            wait_receipt=wait_receipt,
            poll_latency=poll_latency)

        tx_logs = None
        tx_logs_formatted = None

        if tx_receipt:
            # receipt to logs
            tx_logs = {"NewOrderInserted": self.events.NewOrderInserted().processReceipt(tx_receipt)}
            tx_logs_formatted = {"NewOrderInserted": DEXNewOrderInserted(
                self.connection_manager,
                tx_logs["NewOrderInserted"][0])}

        return tx_hash, tx_receipt, tx_logs, tx_logs_formatted

    def _insert_buy_limit_order(self,
                                base_token,
                                secondary_token,
                                amount,
                                price,
                                lifespan,
                                gas_limit=3500000,
                                wait_timeout=240,
                                default_account=None,
                                wait_receipt=True,
                                poll_latency=0.5):
        """ @notice Inserts an order in the buy orderbook of a given pair without a hint
    the pair should not be disabled; the contract should not be paused. Takes the funds
    with a transferFrom """

        tx_hash = None
        tx_receipt = None

        tx_hash = self.connection_manager.fnx_transaction(self.sc,
                                                          'insertBuyLimitOrder',
                                                          base_token,
                                                          secondary_token,
                                                          amount,
                                                          price,
                                                          lifespan,
                                                          default_account=default_account,
                                                          gas_limit=gas_limit)

        if wait_receipt:
            # wait to transaction be mined
            tx_receipt = self.connection_manager.wait_for_transaction_receipt(
                tx_hash,
                timeout=wait_timeout,
                poll_latency=poll_latency)

            self.log.info(
                "Successfully inserted buy limit order in Block  [{0}] Hash: [{1}] Gas used: [{2}] From: [{3}]".format(
                    tx_receipt['blockNumber'],
                    Web3.toHex(tx_receipt['transactionHash']),
                    tx_receipt['gasUsed'],
                    tx_receipt['from']))

        return tx_hash, tx_receipt

    def insert_buy_limit_order(self,
                               base_token,
                               secondary_token,
                               amount,
                               price,
                               lifespan,
                               gas_limit=3500000,
                               wait_timeout=240,
                               default_account=None,
                               wait_receipt=True,
                               poll_latency=0.5):
        """ Inserts an order in the buy orderbook of a given pair without a hint
    the pair should not be disabled; the contract should not be paused. Takes the funds
    with a transferFrom """

        base_token = Web3.toChecksumAddress(base_token)
        secondary_token = Web3.toChecksumAddress(secondary_token)
        amount_sc = int(Decimal(amount) * self.precision)
        price_sc = int(Decimal(price) * self.precision)
        lifespan_sc = int(lifespan)

        if self.paused():
            raise Exception("Contract is paused you cannot operate!")

        tx_hash, tx_receipt = self._insert_buy_limit_order(
            base_token,
            secondary_token,
            amount_sc,
            price_sc,
            lifespan_sc,
            gas_limit=gas_limit,
            wait_timeout=wait_timeout,
            default_account=default_account,
            wait_receipt=wait_receipt,
            poll_latency=poll_latency)

        tx_logs = None
        tx_logs_formatted = None

        if tx_receipt:
            # receipt to logs
            tx_logs = {"NewOrderInserted": self.events.NewOrderInserted().processReceipt(tx_receipt)}
            tx_logs_formatted = {"NewOrderInserted": DEXNewOrderInserted(
                self.connection_manager,
                tx_logs["NewOrderInserted"][0])}

        return tx_hash, tx_receipt, tx_logs, tx_logs_formatted

    def _insert_sell_market_order(self,
                                  base_token,
                                  secondary_token,
                                  amount,
                                  multiply_factor,
                                  lifespan,
                                  gas_limit=3500000,
                                  wait_timeout=240,
                                  default_account=None,
                                  wait_receipt=True,
                                  poll_latency=0.5):
        """ Inserts a market order at start in the buy orderbook of a given pair with a hint;
    the pair should not be disabled; the contract should not be paused. Takes the funds
    with a transferFrom """

        tx_hash = None
        tx_receipt = None
        is_buy = False

        tx_hash = self.connection_manager.fnx_transaction(self.sc,
                                                          'insertMarketOrder',
                                                          base_token,
                                                          secondary_token,
                                                          amount,
                                                          multiply_factor,
                                                          lifespan,
                                                          is_buy,
                                                          default_account=default_account,
                                                          gas_limit=gas_limit)

        if wait_receipt:
            # wait to transaction be mined
            tx_receipt = self.connection_manager.wait_for_transaction_receipt(
                tx_hash,
                timeout=wait_timeout,
                poll_latency=poll_latency)

            self.log.info(
                "Successfully inserted sell market order in Block  [{0}] Hash: [{1}] Gas used: [{2}] From: [{3}]".format(
                    tx_receipt['blockNumber'],
                    Web3.toHex(tx_receipt['transactionHash']),
                    tx_receipt['gasUsed'],
                    tx_receipt['from']))

        return tx_hash, tx_receipt

    def insert_sell_market_order(self,
                                 base_token,
                                 secondary_token,
                                 amount,
                                 multiply_factor,
                                 lifespan,
                                 gas_limit=3500000,
                                 wait_timeout=240,
                                 default_account=None,
                                 wait_receipt=True,
                                 poll_latency=0.5):
        """  Inserts a market order at start in the buy orderbook of a given pair with a hint;
    the pair should not be disabled; the contract should not be paused. Takes the funds
    with a transferFrom """

        base_token = Web3.toChecksumAddress(base_token)
        secondary_token = Web3.toChecksumAddress(secondary_token)
        amount_sc = int(Decimal(amount) * self.precision)
        multiply_factor_sc = int(Decimal(multiply_factor) * self.precision)
        lifespan_sc = int(lifespan)

        if self.paused():
            raise Exception("Contract is paused you cannot operate!")

        tx_hash, tx_receipt = self._insert_sell_market_order(
            base_token,
            secondary_token,
            amount_sc,
            multiply_factor_sc,
            lifespan_sc,
            gas_limit=gas_limit,
            wait_timeout=wait_timeout,
            default_account=default_account,
            wait_receipt=wait_receipt,
            poll_latency=poll_latency)

        tx_logs = None
        tx_logs_formatted = None

        if tx_receipt:
            # receipt to logs
            tx_logs = {"NewOrderInserted": self.events.NewOrderInserted().processReceipt(tx_receipt)}
            tx_logs_formatted = {"NewOrderInserted": DEXNewOrderInserted(
                self.connection_manager,
                tx_logs["NewOrderInserted"][0])}

        return tx_hash, tx_receipt, tx_logs, tx_logs_formatted

    def _insert_buy_market_order(self,
                                 base_token,
                                 secondary_token,
                                 amount,
                                 multiply_factor,
                                 lifespan,
                                 gas_limit=3500000,
                                 wait_timeout=240,
                                 default_account=None,
                                 wait_receipt=True,
                                 poll_latency=0.5):
        """ Inserts a market order at start in the buy orderbook of a given pair with a hint;
    the pair should not be disabled; the contract should not be paused. Takes the funds
    with a transferFrom """

        tx_hash = None
        tx_receipt = None
        is_buy = True

        tx_hash = self.connection_manager.fnx_transaction(self.sc,
                                                          'insertMarketOrder',
                                                          base_token,
                                                          secondary_token,
                                                          amount,
                                                          multiply_factor,
                                                          lifespan,
                                                          is_buy,
                                                          default_account=default_account,
                                                          gas_limit=gas_limit)

        if wait_receipt:
            # wait to transaction be mined
            tx_receipt = self.connection_manager.wait_for_transaction_receipt(
                tx_hash,
                timeout=wait_timeout,
                poll_latency=poll_latency)

            self.log.info(
                "Successfully inserted buy market order in Block  [{0}] Hash: [{1}] Gas used: [{2}] From: [{3}]".format(
                    tx_receipt['blockNumber'],
                    Web3.toHex(tx_receipt['transactionHash']),
                    tx_receipt['gasUsed'],
                    tx_receipt['from']))

        return tx_hash, tx_receipt

    def insert_buy_market_order(self,
                                base_token,
                                secondary_token,
                                amount,
                                multiply_factor,
                                lifespan,
                                gas_limit=3500000,
                                wait_timeout=240,
                                default_account=None,
                                wait_receipt=True,
                                poll_latency=0.5):
        """  Inserts a market order at start in the buy orderbook of a given pair with a hint;
    the pair should not be disabled; the contract should not be paused. Takes the funds
    with a transferFrom """

        base_token = Web3.toChecksumAddress(base_token)
        secondary_token = Web3.toChecksumAddress(secondary_token)
        amount_sc = int(Decimal(amount) * self.precision)
        multiply_factor_sc = int(Decimal(multiply_factor) * self.precision)
        lifespan_sc = int(lifespan)

        if self.paused():
            raise Exception("Contract is paused you cannot operate!")

        tx_hash, tx_receipt = self._insert_buy_market_order(
            base_token,
            secondary_token,
            amount_sc,
            multiply_factor_sc,
            lifespan_sc,
            gas_limit=gas_limit,
            wait_timeout=wait_timeout,
            default_account=default_account,
            wait_receipt=wait_receipt,
            poll_latency=poll_latency)

        tx_logs = None
        tx_logs_formatted = None

        if tx_receipt:
            # receipt to logs
            tx_logs = {"NewOrderInserted": self.events.NewOrderInserted().processReceipt(tx_receipt)}
            tx_logs_formatted = {"NewOrderInserted": DEXNewOrderInserted(
                self.connection_manager,
                tx_logs["NewOrderInserted"][0])}

        return tx_hash, tx_receipt, tx_logs, tx_logs_formatted

    def _cancel_sell_order(self,
                           base_token,
                           secondary_token,
                           order_id,
                           previous_order_id,
                           gas_limit=3500000,
                           wait_timeout=240,
                           default_account=None,
                           wait_receipt=True,
                           poll_latency=0.5):
        """ cancels the sell _orderId order.
    the contract must not be paused; the caller should be the order owner """

        tx_receipt = None
        tx_hash = self.connection_manager.fnx_transaction(self.sc,
                                                          'cancelSellOrder',
                                                          base_token,
                                                          secondary_token,
                                                          order_id,
                                                          previous_order_id,
                                                          default_account=default_account,
                                                          gas_limit=gas_limit)

        if wait_receipt:
            # wait to transaction be mined
            tx_receipt = self.connection_manager.wait_for_transaction_receipt(
                tx_hash,
                timeout=wait_timeout,
                poll_latency=poll_latency)

            self.log.info(
                "Successfully cancell sell order in Block  [{0}] Hash: [{1}] Gas used: [{2}] From: [{3}]".format(
                    tx_receipt['blockNumber'],
                    Web3.toHex(tx_receipt['transactionHash']),
                    tx_receipt['gasUsed'],
                    tx_receipt['from']))

        return tx_hash, tx_receipt

    def cancel_sell_order(self,
                          base_token,
                          secondary_token,
                          order_id,
                          previous_order_id,
                          gas_limit=3500000,
                          wait_timeout=240,
                          default_account=None,
                          wait_receipt=True,
                          poll_latency=0.5):
        """  cancels the sell _orderId order.
    the contract must not be paused; the caller should be the order owner """

        base_token = Web3.toChecksumAddress(base_token)
        secondary_token = Web3.toChecksumAddress(secondary_token)

        if self.paused():
            raise Exception("Contract is paused you cannot operate!")

        tx_hash, tx_receipt = self._cancel_sell_order(
            base_token,
            secondary_token,
            order_id,
            previous_order_id,
            gas_limit=gas_limit,
            wait_timeout=wait_timeout,
            default_account=default_account,
            wait_receipt=wait_receipt,
            poll_latency=poll_latency)

        tx_logs = None
        tx_logs_formatted = None

        if tx_receipt:
            # receipt to logs
            tx_logs = {"OrderCancelled": self.events.OrderCancelled().processReceipt(tx_receipt)}
            tx_logs_formatted = {"OrderCancelled": DEXOrderCancelled(
                self.connection_manager,
                tx_logs["OrderCancelled"][0])}

        return tx_hash, tx_receipt, tx_logs, tx_logs_formatted

    def _cancel_buy_order(self,
                          base_token,
                          secondary_token,
                          order_id,
                          previous_order_id,
                          gas_limit=3500000,
                          wait_timeout=240,
                          default_account=None,
                          wait_receipt=True,
                          poll_latency=0.5):
        """ cancels the buy _orderId order.
    the contract must not be paused; the caller should be the order owner """

        tx_receipt = None
        tx_hash = self.connection_manager.fnx_transaction(self.sc,
                                                          'cancelBuyOrder',
                                                          base_token,
                                                          secondary_token,
                                                          order_id,
                                                          previous_order_id,
                                                          default_account=default_account,
                                                          gas_limit=gas_limit)

        if wait_receipt:
            # wait to transaction be mined
            tx_receipt = self.connection_manager.wait_for_transaction_receipt(
                tx_hash,
                timeout=wait_timeout,
                poll_latency=poll_latency)

            self.log.info(
                "Successfully cancel buy order in Block  [{0}] Hash: [{1}] Gas used: [{2}] From: [{3}]".format(
                    tx_receipt['blockNumber'],
                    Web3.toHex(tx_receipt['transactionHash']),
                    tx_receipt['gasUsed'],
                    tx_receipt['from']))

        return tx_hash, tx_receipt

    def cancel_buy_order(self,
                         base_token,
                         secondary_token,
                         order_id,
                         previous_order_id,
                         gas_limit=3500000,
                         wait_timeout=240,
                         default_account=None,
                         wait_receipt=True,
                         poll_latency=0.5):
        """  cancels the buy _orderId order.
    the contract must not be paused; the caller should be the order owner """

        base_token = Web3.toChecksumAddress(base_token)
        secondary_token = Web3.toChecksumAddress(secondary_token)

        if self.paused():
            raise Exception("Contract is paused you cannot operate!")

        tx_hash, tx_receipt = self._cancel_buy_order(
            base_token,
            secondary_token,
            order_id,
            previous_order_id,
            gas_limit=gas_limit,
            wait_timeout=wait_timeout,
            default_account=default_account,
            wait_receipt=wait_receipt,
            poll_latency=poll_latency)

        tx_logs = None
        tx_logs_formatted = None

        if tx_receipt:
            # receipt to logs
            tx_logs = {"OrderCancelled": self.events.OrderCancelled().processReceipt(tx_receipt)}
            tx_logs_formatted = {"OrderCancelled": DEXOrderCancelled(
                self.connection_manager,
                tx_logs["OrderCancelled"][0])}

        return tx_hash, tx_receipt, tx_logs, tx_logs_formatted

    def withdraw_commissions(self,
                             token,
                             gas_limit=3500000,
                             wait_timeout=240,
                             default_account=None,
                             wait_receipt=True,
                             poll_latency=0.5):
        """
        Withdraws all the already charged(because of a matching, a cancellation or an expiration)
        commissions of a given token
        token Address of the token to withdraw the commissions from
        """

        tx_receipt = None
        tx_hash = self.connection_manager.fnx_transaction(self.sc,
                                                          'withdrawCommissions',
                                                          Web3.toChecksumAddress(token),
                                                          default_account=default_account,
                                                          gas_limit=gas_limit)

        if wait_receipt:
            # wait to transaction be mined
            tx_receipt = self.connection_manager.wait_for_transaction_receipt(tx_hash,
                                                                              timeout=wait_timeout,
                                                                              poll_latency=poll_latency)

            self.log.info(
                "Withdraw commission finished in block [{0}] Hash: [{1}] Gas used: [{2}] From: [{3}]".format(
                    tx_receipt['blockNumber'],
                    Web3.toHex(tx_receipt['transactionHash']),
                    tx_receipt['gasUsed'],
                    tx_receipt['from']))

        tx_logs = None
        tx_logs_formatted = None
        # if tx_receipt:
        #     # receipt to logs
        #     tx_logs = {"CommissionWithdrawn": self.events.CommissionWithdrawn().processReceipt(tx_receipt)}
        #     tx_logs_formatted = {"CommissionWithdrawn": DEXCommissionWithdrawn(
        #         self.connection_manager,
        #         tx_logs["CommissionWithdrawn"][0])}

        return tx_hash, tx_receipt, tx_logs, tx_logs_formatted


class CommissionManager(Contract):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/CommissionManager.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/CommissionManager.bin'))

    mode = 'DEX'
    precision = 10 ** 18

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        if not contract_address:
            # load from connection manager
            network = connection_manager.network
            contract_address = connection_manager.options['networks'][network]['addresses']['commissionManager']

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

        # finally load the contract
        self.load_contract()

    def implementation(self, block_identifier: BlockIdentifier = 'latest'):
        """Implementation of contract"""

        contract_admin = ProxyAdmin(self.connection_manager)
        contract_address = Web3.toChecksumAddress(self.contract_address)

        return contract_admin.implementation(contract_address, block_identifier=block_identifier)

    def beneficiary_address(self, block_identifier: BlockIdentifier = 'latest'):
        """Gets beneficiary destination address """

        result = self.sc.functions.beneficiaryAddress().call(
            block_identifier=block_identifier)

        return result

    def commision_rate(self, formatted: bool = True,
                       block_identifier: BlockIdentifier = 'latest'):
        """Gets commision rate"""

        result = self.sc.functions.commissionRate().call(
            block_identifier=block_identifier)
        if formatted:
            result = Web3.fromWei(result, 'ether')

        return result

    def minimum_commission(self, formatted: bool = True,
                           block_identifier: BlockIdentifier = 'latest'):
        """Get minimum commission"""

        result = self.sc.functions.minimumCommission().call(
            block_identifier=block_identifier)
        if formatted:
            result = Web3.fromWei(result, 'ether')

        return result

    def cancelation_penalty_rate(self, formatted: bool = True,
                                 block_identifier: BlockIdentifier = 'latest'):
        """Gets cancelationPenaltyRate"""

        result = self.sc.functions.cancelationPenaltyRate().call(
            block_identifier=block_identifier)
        if formatted:
            result = Web3.fromWei(result, 'ether')

        return result

    def expiration_penalty_rate(self, formatted: bool = True,
                                block_identifier: BlockIdentifier = 'latest'):
        """Gets expirationPenaltyRate"""

        result = self.sc.functions.expirationPenaltyRate().call(
            block_identifier=block_identifier)
        if formatted:
            result = Web3.fromWei(result, 'ether')

        return result

    def calculate_initial_fee(self,
                              amount: float,
                              price: float,
                              formatted: bool = True,
                              block_identifier: BlockIdentifier = 'latest'):
        """Calculate initial fee. Initial fee is the commission at insertion order"""

        amount_sc = int(Decimal(amount) * self.precision)
        price_sc = int(Decimal(price) * self.precision)

        result = self.sc.functions.calculateInitialFee(amount_sc, price_sc).call(
            block_identifier=block_identifier)
        if formatted:
            result = Web3.fromWei(result, 'ether')

        return result

    def exchange_commissions(self,
                             address: str,
                             formatted: bool = True,
                             block_identifier: BlockIdentifier = 'latest'):
        """Gets exchangeCommissions"""

        result = self.sc.functions.exchangeCommissions(Web3.toChecksumAddress(address)).call(
            block_identifier=block_identifier)
        if formatted:
            result = Web3.fromWei(result, 'ether')

        return result


class BaseConstructor(Contract):
    log = logging.getLogger()

    contract_abi = None
    contract_bin = None

    mode = 'DEX'

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

    def fnx_constructor(self, *tx_parameters, wait_receipt=True):
        """ Constructor deploy """

        sc, content_abi, content_bin = self.connection_manager.load_bytecode_contract(self.contract_abi,
                                                                                      self.contract_bin)
        tx_hash = self.connection_manager.fnx_constructor(sc, *tx_parameters)

        tx_receipt = None
        if wait_receipt:
            tx_receipt = self.connection_manager.wait_for_transaction_receipt(tx_hash)

        return tx_hash, tx_receipt


class TokenPriceProviderLastClosingPrice(BaseConstructor):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/TokenPriceProviderLastClosingPrice.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/TokenPriceProviderLastClosingPrice.bin'))

    mode = 'DEX'

    def constructor(self, base_token, secondary_token):

        network = self.connection_manager.network
        contract_address = self.connection_manager.options['networks'][network]['addresses']['dex']

        self.log.info("Deploying new contract...")

        tx_hash, tx_receipt = self.fnx_constructor(Web3.toChecksumAddress(contract_address),
                                                   Web3.toChecksumAddress(base_token),
                                                   Web3.toChecksumAddress(secondary_token)
                                                   )

        self.log.info("Deployed contract done!")
        self.log.info(Web3.toHex(tx_hash))
        self.log.info(tx_receipt)

        self.log.info("Contract Address: {address}".format(address=tx_receipt.contractAddress))

        return tx_hash, tx_receipt


class MocBproBtcPriceProviderFallback(BaseConstructor):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/MocBproBtcPriceProviderFallback.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/MocBproBtcPriceProviderFallback.bin'))

    mode = 'DEX'

    def constructor(self, moc_state, base_token, secondary_token):

        network = self.connection_manager.network
        contract_address = self.connection_manager.options['networks'][network]['addresses']['dex']

        self.log.info("Deploying new contract...")

        tx_hash, tx_receipt = self.fnx_constructor(Web3.toChecksumAddress(moc_state),
                                                   Web3.toChecksumAddress(contract_address),
                                                   Web3.toChecksumAddress(base_token),
                                                   Web3.toChecksumAddress(secondary_token)
                                                   )

        self.log.info("Deployed contract done!")
        self.log.info(Web3.toHex(tx_hash))
        self.log.info(tx_receipt)

        self.log.info("Contract Address: {address}".format(address=tx_receipt.contractAddress))

        return tx_hash, tx_receipt


class MocBproUsdPriceProviderFallback(BaseConstructor):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/MocBproUsdPriceProviderFallback.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/MocBproUsdPriceProviderFallback.bin'))

    mode = 'DEX'

    def constructor(self, moc_state, base_token, secondary_token):

        network = self.connection_manager.network
        contract_address = self.connection_manager.options['networks'][network]['addresses']['dex']

        self.log.info("Deploying new contract...")

        tx_hash, tx_receipt = self.fnx_constructor(Web3.toChecksumAddress(moc_state),
                                                   Web3.toChecksumAddress(contract_address),
                                                   Web3.toChecksumAddress(base_token),
                                                   Web3.toChecksumAddress(secondary_token)
                                                   )

        self.log.info("Deployed contract done!")
        self.log.info(Web3.toHex(tx_hash))
        self.log.info(tx_receipt)

        self.log.info("Contract Address: {address}".format(address=tx_receipt.contractAddress))

        return tx_hash, tx_receipt


class UnityPriceProvider(BaseConstructor):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/UnityPriceProvider.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/UnityPriceProvider.bin'))

    mode = 'DEX'

    def constructor(self):

        network = self.connection_manager.network
        contract_address = self.connection_manager.options['networks'][network]['addresses']['dex']

        self.log.info("Deploying new contract...")

        tx_hash, tx_receipt = self.fnx_constructor()

        self.log.info("Deployed contract done!")
        self.log.info(Web3.toHex(tx_hash))
        self.log.info(tx_receipt)

        self.log.info("Contract Address: {address}".format(address=tx_receipt.contractAddress))

        return tx_hash, tx_receipt


class ExternalOraclePriceProviderFallback(BaseConstructor):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/ExternalOraclePriceProviderFallback.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/ExternalOraclePriceProviderFallback.bin'))

    mode = 'DEX'

    def constructor(self, external_price_provider, base_token, secondary_token):

        network = self.connection_manager.network
        contract_address = self.connection_manager.options['networks'][network]['addresses']['dex']

        self.log.info("Deploying new contract...")

        tx_hash, tx_receipt = self.fnx_constructor(Web3.toChecksumAddress(external_price_provider),
                                                   Web3.toChecksumAddress(contract_address),
                                                   Web3.toChecksumAddress(base_token),
                                                   Web3.toChecksumAddress(secondary_token)
                                                   )

        self.log.info("Deployed contract done!")
        self.log.info(Web3.toHex(tx_hash))
        self.log.info(tx_receipt)

        self.log.info("Contract Address: {address}".format(address=tx_receipt.contractAddress))

        return tx_hash, tx_receipt


class MocRiskProReservePriceProviderFallback(BaseConstructor):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/MocRiskProReservePriceProviderFallback.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/MocRiskProReservePriceProviderFallback.bin'))

    mode = 'DEX'

    def constructor(self, moc_state, base_token, secondary_token):

        network = self.connection_manager.network
        contract_address = self.connection_manager.options['networks'][network]['addresses']['dex']

        self.log.info("Deploying new contract...")

        tx_hash, tx_receipt = self.fnx_constructor(Web3.toChecksumAddress(moc_state),
                                                   Web3.toChecksumAddress(contract_address),
                                                   Web3.toChecksumAddress(base_token),
                                                   Web3.toChecksumAddress(secondary_token)
                                                   )

        self.log.info("Deployed contract done!")
        self.log.info(Web3.toHex(tx_hash))
        self.log.info(tx_receipt)

        self.log.info("Contract Address: {address}".format(address=tx_receipt.contractAddress))

        return tx_hash, tx_receipt


class MocRiskProUsdPriceProviderFallback(BaseConstructor):
    log = logging.getLogger()

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/MocRiskProUsdPriceProviderFallback.abi'))
    contract_bin = Contract.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi_dex/MocRiskProUsdPriceProviderFallback.bin'))

    mode = 'DEX'

    def constructor(self, moc_state, base_token, secondary_token):

        network = self.connection_manager.network
        contract_address = self.connection_manager.options['networks'][network]['addresses']['dex']

        self.log.info("Deploying new contract...")

        tx_hash, tx_receipt = self.fnx_constructor(Web3.toChecksumAddress(moc_state),
                                                   Web3.toChecksumAddress(contract_address),
                                                   Web3.toChecksumAddress(base_token),
                                                   Web3.toChecksumAddress(secondary_token)
                                                   )

        self.log.info("Deployed contract done!")
        self.log.info(Web3.toHex(tx_hash))
        self.log.info(tx_receipt)

        self.log.info("Contract Address: {address}".format(address=tx_receipt.contractAddress))

        return tx_hash, tx_receipt
