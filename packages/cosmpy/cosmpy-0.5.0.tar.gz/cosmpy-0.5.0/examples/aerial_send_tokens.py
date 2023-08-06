# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2021 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------
from cosmpy.aerial.client import LedgerClient, NetworkConfig
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.crypto.keypairs import PrivateKey


def main():
    alice = LocalWallet(PrivateKey("X2Tv0Ok3RN2yi9GhWjLUX7RIfX5go9Wu+fwoJlqK2Og="))
    bob = LocalWallet(PrivateKey("p0h0sYImB4xGq3Zz+xfIrY4QR6CPqeNg8w6X3NUWLe4="))

    ledger = LedgerClient(NetworkConfig.fetchai_stable_testnet())

    print(
        f"Alice Address: {alice.address()} Balance: {ledger.query_bank_balance(alice.address())}"
    )
    print(
        f"Bob   Address: {bob.address()} Balance: {ledger.query_bank_balance(bob.address())}"
    )

    tx = ledger.send_tokens(bob.address(), 10, "atestfet", alice)

    print(f"TX {tx.tx_hash} waiting to complete...")
    tx.wait_to_complete()
    print(f"TX {tx.tx_hash} waiting to complete...done")

    print(
        f"Alice Address: {alice.address()} Balance: {ledger.query_bank_balance(alice.address())}"
    )
    print(
        f"Bob   Address: {bob.address()} Balance: {ledger.query_bank_balance(bob.address())}"
    )


if __name__ == "__main__":
    main()
