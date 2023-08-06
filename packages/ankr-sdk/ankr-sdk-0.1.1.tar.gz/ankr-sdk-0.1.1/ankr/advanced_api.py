from __future__ import annotations

from typing import Any, Iterable

from ankr import types
from ankr.provider import AnkrProvider


class AnkrAdvancedAPI:
    def __init__(
        self,
        api_key: str | None = None,
        endpoint_uri: str | None = None,
    ) -> None:
        self.provider = AnkrProvider(api_key or "", endpoint_uri)

    def get_logs(
        self,
        blockchain: types.BlockchainNames,
        from_block: types.BlockNumber | None = None,
        to_block: types.BlockNumber | None = None,
        address: types.AddressOrAddresses | None = None,
        topics: types.Topics | None = None,
        decode_logs: bool | None = None,
        **kwargs: Any,
    ) -> Iterable[types.Log]:
        for reply in self.provider.call_method_paginated(
            "ankr_getLogs",
            types.GetLogsRequest(
                blockchain=blockchain,
                from_block=from_block,
                to_block=to_block,
                address=address,
                topics=topics,
                decode_logs=decode_logs,
                **kwargs,
            ),
            types.GetLogsReply,
        ):
            yield from reply.logs

    def get_blocks(
        self,
        blockchain: types.BlockchainName,
        from_block: types.BlockNumber | None = None,
        to_block: types.BlockNumber | None = None,
        desc_order: bool | None = None,
        include_logs: bool | None = None,
        include_txs: bool | None = None,
        decode_logs: bool | None = None,
        decode_tx_data: bool | None = None,
        **kwargs: Any,
    ) -> list[types.Block]:
        reply = self.provider.call_method(
            "ankr_getBlocks",
            types.GetBlocksRequest(
                blockchain=blockchain,
                from_block=from_block,
                to_block=to_block,
                desc_order=desc_order,
                include_logs=include_logs,
                include_txs=include_txs,
                decode_logs=decode_logs,
                decode_tx_data=decode_tx_data,
                **kwargs,
            ),
            types.GetBlocksReply,
        )
        return reply.blocks

    def get_nfts(
        self,
        blockchain: types.BlockchainNames,
        wallet_address: str,
        filter: list[dict[str, list[str]]] | None = None,
        **kwargs: Any,
    ) -> Iterable[types.Nft]:
        for reply in self.provider.call_method_paginated(
            "ankr_getNFTsByOwner",
            types.GetNFTsByOwnerRequest(
                blockchain=blockchain,
                wallet_address=wallet_address,
                filter=filter,
                **kwargs,
            ),
            types.GetNFTsByOwnerReply,
        ):
            yield from reply.assets
