import rlp
import time
from functools import reduce
from typing import Any, Dict, List, Optional, Callable, Union

from eth_account import Account
from eth_account._utils.legacy_transactions import (
    Transaction,
    encode_transaction,
    serializable_unsigned_transaction_from_dict,
)
from eth_account._utils.typed_transactions import (
    AccessListTransaction,
    DynamicFeeTransaction,
)
from eth_typing import HexStr
from hexbytes import HexBytes
from toolz import dissoc
from web3 import Web3
from web3.exceptions import TransactionNotFound
from web3.method import Method
from web3.module import Module
from web3.types import RPCEndpoint, Nonce, TxParams

from .types import (
    FlashbotsOpts,
    FlashbotsBundleRawTx,
    FlashbotsBundleTx,
    FlashbotsBundleDictTx,
    SignedTxAndHash,
    TxReceipt,
)


SECONDS_PER_BLOCK = 15


class FlashbotsRPC:
    eth_sendBundle = RPCEndpoint("eth_sendBundle")
    eth_callBundle = RPCEndpoint("eth_callBundle")
    eth_sendPrivateTransaction = RPCEndpoint("eth_sendPrivateTransaction")
    eth_cancelPrivateTransaction = RPCEndpoint("eth_cancelPrivateTransaction")
    flashbots_getBundleStats = RPCEndpoint("flashbots_getBundleStats")
    flashbots_getUserStats = RPCEndpoint("flashbots_getUserStats")


class FlashbotsBundleResponse:
    w3: Web3
    bundle: List[SignedTxAndHash]
    target_block_number: int

    def __init__(self, w3: Web3, txs: List[HexBytes], target_block_number: int):
        self.w3 = w3

        def parse_tx(tx):
            return {
                "signed_transaction": tx,
                "hash": self.w3.keccak(tx),
            }

        self.bundle = list(map(parse_tx, txs))
        self.target_block_number = target_block_number

    def wait(self) -> None:
        """Waits until the target block has been reached"""
        while self.w3.eth.block_number < self.target_block_number:
            time.sleep(1)

    def receipts(self) -> List[TxReceipt]:
        """Returns all the transaction receipts from the submitted bundle"""
        self.wait()
        return list(
            map(lambda tx: self.w3.eth.get_transaction_receipt(tx["hash"]), self.bundle)
        )


class FlashbotsPrivateTransactionResponse:
    w3: Web3
    tx: SignedTxAndHash
    max_block_number: int

    def __init__(self, w3: Web3, signed_tx: HexBytes, max_block_number: int):
        self.w3 = w3
        self.max_block_number = max_block_number
        self.tx = {
            "signed_transaction": signed_tx,
            "hash": self.w3.sha3(signed_tx),
        }

    def wait(self) -> bool:
        """Waits up to max block number, returns `True` if/when tx has been mined.

        If tx has not been mined by the time the current block > max_block_number, returns `False`."""
        while True:
            try:
                self.w3.eth.get_transaction(self.tx["hash"])
                return True
            except TransactionNotFound:
                if self.w3.eth.block_number > self.max_block_number:
                    return False
                time.sleep(1)

    def receipt(self) -> Optional[TxReceipt]:
        """Gets private tx receipt if tx has been mined. If tx is not mined within `max_block_number` period, returns None."""
        if self.wait():
            return self.w3.eth.get_transaction_receipt(self.tx["hash"])
        else:
            return None


