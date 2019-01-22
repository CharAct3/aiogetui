import asyncio

from client import IGeTui
from common import ToSingleMessage
from template import NotificationTemplate

APP_ID = ''
APP_KEY = ''
MASTER_SECRET = ''
CLIENT_ID = ''


def main():
    client = IGeTui(APP_ID, APP_KEY, MASTER_SECRET)

    async def run():
        await client.auth_sign()
        message = ToSingleMessage(client_id=CLIENT_ID,
                                  template=NotificationTemplate(
                                      {
                                          'title': 'my title',
                                          'text': 'My text.',
                                      }
                                  ))
        _result = await client.push(message)
        await client.close()
        return _result

    result = asyncio.get_event_loop().run_until_complete(run())
    print(result)


if __name__ == '__main__':
    main()
