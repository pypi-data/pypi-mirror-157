from enum import IntEnum

CSV_HEADER = [
    "phone_number",
    "user_address",
    "contract_address",
    "current_balance",
    "send_amount",
    "timestamp",
]

DEFAULT_RPC_PROVIDER = "https://rpc.sarafu.network"
DEFAULT_CHAIN_SPEC = "evm:kitabu:6060:sarafu"
DEFAULT_GAS_LIMIT = 16_000_000


class CSV_Column(IntEnum):
    Phone = 0
    Address = 1
    ContractAddress = 2
    CurrentBalance = 3
    SendAmount = 4
    Timestamp = 5
