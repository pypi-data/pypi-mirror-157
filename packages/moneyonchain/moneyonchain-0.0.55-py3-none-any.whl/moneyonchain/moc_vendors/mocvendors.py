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
from web3 import Web3
from web3.types import BlockIdentifier

from moneyonchain.contract import ContractBase
from moneyonchain.governance import ProxyAdmin
from moneyonchain.transaction import receipt_to_log

from .utils import array_to_dictionary


class VENDORSMoCVendors(ContractBase):
    contract_name = 'MoCVendors'

    contract_abi = ContractBase.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi/MoCVendors.abi'))
    contract_bin = ContractBase.content_bin_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi/MoCVendors.bin'))

    precision = 10 ** 18
    mode = 'MoC'
    project = 'MoC'

    def __init__(self,
                 network_manager,
                 contract_name=None,
                 contract_address=None,
                 contract_abi=None,
                 contract_bin=None):

        if not contract_address:
            config_network = network_manager.config_network
            contract_address = network_manager.options['networks'][config_network]['addresses']['MoCVendors']

        super().__init__(network_manager,
                         contract_name=contract_name,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

    def implementation(self, block_identifier: BlockIdentifier = 'latest'):
        """Implementation of contract"""

        contract_admin = ProxyAdmin(self.network_manager).from_abi()
        contract_address = Web3.toChecksumAddress(self.contract_address)

        return contract_admin.implementation(contract_address, block_identifier=block_identifier)

    # def get_vendor(self,
    #                vendor_account,
    #                formatted: bool = True,
    #                block_identifier: BlockIdentifier = 'latest'):
    #     """Gets vendor from mapping"""
    #
    #     vendor_details = self.sc.vendors(vendor_account, block_identifier=block_identifier)
    #
    #     names_array = ["isActive", "markup", "totalPaidInMoC", "staking", "paidMoC", "paidRBTC"]
    #
    #     if formatted:
    #         vendor_details = [Web3.fromWei(unformatted_value, 'ether') for unformatted_value in vendor_details[1:]]
    #
    #     return array_to_dictionary(vendor_details, names_array)

    def get_vendor(self,
                   vendor_account,
                   formatted: bool = True,
                   block_identifier: BlockIdentifier = 'latest'):
        """Gets vendor from mapping"""

        vendor_details = self.sc.vendors(vendor_account, block_identifier=block_identifier)

        names_array = ["isActive", "markup", "totalPaidInMoC", "staking", "paidMoC", "paidRBTC"]

        if formatted:
            vendor_details = [vendor_details[0]] + [Web3.fromWei(unformatted_value, 'ether') for unformatted_value in vendor_details[1:]]

        return array_to_dictionary(vendor_details, names_array)

    def get_vendors_addresses(self,
                              block_identifier: BlockIdentifier = 'latest'):
        """Gets all active vendors addresses"""

        vendor_count = self.sc.getVendorsCount(block_identifier=block_identifier)
        result = []

        for i in range(0, vendor_count):
            result.append(self.sc.vendorsList(i, block_identifier=block_identifier))

        return result

    def is_active(self, account, block_identifier: BlockIdentifier = 'latest'):
        """ Gets if a vendor is active
        return true if vendor is active; false otherwise
        """

        account = Web3.toChecksumAddress(account)

        result = self.sc.getIsActive(account, block_identifier=block_identifier)

        return result

    def markup(
            self,
            account,
            formatted: bool = True,
            block_identifier: BlockIdentifier = 'latest'):
        """Gets vendor markup"""

        account = Web3.toChecksumAddress(account)

        result = self.sc.getMarkup(account, block_identifier=block_identifier)

        if formatted:
            result = Web3.fromWei(result, 'ether')

        return result

    def total_paid_in_moc(
            self,
            account,
            formatted: bool = True,
            block_identifier: BlockIdentifier = 'latest'):
        """Gets vendor total paid in MoC"""

        account = Web3.toChecksumAddress(account)

        result = self.sc.getTotalPaidInMoC(account, block_identifier=block_identifier)

        if formatted:
            result = Web3.fromWei(result, 'ether')

        return result

    def staking(
            self,
            account,
            formatted: bool = True,
            block_identifier: BlockIdentifier = 'latest'):
        """Gets vendor staking"""

        account = Web3.toChecksumAddress(account)

        result = self.sc.getStaking(account, block_identifier=block_identifier)

        if formatted:
            result = Web3.fromWei(result, 'ether')

        return result

    def get_vendors(self,
                    formatted: bool = True,
                    block_identifier: BlockIdentifier = 'latest'):
        """Gets all active vendors from mapping"""

        vendors_list = self.get_vendors_addresses()

        result = {}

        for vendor in vendors_list:
            result[vendor] = self.get_vendor(vendor)

        return result

    def register(self,
                 account,
                 markup=0.01,
                 **tx_arguments):
        """
        Allows to register a vendor
        @param account Vendor address
        @param markup Markup which vendor will perceive from mint/redeem operations
        """

        tx_args = self.tx_arguments(**tx_arguments)
        account = Web3.toChecksumAddress(account)

        tx_receipt = self.sc.registerVendor(
            account,
            int(markup * self.precision),
            tx_args)

        tx_receipt.info()
        receipt_to_log(tx_receipt, self.log)

        return tx_receipt

    def unregister(self,
                   account,
                   **tx_arguments):
        """
        Allows to unregister a vendor
        @param account Vendor address
        """

        tx_args = self.tx_arguments(**tx_arguments)
        account = Web3.toChecksumAddress(account)

        tx_receipt = self.sc.unregisterVendor(
            account,
            tx_args)

        tx_receipt.info()
        receipt_to_log(tx_receipt, self.log)

        return tx_receipt

    def add_stake(self,
                  staking,
                  **tx_arguments):
        """
        allows an active vendor (msg.sender) to add staking
        @param staking Staking the vendor wants to add
        """

        tx_args = self.tx_arguments(**tx_arguments)

        tx_receipt = self.sc.addStake(
            int(staking * self.precision),
            tx_args)

        tx_receipt.info()
        receipt_to_log(tx_receipt, self.log)

        return tx_receipt

    def remove_stake(self,
                     staking,
                     **tx_arguments):
        """
        Allows an active vendor (msg.sender) to remove staking
        @param staking Staking the vendor wants to remove
        """

        tx_args = self.tx_arguments(**tx_arguments)

        tx_receipt = self.sc.removeStake(
            int(staking * self.precision),
            tx_args)

        tx_receipt.info()
        receipt_to_log(tx_receipt, self.log)

        return tx_receipt
