import hashlib
import traceback

import aiohttp
import time

import asyncio

from aiogetui.common import Message, PushResult
from aiogetui.exceptions import AuthSignFailed


class IGeTui:
    SIGN_URL = 'https://restapi.getui.com/v1/{app_id}/auth_sign'
    PUSH_SINGLE_URL = 'https://restapi.getui.com/v1/{app_id}/push_single'

    def __init__(
        self, app_id, app_key, master_secret, resign_interval=20 * 60, loop=None
    ):
        """
        :param app_id:
        :param app_key:
        :param master_secret:
        :param resign_interval: 单位分钟, 每过多少小时重新刷新 token, 由于限制是 24 小时自动过期, 所以默认 20 小时重新认证
        """
        self.app_id = app_id
        self.app_key = app_key
        self.master_secret = master_secret

        self.loop = loop
        self.session = None

        # sign
        self.sign_url = self.SIGN_URL.format(app_id=self.app_id)
        self.expire_timestamp = None
        self.auth_token = None
        self.lock = None
        self.resign_interval = resign_interval
        assert self.resign_interval > 0

        # push
        self.push_single_url = self.PUSH_SINGLE_URL.format(app_id=self.app_id)

    async def auth_sign(self):
        """用户身份验证通过获得 auth_token 权限令牌，后面的请求都需要带上 auth_token
        """
        if self.session is None:
            self.session = aiohttp.ClientSession(loop=self.loop)

        timestamp = int(time.time() * 1000)
        raw_sign = self.app_key + str(timestamp) + self.master_secret
        sign = hashlib.sha256(raw_sign.encode()).hexdigest()

        sign_params = {'appkey': self.app_key, 'timestamp': timestamp, 'sign': sign}
        json_result = await self._post(self.sign_url, json=sign_params)

        if 'auth_token' not in json_result:
            raise AuthSignFailed(f'Reason: {json_result.get("result")}')
        self.auth_token = json_result['auth_token']
        self.expire_timestamp = timestamp + self.resign_interval * 1000 * 60

    async def push(self, message: Message) -> PushResult:
        """推送消息
        """
        if self.lock is None:
            self.lock = asyncio.Lock()
        async with self.lock:
            # 如果 token 过期, 重新认证一次签名
            timestamp = int(time.time() * 1000)
            if self.expire_timestamp is None or timestamp > self.expire_timestamp:
                await self.auth_sign()

        try:
            json_result = await self._post(
                self.push_single_url, json=message.to_params(self.app_key)
            )
        except aiohttp.ClientError:
            return PushResult(
                PushResult.HTTP_REQUEST_FAILED, description=traceback.format_exc()
            )
        return PushResult(
            json_result.get('result'),
            json_result.get('desc'),
            json_result.get('taskid'),
            json_result.get('status'),
        )

    async def _post(self, url, json=None):
        headers = dict()
        if self.auth_token:
            headers.update({'authtoken': self.auth_token})
        async with self.session.post(url, json=json, headers=headers) as response:
            response.raise_for_status()
            return await response.json(content_type='text/html')

    async def close(self):
        if self.session:
            await self.session.close()
