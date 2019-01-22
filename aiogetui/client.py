import hashlib
import traceback
from http import HTTPStatus

import aiohttp
import time

from common import Message, PushResult
from exceptions import AuthSignFailed


class IGeTui:
    SIGN_URL = 'https://restapi.getui.com/v1/{app_id}/auth_sign'
    PUSH_SINGLE_URL = 'https://restapi.getui.com/v1/{app_id}/push_single'

    def __init__(self, app_id, app_key, master_secret, loop=None):
        self.app_id = app_id
        self.app_key = app_key
        self.master_secret = master_secret

        self.loop = loop
        self.session = None

        # sign
        self.sign_url = self.SIGN_URL.format(app_id=self.app_id)
        self.sign_timestamp = None
        self.auth_token = None

        # push
        self.push_single_url = self.PUSH_SINGLE_URL.format(app_id=self.app_id)

    async def auth_sign(self):
        """用户身份验证通过获得auth_token权限令牌，后面的请求都需要带上auth_token
        """
        if self.session is None:
            self.session = aiohttp.ClientSession(loop=self.loop)

        self.sign_timestamp = int(time.time() * 1000)
        raw_sign = self.app_key + str(self.sign_timestamp) + self.master_secret
        sign = hashlib.sha256(raw_sign.encode()).hexdigest()

        sign_params = {
            'appkey': self.app_key,
            'timestamp': self.sign_timestamp,
            'sign': sign,
        }
        json_result = await self._post(self.sign_url, json=sign_params)

        if 'auth_token' not in json_result:
            raise AuthSignFailed(f'Reason: {json_result.get("result")}')
        self.auth_token = json_result['auth_token']

    async def push(self, message: Message) -> PushResult:
        """推送消息
        """
        assert self.auth_token is not None, \
            'No auth_token, cannot send request'

        try:
            json_result = await self._post(self.push_single_url,
                                           json=message.to_params(self.app_key))
        except aiohttp.ClientError:
            return PushResult(PushResult.HTTP_REQUEST_FAILED,
                              description=traceback.format_exc())
        return PushResult(json_result.get('result'),
                          json_result.get('desc'),
                          json_result.get('taskid'),
                          json_result.get('status'))

    async def _post(self, url, json=None):
        headers = dict()
        if self.auth_token:
            headers.update({'authtoken': self.auth_token})
        async with self.session.post(
                url, json=json, headers=headers) as response:
            assert response.status == HTTPStatus.OK
            return await response.json(content_type='text/html')

    async def close(self):
        if self.session:
            await self.session.close()
