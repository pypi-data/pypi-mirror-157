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

"""Module for P2PKH address encoding/decoding."""

# Imports
from enum import auto, Enum, unique
from typing import Any, Union
from bip_utils.addr.addr_dec_utils import AddrDecUtils
from bip_utils.addr.addr_key_validator import AddrKeyValidator
from bip_utils.addr.iaddr_decoder import IAddrDecoder
from bip_utils.addr.iaddr_encoder import IAddrEncoder
from bip_utils.base58 import Base58Alphabets, Base58ChecksumError, Base58Decoder, Base58Encoder
from bip_utils.bech32 import Bech32ChecksumError, BchBech32Decoder, BchBech32Encoder
from bip_utils.ecc import IPublicKey
from bip_utils.utils.misc import BytesUtils, CryptoUtils


@unique
class P2PKHPubKeyModes(Enum):
    """Enumerative for P2PKH public key modes."""

    COMPRESSED = auto()
    UNCOMPRESSED = auto()


class P2PKHAddrDecoder(IAddrDecoder):
    """
    P2PKH address decoder class.
    It allows the Pay-to-Public-Key-Hash address decoding.
    """

    @staticmethod
    def DecodeAddr(addr: str,
                   **kwargs: Any) -> bytes:
        """
        Decode a P2PKH address to bytes.

        Args:
            addr (str): Address string

        Other Parameters:
            net_ver (bytes)                        : Net address version
            base58_alph (Base58Alphabets, optional): Base58 alphabet, Bitcoin alphabet by default

        Returns:
            bytes: Public key hash bytes

        Raises:
            ValueError: If the address encoding is not valid
        """
        net_ver_bytes = kwargs["net_ver"]
        base58_alph = kwargs.get("base58_alph", Base58Alphabets.BITCOIN)

        try:
            addr_dec_bytes = Base58Decoder.CheckDecode(addr, base58_alph)
        except Base58ChecksumError as ex:
            raise ValueError("Invalid base58 checksum") from ex
        else:
            # Validate length
            AddrDecUtils.ValidateLength(addr_dec_bytes,
                                        CryptoUtils.Hash160DigestSize() + len(net_ver_bytes))
            # Validate and remove prefix
            return AddrDecUtils.ValidateAndRemovePrefix(addr_dec_bytes, net_ver_bytes)


class P2PKHAddrEncoder(IAddrEncoder):
    """
    P2PKH address encoder class.
    It allows the Pay-to-Public-Key-Hash address encoding.
    """

    @staticmethod
    def EncodeKey(pub_key: Union[bytes, IPublicKey],
                  **kwargs: Any) -> str:
        """
        Encode a public key to P2PKH address.

        Args:
            pub_key (bytes or IPublicKey): Public key bytes or object

        Other Parameters:
            net_ver (bytes)                        : Net address version
            base58_alph (Base58Alphabets, optional): Base58 alphabet, Bitcoin alphabet by default

        Returns:
            str: Address string

        Raises:
            ValueError: If the public key is not valid
            TypeError: If the public key is not secp256k1
        """
        net_ver_bytes = kwargs["net_ver"]
        base58_alph = kwargs.get("base58_alph", Base58Alphabets.BITCOIN)
        pub_key_mode = kwargs.get("pub_key_mode", P2PKHPubKeyModes.COMPRESSED)

        pub_key_obj = AddrKeyValidator.ValidateAndGetSecp256k1Key(pub_key)
        pub_key_bytes = (pub_key_obj.RawCompressed().ToBytes()
                         if pub_key_mode == P2PKHPubKeyModes.COMPRESSED
                         else pub_key_obj.RawUncompressed().ToBytes())

        return Base58Encoder.CheckEncode(net_ver_bytes + CryptoUtils.Hash160(pub_key_bytes), base58_alph)


class P2PKHAddr(P2PKHAddrEncoder):
    """
    P2PKH address class.
    Only kept for compatibility, P2PKHAddrEncoder shall be used instead.
    """


class BchP2PKHAddrDecoder(IAddrDecoder):
    """
    Bitcoin Cash P2PKH address decoder class.
    It allows the Bitcoin Cash P2PKH decoding.
    """

    @staticmethod
    def DecodeAddr(addr: str,
                   **kwargs: Any) -> bytes:
        """
        Decode a Bitcoin Cash P2PKH address to bytes.

        Args:
            addr (str): Address string

        Other Parameters:
            hrp (str)      : HRP
            net_ver (bytes): Net address version

        Returns:
            bytes: Public key hash bytes

        Raises:
            ValueError: If the address encoding is not valid
        """
        hrp = kwargs["hrp"]
        net_ver_bytes = kwargs["net_ver"]

        try:
            net_ver_bytes_got, addr_dec_bytes = BchBech32Decoder.Decode(hrp, addr)
        except Bech32ChecksumError as ex:
            raise ValueError("Invalid bech32 checksum") from ex
        else:
            # Check net version
            if net_ver_bytes != net_ver_bytes_got:
                raise ValueError(f"Invalid net version (expected {BytesUtils.ToHexString(net_ver_bytes)}, "
                                 f"got {BytesUtils.ToHexString(net_ver_bytes_got)})")
            # Validate length
            AddrDecUtils.ValidateLength(addr_dec_bytes,
                                        CryptoUtils.Hash160DigestSize())
            return addr_dec_bytes


class BchP2PKHAddrEncoder(IAddrEncoder):
    """
    Bitcoin Cash P2PKH address encoder class.
    It allows the Bitcoin Cash P2PKH encoding.
    """

    @staticmethod
    def EncodeKey(pub_key: Union[bytes, IPublicKey],
                  **kwargs: Any) -> str:
        """
        Encode a public key to Bitcoin Cash P2PKH address.

        Args:
            pub_key (bytes or IPublicKey): Public key bytes or object

        Other Parameters:
            hrp (str)      : HRP
            net_ver (bytes): Net address version

        Returns:
            str: Address string

        Raises:
            ValueError: If the public key is not valid
            TypeError: If the public key is not secp256k1
        """
        hrp = kwargs["hrp"]
        net_ver_bytes = kwargs["net_ver"]

        pub_key_obj = AddrKeyValidator.ValidateAndGetSecp256k1Key(pub_key)
        return BchBech32Encoder.Encode(hrp,
                                       net_ver_bytes,
                                       CryptoUtils.Hash160(pub_key_obj.RawCompressed().ToBytes()))


class BchP2PKHAddr(BchP2PKHAddrEncoder):
    """
    Bitcoin Cash P2PKH address.
    Only kept for compatibility, BchP2PKHAddrEncoder shall be used instead.
    """
