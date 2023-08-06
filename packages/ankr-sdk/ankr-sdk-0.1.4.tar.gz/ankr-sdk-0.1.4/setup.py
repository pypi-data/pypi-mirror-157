# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ankr']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.1,<2.0.0', 'pyhumps>=3.7.2,<4.0.0', 'web3>=5.29.2,<6.0.0']

setup_kwargs = {
    'name': 'ankr-sdk',
    'version': '0.1.4',
    'description': "Compact Python library for interacting with Ankr's Advanced APIs.",
    'long_description': '# ⚓️ Ankr Python SDK\n\nCompact Python library for interacting with Ankr\'s [Advanced APIs](https://www.ankr.com/advanced-api/).\n\n## Get started in 2 minutes\n\n#### 1. Install the package from PyPi\n\n```bash\npip install ankr-sdk\n```\n\n#### 2. Initialize the SDK\n\n```python3\nfrom ankr import AnkrAdvancedAPI, types\n\nankr_api = AnkrAdvancedAPI()\n```\n\n####3. Use the sdk and call one of the supported methods\n\n```python3\nfrom ankr.types import BlockchainName\n\nnfts = ankr_api.get_nfts(\n    blockchain=BlockchainName.ETH,\n    wallet_address="0x0E11A192d574b342C51be9e306694C41547185DD",\n    filter=[\n        {"0x700b4b9f39bb1faf5d0d16a20488f2733550bff4": []},\n        {"0xd8682bfa6918b0174f287b888e765b9a1b4dc9c3": ["8937"]},\n    ],\n)\n```\n\n## Supported chains\n\n`ankr-sdk` supports the following chains at this time:\n\n- ETH: `"eth"`\n- BSC: `"bsc"`\n- Polygon: `"polygon"`\n- Fantom: `"fantom"`\n- Arbitrum: `"arbitrum"`\n- Avalanche: `"avalanche"`\n- Syscoin NEVM: `"syscoin"`\n\n## Available methods\n\n`ankr-sdk` supports the following methods:\n\n- [`get_nfts`](#get_nfts)\n- [`get_logs`](#get_logs)\n- [`get_blocks`](#get_blocks)\n\n#### `get_logs`\n\nGet logs matching the filter.\n\n```python3\nlogs = ankr_api.get_logs(\n    blockchain="eth",\n    from_block="0xdaf6b1",\n    to_block=14350010,\n    address=["0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"],\n    topics=[\n        [],\n        ["0x000000000000000000000000def1c0ded9bec7f1a1670819833240f027b25eff"],\n    ],\n    decode_logs=True,\n)\n```\n\n#### `get_blocks`\n\nQuery data about blocks within a specified range.\n\n```python3\nblocks = ankr_api.get_blocks(\n    blockchain="eth",\n    from_block=14500001,\n    to_block=14500001,\n    desc_order=True,\n    include_logs=True,\n    include_txs=True,\n    decode_logs=True,\n)\n```\n\n#### `get_nfts`\n\nGet data about all the NFTs (collectibles) owned by a wallet.\n\n````python3\nnfts = ankr_api.get_nfts(\n    blockchain="eth",\n    wallet_address="0x0E11A192d574b342C51be9e306694C41547185DD",\n    filter=[\n        {"0x700b4b9f39bb1faf5d0d16a20488f2733550bff4": []},\n        {"0xd8682bfa6918b0174f287b888e765b9a1b4dc9c3": ["8937"]},\n    ],\n)\n````\n\n\n### About API keys\n\nFor now, Ankr is offering _free_ access to these APIs with no request limits i.e. you don\'t need an API key at this time.\n\nLater on, these APIs will become a part of Ankr Protocol\'s [Premium Plan](https://www.ankr.com/protocol/plan/).\n',
    'author': 'Roman Fasakhov',
    'author_email': 'romanfasakhov@ankr.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://ankr.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