class Flashbots(Module):
    signed_txs: List[HexBytes]
    response: Union[FlashbotsBundleResponse, FlashbotsPrivateTransactionResponse]

    def sign_bundle(
        self,
        bundled_transactions: List[
            Union[FlashbotsBundleTx, FlashbotsBundleRawTx, FlashbotsBundleDictTx]
        ],
    ) -> List[HexBytes]:
        """Given a bundle of signed and unsigned transactions, it signs them all"""
        nonces: Dict[HexStr, Nonce] = {}
        signed_transactions: List[HexBytes] = []

        for tx in bundled_transactions:
            if "signed_transaction" in tx:  # FlashbotsBundleRawTx
                tx_params = _parse_signed_tx(tx["signed_transaction"])
                nonces[tx_params["from"]] = tx_params["nonce"] + 1
                signed_transactions.append(tx["signed_transaction"])

            elif "signer" in tx:  # FlashbotsBundleTx
                signer, tx = tx["signer"], tx["transaction"]
                tx["from"] = signer.address

                if tx.get("nonce") is None:
                    tx["nonce"] = nonces.get(
                        signer.address,
                        self.web3.eth.get_transaction_count(signer.address),
                    )
                nonces[signer.address] = tx["nonce"] + 1

                if "gas" not in tx:
                    tx["gas"] = self.web3.eth.estimateGas(tx)

                signed_tx = signer.sign_transaction(tx)
                signed_transactions.append(signed_tx.rawTransaction)

            elif all(key in tx for key in ["v", "r", "s"]):  # FlashbotsBundleDictTx
                v, r, s = (
                    tx["v"],
                    int(tx["r"].hex(), base=16),
                    int(tx["s"].hex(), base=16),
                )

                tx_dict = {
                    "nonce": tx["nonce"],
                    "data": HexBytes(tx["input"]),
                    "value": tx["value"],
                    "gas": tx["gas"],
                }

                if "maxFeePerGas" in tx or "maxPriorityFeePerGas" in tx:
                    assert "maxFeePerGas" in tx and "maxPriorityFeePerGas" in tx
                    tx_dict["maxFeePerGas"], tx_dict["maxPriorityFeePerGas"] = (
                        tx["maxFeePerGas"],
                        tx["maxPriorityFeePerGas"],
                    )
                else:
                    assert "gasPrice" in tx
                    tx_dict["gasPrice"] = tx["gasPrice"]

                if tx.get("accessList"):
                    tx_dict["accessList"] = tx["accessList"]

                if tx.get("chainId"):
                    tx_dict["chainId"] = tx["chainId"]

                if tx.get("to"):
                    tx_dict["to"] = HexBytes(tx["to"])

                unsigned_tx = serializable_unsigned_transaction_from_dict(tx_dict)
                raw = encode_transaction(unsigned_tx, vrs=(v, r, s))
                assert self.web3.keccak(raw) == tx["hash"]
                signed_transactions.append(raw)

        return signed_transactions

    def to_hex(self, signed_transaction: bytes) -> str:
        tx_hex = signed_transaction.hex()
        if tx_hex[0:2] != "0x":
            tx_hex = f"0x{tx_hex}"
        return tx_hex

    def send_raw_bundle_munger(
        self,
        signed_bundled_transactions: List[HexBytes],
        target_block_number: int,
        opts: Optional[FlashbotsOpts] = None,
    ) -> List[Any]:
        """Given a raw signed bundle, it packages it up with the block number and the timestamps"""
        # convert to hex
        return [
            {
                "txs": list(map(lambda x: self.to_hex(x), signed_bundled_transactions)),
                "blockNumber": hex(target_block_number),
                "minTimestamp": opts["minTimestamp"] if opts else 0,
                "maxTimestamp": opts["maxTimestamp"] if opts else 0,
                "revertingTxHashes": opts["revertingTxHashes"] if opts else [],
            }
        ]

    sendRawBundle: Method[Callable[[Any], Any]] = Method(
        FlashbotsRPC.eth_sendBundle, mungers=[send_raw_bundle_munger]
    )
    send_raw_bundle = sendRawBundle

    def send_bundle_munger(
        self,
        bundled_transactions: List[Union[FlashbotsBundleTx, FlashbotsBundleRawTx]],
        target_block_number: int,
        opts: Optional[FlashbotsOpts] = None,
    ) -> List[Any]:
        signed_txs = self.sign_bundle(bundled_transactions)
        self.response = FlashbotsBundleResponse(
            self.web3, signed_txs, target_block_number
        )
        return self.send_raw_bundle_munger(signed_txs, target_block_number, opts)

    def raw_bundle_formatter(self, resp) -> Any:
        return lambda _: resp.response

    sendBundle: Method[Callable[[Any], Any]] = Method(
        FlashbotsRPC.eth_sendBundle,
        mungers=[send_bundle_munger],
        result_formatters=raw_bundle_formatter,
    )
    send_bundle = sendBundle

    def simulate(
        self,
        bundled_transactions: List[Union[FlashbotsBundleTx, FlashbotsBundleRawTx]],
        block_tag: Union[int, str] = None,
        state_block_tag: int = None,
        block_timestamp: int = None,
    ):
        # interpret block number from tag
        block_number = (
            self.web3.eth.block_number
            if block_tag is None or block_tag == "latest"
            else block_tag
        )

        # sets evm params
        evm_block_number = self.web3.toHex(block_number)
        evm_block_state_number = (
            state_block_tag
            if state_block_tag is not None
            else self.web3.toHex(block_number - 1)
        )
        evm_timestamp = (
            block_timestamp
            if block_timestamp is not None
            else self.extrapolate_timestamp(block_number, self.web3.eth.block_number)
        )

        signed_bundled_transactions = self.sign_bundle(bundled_transactions)
        # calls evm simulator
        call_result = self.call_bundle(
            signed_bundled_transactions,
            evm_block_number,
            evm_block_state_number,
            evm_timestamp,
        )

        return {
            "bundleHash": call_result["bundleHash"],
            "coinbaseDiff": call_result["coinbaseDiff"],
            "results": call_result["results"],
            "signedBundledTransactions": signed_bundled_transactions,
            "totalGasUsed": reduce(
                lambda a, b: a + b["gasUsed"], call_result["results"], 0
            ),
        }

    def extrapolate_timestamp(self, block_tag: int, latest_block_number: int):
        block_delta = block_tag - latest_block_number
        if block_delta < 0:
            raise Exception("block extrapolation negative")
        return self.web3.eth.get_block(latest_block_number)["timestamp"] + (
            block_delta * SECONDS_PER_BLOCK
        )

    def call_bundle_munger(
        self,
        signed_bundled_transactions: List[
            Union[FlashbotsBundleTx, FlashbotsBundleRawTx]
        ],
        evm_block_number,
        evm_block_state_number,
        evm_timestamp,
        opts: Optional[FlashbotsOpts] = None,
    ) -> Any:
        """Given a raw signed bundle, it packages it up with the block number and the timestamps"""
        inpt = [
            {
                "txs": list(map(lambda x: x.hex(), signed_bundled_transactions)),
                "blockNumber": evm_block_number,
                "stateBlockNumber": evm_block_state_number,
                "timestamp": evm_timestamp,
            }
        ]
        return inpt

    call_bundle: Method[Callable[[Any], Any]] = Method(
        json_rpc_method=FlashbotsRPC.eth_callBundle, mungers=[call_bundle_munger]
    )

    def get_user_stats_munger(self) -> List:
        return [{"blockNumber": hex(self.web3.eth.blockNumber)}]

    getUserStats: Method[Callable[[Any], Any]] = Method(
        json_rpc_method=FlashbotsRPC.flashbots_getUserStats,
        mungers=[get_user_stats_munger],
    )
    get_user_stats = getUserStats

    def get_bundle_stats_munger(
        self, bundle_hash: Union[str, int], block_number: Union[str, int]
    ) -> List:
        if isinstance(bundle_hash, int):
            bundle_hash = hex(bundle_hash)
        if isinstance(block_number, int):
            block_number = hex(block_number)
        return [{"bundleHash": bundle_hash, "blockNumber": block_number}]

    getBundleStats: Method[Callable[[Any], Any]] = Method(
        json_rpc_method=FlashbotsRPC.flashbots_getBundleStats,
        mungers=[get_bundle_stats_munger],
    )
    get_bundle_stats = getBundleStats

    # sends private transaction
    # returns tx hash
    def send_private_transaction_munger(
        self,
        transaction: Union[FlashbotsBundleTx, FlashbotsBundleRawTx],
        max_block_number: Optional[int] = None,
    ) -> Any:
        """Sends a single transaction to Flashbots.

        If `max_block_number` is set, Flashbots will try to submit the transaction in every block <= that block (max 25 blocks from present)."""
        signed_transaction: str
        if "signed_transaction" in transaction:
            signed_transaction = transaction["signed_transaction"]
        else:
            signed_transaction = (
                transaction["signer"]
                .sign_transaction(transaction["transaction"])
                .rawTransaction
            )
        if max_block_number is None:
            # get current block num, add 25
            current_block = self.web3.eth.block_number
            max_block_number = current_block + 25
        params = {
            "tx": self.to_hex(signed_transaction),
            "maxBlockNumber": max_block_number,
        }
        self.response = FlashbotsPrivateTransactionResponse(
            self.web3, signed_transaction, max_block_number
        )
        return [params]

    sendPrivateTransaction: Method[Callable[[Any], Any]] = Method(
        json_rpc_method=FlashbotsRPC.eth_sendPrivateTransaction,
        mungers=[send_private_transaction_munger],
        result_formatters=raw_bundle_formatter,
    )
    send_private_transaction = sendPrivateTransaction

    # cancels private tx given pending private tx hash
    # returns True if successful, False otherwise
    def cancel_private_transaction_munger(
        self,
        tx_hash: str,
    ) -> bool:
        """Stops a private transaction from being sent to miners by Flashbots.

        Note: if a transaction has already been received by a miner, it may still be mined. This simply stops further submissions."""
        params = {
            "txHash": tx_hash,
        }
        return [params]

    cancelPrivateTransaction: Method[Callable[[Any], Any]] = Method(
        json_rpc_method=FlashbotsRPC.eth_cancelPrivateTransaction,
        mungers=[cancel_private_transaction_munger],
    )
    cancel_private_transaction = cancelPrivateTransaction


def _parse_signed_tx(signed_tx: HexBytes) -> TxParams:
    # decode tx params based on its type
    tx_type = signed_tx[0]
    if tx_type > int("0x7f", 16):
        # legacy and EIP-155 transactions
        decoded_tx = rlp.decode(signed_tx, Transaction).as_dict()
    else:
        # typed transactions (EIP-2718)
        if tx_type == 1:
            # EIP-2930
            sedes = AccessListTransaction._signed_transaction_serializer
        elif tx_type == 2:
            # EIP-1559
            sedes = DynamicFeeTransaction._signed_transaction_serializer
        else:
            raise ValueError(f"Unknown transaction type: {tx_type}.")
        decoded_tx = rlp.decode(signed_tx[1:], sedes).as_dict()

    # recover sender address and remove signature fields
    decoded_tx["from"] = Account.recover_transaction(signed_tx)
    decoded_tx = dissoc(decoded_tx, "v", "r", "s")
    return decoded_tx
