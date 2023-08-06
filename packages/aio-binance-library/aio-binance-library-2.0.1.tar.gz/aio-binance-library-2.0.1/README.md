# aio-binance-futures
# Binance Futures Public Async API Connector Python
[![Python 3.7](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This is a lightweight library that works as a connector to [Binance Futures public API](https://binance-docs.github.io/apidocs/futures/en/)

- Supported APIs:
    - USDT-M Futures `/fapi/*``
    - Futures/Delivery Websocket Market Stream
    - Futures/Delivery User Data Stream
- Inclusion of examples
- Response metadata can be displayed

## Installation

```bash
pip install aio-binance
```


## RESTful APIs

Usage examples:
```python
import asyncio
from aio_binance.futures.usdt import Client 

async def main():
    client = Client()
    res = await client.time()
    print(res)

    client = Client(key='<api_key>', secret='<api_secret>')

    # Get account information
    res = await client.account()
    print(res)

    # Post a new order
    params = {
        'symbol': 'BTCUSDT',
        'side': 'SELL',
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': 0.002,
        'price': 59808
    }

    res = await client.new_order(**params)
    print(response)

asyncio.run(main())

```
Please find `examples` folder to check for more endpoints.

### Testnet

You can choose testnet

```python
from aio_binance.futures.usdt import Client

client= Client(testnet=True)
```

### Optional parameters

PEP8 suggests _lowercase with words separated by underscores_, but for this connector,
the methods' optional parameters should follow their exact naming as in the API documentation.

```python
# Recognised parameter name
response = client.query_order('BTCUSDT', orderListId=1)

# Unrecognised parameter name
response = client.query_order('BTCUSDT', order_list_id=1)
```

### Timeout

`timeout` is available to be assigned with the number of seconds you find most appropriate to wait for a server response.<br/>
Please remember the value as it won't be shown in error message _no bytes have been received on the underlying socket for timeout seconds_.<br/>
By default, `timeout=5`

```python
from aio_binance.futures.usdt import Client

client= Client(timeout=1)
```

### Response Metadata

The Binance API server provides weight usages in the headers of each response.
You can display them by initializing the client with `show_limit_usage=True`:

```python
from aio_binance.futures.usdt import Client

client = Client(show_limit_usage=True)
print(client.time())
```
returns:

```python
{'data': {'serverTime': 1647990837551}, 'limit_usage': 40}
```
You can also display full response metadata to help in debugging:

```python
client = Client(show_header=True)
print(client.time())
```

returns:

```python
{'data': {'serverTime': 1587990847650}, 'header': {'Context-Type': 'application/json;charset=utf-8', ...}}
```

### User agent

```python
client = Client(agent='name_app')
```

You can pass the name of your application.


## Websocket

This is an example of connecting to multiple streams

```python
import asyncio

from aio_binance.futures.usdt import WsClient


async def calback_event(data: dict):
    print(data)

async def main():
    ws = WsClient()
    stream = [
        ws.liquidation_order(),
        ws.book_ticker(),
        ws.ticker('BTCUSDT')
    ]
    res = await asyncio.gather(*stream)
    await ws.subscription_streams(res, calback_event)

asyncio.run(main())
```
More websocket examples are available in the `examples` folder

### Heartbeat

Once connected, the websocket server sends a ping frame every 3 minutes and requires a response pong frame back within
a 5 minutes period. This package handles the pong responses automatically.
