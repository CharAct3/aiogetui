import asyncio

from client import IGeTui
from common import ToSingleMessage
from template import NotificationTemplate

APP_ID = ''
APP_KEY = ''
MASTER_SECRET = ''
CLIENT_ID = ''


def main():
    # 设置 resign_interval, 指定每多少分钟重新签名认证, 默认是 20 小时, 一个 token 24 小时过期
    client = IGeTui(APP_ID, APP_KEY, MASTER_SECRET, resign_interval=60)

    async def run():
        message = ToSingleMessage(
            client_id=CLIENT_ID,
            template=NotificationTemplate({'title': 'my title', 'text': 'My text.'}),
        )
        # auth_sign() 用于验证 app_key 获取 token, 也可以省略, 等第一次 push 时会自动调用 auth_sign()
        # 推荐提前验证
        await client.auth_token()
        result = await client.push(message)
        print(result)
        await client.close()

    asyncio.get_event_loop().run_until_complete(run())


if __name__ == '__main__':
    main()
