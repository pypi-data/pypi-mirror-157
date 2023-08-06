# Copyright (c) 2021 Emanuele Bellocchia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Module for generating Substrate wallets."""

# Imports
from typing import Any, Dict
from bip_utils import SubstrateKeyError, SubstratePathError, Substrate
from py_crypto_hd_wallet.common import HdWalletBase
from py_crypto_hd_wallet.substrate.hd_wallet_substrate_enum import HdWalletSubstrateDataTypes, HdWalletDataTypes
from py_crypto_hd_wallet.substrate.hd_wallet_substrate_keys import HdWalletSubstrateKeys
from py_crypto_hd_wallet.utils import Utils


class HdWalletSubstrateConst:
    """Class container for HD wallet Substrate constants."""

    # Map data types to dictionary key
    DATA_TYPE_TO_DICT_KEY: Dict[HdWalletDataTypes, str] = {
        HdWalletSubstrateDataTypes.WALLET_NAME: "wallet_name",
        HdWalletSubstrateDataTypes.COIN_NAME: "coin_name",
        HdWalletSubstrateDataTypes.MNEMONIC: "mnemonic",
        HdWalletSubstrateDataTypes.PASSPHRASE: "passphrase",
        HdWalletSubstrateDataTypes.SEED_BYTES: "seed_bytes",
        HdWalletSubstrateDataTypes.PATH: "path",
        HdWalletSubstrateDataTypes.KEY: "key",
    }


class HdWalletSubstrate(HdWalletBase):
    """
    HD wallet Substrate class.
    It allows to generate a Substrate wallet like the official one.
    """

    m_substrate_obj: Substrate
    m_wallet_data: Dict[str, Any]

    #
    # Public methods
    #

    def __init__(self,
                 wallet_name: str,
                 substrate_obj: Substrate,
                 mnemonic: str = "",
                 passphrase: str = "",
                 seed_bytes: bytes = b"") -> None:
        """
        Construct class.

        Args:
            wallet_name (str)               : Wallet name
            substrate_obj (Substrate object): Substrate object
            mnemonic (str, optional)        : Mnemonic, empty if not specified
            passphrase (str, optional)      : Passphrase, empty if not specified
            seed_bytes (bytes, optional)    : Seed_bytes, empty if not specified
        """
        super().__init__(HdWalletSubstrateDataTypes, HdWalletSubstrateConst.DATA_TYPE_TO_DICT_KEY)
        self.m_substrate_obj = substrate_obj
        # Initialize data
        self.__InitData(wallet_name, mnemonic, passphrase, seed_bytes)

    def Generate(self,
                 **kwargs: Any) -> None:
        """
        Generate wallet keys and addresses.

        Other Parameters:
            path (str, optional): Derivation path (default: empty)
        """
        path = kwargs.get("path", "")

        if path != "":
            self._SetData(HdWalletSubstrateDataTypes.PATH, path)

        try:
            substrate_obj = self.m_substrate_obj.DerivePath(path)
            self.__SetKeys(HdWalletSubstrateDataTypes.KEY, substrate_obj)
        except (SubstrateKeyError, SubstratePathError) as ex:
            raise ValueError(f"Invalid path: {path}") from ex

    def IsWatchOnly(self) -> bool:
        """
        Get if the wallet is watch-only.

        Returns :
            bool: True if watch-only, false otherwise
        """
        return self.m_substrate_obj.IsPublicOnly()

    #
    # Private methods
    #

    def __InitData(self,
                   wallet_name: str,
                   mnemonic: str,
                   passphrase: str,
                   seed_bytes: bytes) -> None:
        """
        Initialize data.

        Args:
            wallet_name (str) : Wallet name
            mnemonic (str)    : Mnemonic
            passphrase (str)  : Passphrase
            seed_bytes (bytes): Seed_bytes
        """

        # Set wallet name
        self._SetData(HdWalletSubstrateDataTypes.WALLET_NAME, wallet_name)
        # Set coin name
        coin_names = self.m_substrate_obj.CoinConf().CoinNames()
        self._SetData(HdWalletSubstrateDataTypes.COIN_NAME, f"{coin_names.Name()} ({coin_names.Abbreviation()})")

        # Set optional data if specified
        if mnemonic != "":
            self._SetData(HdWalletSubstrateDataTypes.MNEMONIC, mnemonic)
            self._SetData(HdWalletSubstrateDataTypes.PASSPHRASE, passphrase)
        if seed_bytes != b"":
            self._SetData(HdWalletSubstrateDataTypes.SEED_BYTES, Utils.BytesToHexString(seed_bytes))

    def __SetKeys(self,
                  data_type: HdWalletSubstrateDataTypes,
                  substrate_obj: Substrate) -> None:
        """
        Add keys to wallet data.

        Args:
            data_type (HdWalletSubstrateDataTypes): Data type
            substrate_obj (Substrate object)      : Substrate object
        """
        self._SetData(data_type, HdWalletSubstrateKeys(substrate_obj))
