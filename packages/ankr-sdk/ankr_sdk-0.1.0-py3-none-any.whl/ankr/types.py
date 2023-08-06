from __future__ import annotations

import enum
from abc import ABC
from typing import Type

import humps
from pydantic import BaseModel


class BlockchainName(str, enum.Enum):
    ETH = "eth"
    BSC = "bsc"
    POLYGON = "polygon"
    FANTOM = "fantom"
    ARBITRUM = "arbitrum"
    AVALANCHE = "avalanche"
    SYSCOIN = "syscoin"


class BlockNumberName(str, enum.Enum):
    latest = "latest"
    earliest = "earliest"


BlockchainNames = BlockchainName | list[BlockchainName] | str
BlockNumber = int | str | BlockNumberName
AddressOrAddresses = str | list[str]
Topics = str | list[str | list[str]]


class RPCModel(BaseModel):
    class Config:
        alias_generator = humps.camelize
        allow_population_by_field_name = True


class RPCRequestPaginated(ABC, RPCModel):
    page_token: str | None = None


class RPCReplyPaginated(ABC, RPCModel):
    next_page_token: str | None = None
    _iter_type: Type


class GetNFTsByOwnerRequest(RPCRequestPaginated):
    blockchain: BlockchainNames
    wallet_address: str
    filter: list[dict[str, list[str]]] | None = None
    page_token: str | None = None
    page_size: int | None = None


class Attribute(RPCModel):
    trait_type: str | None = None
    value: str | None = None
    display_type: str | None = None
    bunny_id: str | None = None
    count: int | None = None
    frequency: str | None = None
    mp_score: str | None = None
    rarity: str | None = None


class Nft(RPCModel):
    blockchain: BlockchainName
    name: str
    token_id: str
    token_url: str
    image_url: str
    collection_name: str
    symbol: str
    contract_type: str
    contract_address: str
    quantity: str | None = None
    traits: list[Attribute] | None = None


class GetNFTsByOwnerReply(RPCReplyPaginated):
    owner: str
    assets: list[Nft]
    next_page_token: str


class GetNFTMetadataRequest(RPCModel):
    blockchain: BlockchainName
    contract_address: str
    token_id: str


class NftAttributes(RPCModel):
    token_url: str
    image_url: str
    name: str
    description: str
    contract_type: int
    traits: list[Attribute] | None = None


class NftMetadata(RPCModel):
    blockchain: BlockchainName
    contract_address: str
    token_id: str
    contract_type: int


class GetNFTMetadataReply(RPCModel):
    metadata: NftMetadata | None = None
    attributes: NftAttributes | None = None


class Balance(RPCModel):
    blockchain: str
    token_name: str
    token_symbol: str
    token_decimals: int
    token_type: str
    holder_address: str
    balance: str
    balance_raw_integer: str
    balance_usd: str
    token_price: str
    thumbnail: str
    contract_address: str | None = None


class GetAccountBalanceReply(RPCReplyPaginated):
    total_balance_usd: str
    assets: list[Balance]
    next_page_token: str | None = None


class GetAccountBalanceRequest(RPCRequestPaginated):
    blockchain: BlockchainName | list[BlockchainName] | None
    wallet_address: str
    page_token: str | None = None
    page_size: int | None = None


class GetTokenHoldersRequest(RPCRequestPaginated):
    blockchain: BlockchainName
    contract_address: str
    page_token: str | None = None
    page_size: int | None = None


class HolderBalance(RPCModel):
    holder_address: str
    balance: str
    balance_raw_integer: str


class GetTokenHoldersReply(RPCReplyPaginated):
    blockchain: BlockchainName
    contract_address: str
    token_decimals: int
    holders: list[HolderBalance]
    holders_count: int
    next_page_token: str


class GetTokenHoldersCountRequest(RPCRequestPaginated):
    blockchain: BlockchainName
    contract_address: str
    page_token: str | None = None
    page_size: int | None = None


