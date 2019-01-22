# aiogetui
Python SDK for Getui push service based on asyncio(aiohttp).
Based on [GeTui rest api](http://docs.getui.com/getui/server/rest/push/).

## Installation
```bash
$ pip install aiogetui
```

## Basic Usage
```python
import asyncio
import uuid
from aiogetui import IGeTui, ToSingleMessage, NotificationTemplate

APP_ID = ''
APP_KEY = ''
MASTER_SECRET = ''
CLIENT_ID = ''


async def run():
    client = IGeTui(APP_ID, APP_KEY, MASTER_SECRET)
    await client.auth_sign()
    message = ToSingleMessage(client_id=CLIENT_ID,
                              template=NotificationTemplate(
                                  {
                                      'title': 'my title',
                                      'text': 'My text.',
                                  }),
                              is_offline=True,  # optional, default to False
                              message_id=uuid.uuid4().hex,  # optional, length 10~32
    )
    _result = await client.push(message)
    await client.close()
    return _result

result = asyncio.get_event_loop().run_until_complete(run())
print(result)
```
