from datetime import datetime
import os
import sys
import csv
import json

from typing import Any
from tqdm import tqdm
from dotenv import load_dotenv
from web3 import Web3
from redis import Redis  # type: ignore

from constants import ERC_165_ABI, ERC_721_ABI, ERC_721_INTERFACE_ID

load_dotenv()

r: Redis = Redis(host="localhost", port=6379, db=0)
w3 = Web3(Web3.HTTPProvider(os.environ["RPC_URL"]))
DIR_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def get_block_and_transaction_data(record):
    block_number = record["block_number"]
    transaction_index = record["transaction_index"]

    if r.exists(block_number):
        block = json.loads(r.get(block_number).decode("utf-8"))
        transaction = block["transactions"][transaction_index]
    else:
        base_block = w3.eth.get_block(block_number, full_transactions=True)

        block = {
            "block_timestamp": base_block.timestamp,
            "gas_used": base_block.gasUsed,
            "transactions": list(
                map(
                    lambda tx: {
                        "gas": tx.gas,
                        "gas_price": tx.gasPrice,
                        "nonce": tx.nonce,
                    },
                    base_block.transactions,
                )
            ),
        }
        transaction = block["transactions"][transaction_index]
        r.set(block_number, json.dumps(block))

    return record | {
        "block_timestamp": block["block_timestamp"],
        "gas_used": block["gas_used"],
        "gas": transaction["gas"],
        "gas_price": transaction["gas_price"],
        "nonce": transaction["nonce"],
    }


def get_balance_data(record):
    block_number = record["block_number"]
    from_address = record["from"]
    to_address = record["to"]

    from_balance_key = f"{from_address}{block_number}"
    to_balance_key = f"{to_address}{block_number}"

    if r.exists(from_balance_key):
        from_balance = r.get(from_balance_key)
    else:
        from_balance = float(
            w3.fromWei(w3.eth.get_balance(from_address, block_number), "ether")
        )
        r.set(from_balance_key, from_balance)

    if r.exists(to_balance_key):
        to_balance = r.get(to_balance_key)
    else:
        to_balance = float(
            w3.fromWei(w3.eth.get_balance(to_address, block_number), "ether")
        )
        r.set(to_balance_key, to_balance)

    return record | {
        "from_balance": from_balance,
        "to_balance": to_balance,
    }


def get_record_from_log(log, token_name, token_symbol):
    record = {
        "tx_hash": w3.toHex(log["transactionHash"]),
        "block_number": log["blockNumber"],
        "block_hash": w3.toHex(log["blockHash"]),
        "transaction_index": log["transactionIndex"],
        "contract_address": log["address"],
        "from": log["args"]["from"],
        "to": log["args"]["to"],
        "token_id": log["args"]["tokenId"],
        "token_name": token_name,
        "token_symbol": token_symbol,
    }

    return get_balance_data(get_block_and_transaction_data(record))


def write_header(job_hash, path):
    with open(f"{path}/{job_hash}.csv", "w+") as f:
        # with open(f"{DIR_PATH}/completed_jobs/{job_hash}.csv", "w+") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "tx_hash",
                "block_number",
                "block_timestamp",
                "block_hash",
                "contract_address",
                "from",
                "to",
                "token_id",
                "token_name",
                "token_symbol",
                "transaction_index",
                "gas",
                "gas_used",
                "gas_price",
                "nonce",
                "from_balance",
                "to_balance",
            ]
        )


def write_row(writer, record):
    writer.writerow(
        [
            record["tx_hash"],
            record["block_number"],
            record["block_timestamp"],
            record["block_hash"],
            record["contract_address"],
            record["from"],
            record["to"],
            record["token_id"],
            record["token_name"],
            record["token_symbol"],
            record["transaction_index"],
            record["gas"],
            record["gas_used"],
            record["gas_price"],
            record["nonce"],
            record["from_balance"],
            record["to_balance"],
        ]
    )


def write_records(job_hash, contract, from_block, to_block, path):
    token_name = contract.functions.name().call()
    token_symbol = contract.functions.symbol().call()

    current_block = from_block
    end_block = to_block

    while current_block != end_block:
        print(f"In block {current_block} of {end_block}")
        filter = contract.events.Transfer.createFilter(
            fromBlock=current_block, toBlock=current_block + 2000
        )

        if len(filter.get_all_entries()) != 0:
            records = [
                get_record_from_log(entry, token_name, token_symbol)
                for entry in tqdm(filter.get_all_entries())
            ]

            # with open(f"{DIR_PATH}/completed_jobs/{job_hash}.csv", "a+") as f:
            with open(f"{path}/{job_hash}.csv", "a+") as f:
                writer = csv.writer(f)
                for record in records:
                    write_row(writer, record)

        current_block += 2000


def supports_erc_721(address):
    contract_erc_165 = w3.eth.contract(address=address, abi=ERC_165_ABI)

    try:
        return contract_erc_165.functions.supportsInterface(ERC_721_INTERFACE_ID).call()
    except:
        return False


def fetch(job_hash, contract_address, from_block, to_block, path):
    address = w3.toChecksumAddress(contract_address)
    supports_721 = supports_erc_721(address)

    if supports_721:
        contract_erc_721 = w3.eth.contract(address=address, abi=ERC_721_ABI)
        write_header(job_hash, path)
        write_records(job_hash, contract_erc_721, from_block, to_block, path)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise Exception("Invalid cli args provided")
    elif len(sys.argv) == 4:
        fetch(
            f"{sys.argv[1][:10]}_{str(datetime.now().isoformat(timespec='minutes'))}",
            str(sys.argv[1]),
            int(sys.argv[2]),
            int(sys.argv[3]),
            os.getcwd(),
        )
