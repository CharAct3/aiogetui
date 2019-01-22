class AioGeTuiException(Exception):
    pass


class AuthSignFailed(AioGeTuiException):
    """验证签名失败"""

    pass
