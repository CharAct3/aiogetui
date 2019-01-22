import uuid
from template import Template


class Message:

    def __init__(self,
                 client_id: str,
                 template: Template,
                 is_offline: bool = False,
                 offline_expire_time: int = 0,
                 message_id: str = None,
                 push_info: dict = None):
        """
        :param client_id: 客户端的 id
        :param template: 消息内容模板
        :param is_offline: 是否离线发送
        :param offline_expire_time: 离线消息的有效期(单位: ms)
        :param message_id: 长度为 10~32
        """
        self.client_id = client_id
        self.template = template
        self.is_offline = is_offline
        self.offline_expire_time = offline_expire_time

        if message_id is None:
            self.message_id = uuid.uuid4().hex  # 长度限制为 32
        else:
            self.message_id = message_id

        # 当手机为 ios，并且为离线的时候, 可是通过 push_info 发送消息
        self.push_info = push_info

        self.duration = 0

    def to_params(self, app_key: str):
        raise NotImplementedError


class ToSingleMessage(Message):
    """单独推送的消息
    """

    def to_params(self, app_key: str):
        params = {
            'cid': self.client_id,
            'requestid': self.message_id,
            'message': {
                'appkey': app_key,
                'is_offline': self.is_offline,
                'offline_expire_time': self.offline_expire_time,
                'msgtype': self.template.type,
            },
            self.template.type: self.template.to_dict(),
        }
        if self.push_info:
            params['push_info'] = self.push_info
        return params


class PushResult:
    OK = 'ok'
    INVALID_CLIENT_ID = 'no_user'
    HTTP_REQUEST_FAILED = 'http_request_failed'

    def __init__(self,
                 result: str,
                 description: str=None,
                 task_id: str=None,
                 status: str=None):
        self.result = result
        self.description = description
        self.task_id = task_id
        self.status = status

    def __str__(self):
        return f'PushResult<' \
               f'result: {self.result}, ' \
               f'description: {self.description}, ' \
               f'task_id: {self.task_id}, ' \
               f'status: {self.status}, ' \
               f'>'

    @property
    def is_successful(self):
        return self.status == self.OK

    @property
    def is_client_id_invalid(self):
        return self.status == self.INVALID_CLIENT_ID