class DailyHolderCount(RPCModel):
    holder_count: int
    total_amount: str
    total_amount_raw_integer: str
    last_updated_at: str


class GetTokenHoldersCountReply(RPCReplyPaginated):
    blockchain: BlockchainName
    contract_address: str
    token_decimals: int
    holder_count_history: list[DailyHolderCount]
    next_page_token: str


class GetCurrenciesRequest(RPCModel):
    blockchain: BlockchainName


class CurrencyDetailsExtended(RPCModel):
    blockchain: BlockchainName
    address: str | None
    name: str
    decimals: int
    symbol: str
    thumbnail: str


class GetCurrenciesReply(RPCModel):
    currencies: list[CurrencyDetailsExtended]


class GetUsdPriceRequest(RPCModel):
    blockchain: BlockchainName
    contract_address: str


class GetUsdPriceReply(RPCModel):
    usd_price: str
    blockchain: BlockchainName
    contract_address: str | None = None


class EventInput(RPCModel):
    name: str
    type: str
    indexed: bool
    size: int
    value_decoded: str


class Event(RPCModel):
    name: str
    inputs: list[EventInput]
    anonymous: bool
    string: str
    signature: str
    id: str
    verified: bool


class Log(RPCModel):
    address: str
    topics: list[str]
    data: str
    block_number: str
    transaction_hash: str
    transaction_index: str
    block_hash: str
    log_index: str
    removed: bool
    event: Event | None = None


class GetLogsReply(RPCReplyPaginated):
    logs: list[Log]
    next_page_token: str | None = None


class GetLogsRequest(RPCRequestPaginated):
    blockchain: BlockchainName | list[BlockchainName]
    from_block: BlockNumber | None = None
    to_block: BlockNumber | None = None
    address: str | list[str] | None = None
    topics: Topics | None = None
    page_token: str | None = None
    page_size: int | None = None
    decode_logs: bool | None = None


class GetBlocksRequest(RPCModel):
    blockchain: BlockchainName
    from_block: BlockNumber | None = None
    to_block: BlockNumber | None = None
    desc_order: bool | None = None
    include_logs: bool | None = None
    include_txs: bool | None = None
    decode_logs: bool | None = None
    decode_tx_data: bool | None = None


class MethodInput(RPCModel):
    name: str
    type: str
    size: int
    value_decoded: str


class Method(RPCModel):
    name: str
    inputs: list[MethodInput]
    string: str
    signature: str
    id: str
    verified: bool


class Transaction(RPCModel):
    class Config:
        fields = {
            "from_address": "from",
            "to_address": "to",
        }

    v: str
    r: str
    s: str
    nonce: str
    gas: str
    gas_price: str
    input: str
    block_number: str
    to_address: str | None
    from_address: str
    transaction_index: str
    block_hash: str
    value: str
    type: str
    contract_address: str | None
    cumulative_gas_used: str
    gas_used: str
    logs: list[Log]
    logs_bloom: str
    transaction_hash: str
    hash: str
    status: str
    blockchain: str
    timestamp: str
    method: Method | None


class Block(RPCModel):
    blockchain: str
    int: str
    hash: str
    parent_hash: str
    nonce: str
    mix_hash: str
    sha3_uncles: str
    logs_bloom: str
    state_root: str
    miner: str
    difficulty: str
    extra_data: str
    size: str
    gas_limit: str
    gas_used: str
    timestamp: str
    transactions_root: str
    receipts_root: str
    total_difficulty: str
    transactions: list[Transaction]
    uncles: list[str]


class GetBlocksReply(RPCModel):
    blocks: list[Block]


class GetTransactionsByHashRequest(RPCModel):
    blockchain: BlockchainName | list[BlockchainName] | None
    transaction_hash: str
    include_logs: bool | None = None
    decode_logs: bool | None = None
    decode_tx_data: bool | None = None


class GetTransactionsByHashReply(RPCModel):
    transactions: list[Transaction]
