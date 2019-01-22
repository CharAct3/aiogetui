class Template:
    """消息模板
    有四种:
    1. notification, 点击通知直接打开应用
    2. link, 用户点击时, 可以打开指定的网页
    3. notypopload, 弹窗通知, 用户点击可直接下载文件/应用, 可用于检测版本更新
    4. transmission, 透传消, 是指消息传递到客户端只有消息内容, 展现的形式由客户端自行定义
    """

    type = None

    def to_dict(self):
        raise NotImplementedError


class NotificationTemplate(Template):
    type = 'notification'

    def __init__(
        self,
        style: dict,
        transmission_type: bool = None,
        transmission_content: str = None,
        duration_begin: str = None,
        duration_end: str = None,
    ):
        """
        除了 style, 都可以缺省
        :param style: {
                   "type": 0,
                   "text": "请填写通知内容",
                   "title": "请填写通知标题",
                   "logo": "logo.png",
                   "logourl": "http://xxxx/a.png",
                   "is_ring": true,
                   "is_vibrate": true,
                   "is_clearable": true
                 }
        :param transmission_type: 收到消息是否立即启动应用, true 为立即启动,
                                  false 则广播等待启动
        :param transmission_content: 透传内容, 由用户自定义及客户端自行处理
        :param duration_begin: 设定展示开始时间, 格式为 yyyy-MM-dd HH:mm:ss
        :param duration_end: 展示结束时间，格式为 yyyy-MM-dd HH:mm:ss
        """
        self.style = style
        if 'type' not in self.style:
            self.style['type'] = 0
        self.transmission_type = transmission_type
        self.transmission_content = transmission_content
        self.duration_begin = duration_begin
        self.duration_end = duration_end

    def to_dict(self):
        result = dict()
        result['style'] = self.style
        if self.transmission_type is not None:
            result['transmission_type'] = self.transmission_type
        if self.transmission_content is not None:
            result['transmission_content'] = self.transmission_content
        if self.duration_begin is not None:
            result['duration_begin'] = self.duration_begin
        if self.duration_end is not None:
            result['duration_end'] = self.duration_end
        return result
