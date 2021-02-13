# Wrapper around Web3.py's 
from typing import Callable, Optional, Union, List
from hexbytes.main import HexBytes
from web3 import Web3
from web3.method import Method
from web3.module import ModuleV2
from web3.types import RPCEndpoint, Nonce
from typing import Any

from .types import *
import time

class FlashbotsRPC:
    eth_sendBundle = RPCEndpoint("eth_sendBundle")
    eth_callBundle = RPCEndpoint("eth_callBundle")

class FlashbotsTransactionResponse:
    w3: Web3
    bundle: List[Any]
    target_block_number: int

    def __init__(self, w3: Web3, txs: List[HexBytes], target_block_number: int):
        self.w3 = w3
        # TODO: Parse them instead
        def parse_tx(tx):
            return {
                "signed_transaction": tx,
                "hash": self.w3.sha3(tx),
                # todo, decode and add account/nonce
            }
        self.bundle = list(map(parse_tx, txs))
        self.target_block_number = target_block_number

    def wait(self):
        """ Waits until the target block has been reached """
        while self.w3.eth.blockNumber < self.target_block_number:
            time.sleep(1)

    def simulate(self):
        """ TODO: Implement """
        pass

    def receipts(self):
        """ Returns all the transaction receipts from the submitted bundle """
        self.wait()
        return list(map(lambda tx: self.w3.eth.getTransactionReceipt(tx["hash"]), self.bundle))

class Flashbots(ModuleV2):
    signed_txs: List[HexBytes]
    response: FlashbotsTransactionResponse

    def sign_bundle(
        self,
        bundled_transactions: List[Union[FlashbotsBundleTx, FlashbotsBundleRawTx]],
    ) -> List[HexBytes]:
        """ Given a bundle of signed and unsigned transactions, it signs them all"""
        nonces = {}
        signed_transactions = []
        for tx in bundled_transactions:
            # if it's not given a signer, we assume it's a signed RLP encoded tx,
            if "signer" not in tx:
                # TODO: Figure out how to decode a raw transaction with RLP
                # decoded_tx = rlp.decode(tx["signed_transaction"], sedes=BaseTransactionFields)
                # nonces[decoded_tx["from"]] = decoded_tx["nonce"] + 1
                signed_transactions.append(tx["signed_transaction"])
            else:
                # set all the fields
                signer = tx["signer"]
                tx = tx["transaction"]
                if tx["nonce"] is None:
                    nonce = nonces.get(signer.address) or Nonce(0)
                    tx["nonce"] = nonce
                else:
                    nonce = tx["nonce"]

                # store the new nonce
                nonces[signer.address] = nonce + 1

                # and update the tx details
                tx["from"] = signer.address
                tx["gasPrice"] = 0
                tx["gas"] = self.web3.eth.estimateGas(tx)

                # sign the tx
                signed_tx = signer.sign_transaction(tx)
                signed_transactions.append(signed_tx.rawTransaction)

        return signed_transactions

    def send_raw_bundle_munger(
         self,
         signed_bundled_transactions: List[HexBytes],
         target_block_number: int,
         opts: Optional[FlashbotsOpts] = None,
    ) -> List[Any]:
        """ Given a raw signed bundle, it packages it up with the block numbre and the timestamps """
        # convert to hex
        return [
            list(map(lambda x: x.hex(), signed_bundled_transactions)), 
            hex(target_block_number), 
            opts["minTimestamp"] if opts else 0,
            opts["maxTimestamp"] if opts else 0,
        ]

    sendRawBundle: Method[Callable[[Any], Any]] = Method(
        FlashbotsRPC.eth_sendBundle,
        mungers=[send_raw_bundle_munger],
    )

    def send_bundle_munger(
         self,
         bundled_transactions: List[Union[FlashbotsBundleTx, FlashbotsBundleRawTx]],
         target_block_number: int,
         opts: Optional[FlashbotsOpts] = None,
     ) -> List[Any]:
        signed_txs = self.sign_bundle(bundled_transactions)
        self.response = FlashbotsTransactionResponse(self.web3, signed_txs, target_block_number)
        return self.send_raw_bundle_munger(signed_txs, target_block_number, opts)

    def raw_bundle_formatter(self, resp) -> Any: 
        return lambda _: resp.response

    sendBundle: Method[Callable[[Any], Any]] = Method(
        FlashbotsRPC.eth_sendBundle,
        mungers=[send_bundle_munger],
        result_formatters=raw_bundle_formatter,
    )
