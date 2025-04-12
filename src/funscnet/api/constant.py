# -*- coding: utf-8 -*-

from typing import Any

from funutil import getLogger

logger = getLogger("funscnet")


class ApiException(Exception):
    """计算服务网络API异常"""

    def __init__(
        self,
        message: str,
        error_code: str = None,
        error_type: str = "api",
        response: Any = None,
    ):
        self.message = message
        self.error_code = error_code
        self.error_type = error_type  # 可以是 "auth", "resource", "api" 等
        self.response = response
        super().__init__(self.message)


class ApiConstants:
    """API常量定义"""

    # 响应码
    CODE_SUCCESS = "0"

    # 错误码映射
    ERROR_CODES = {
        # 通用错误码
        "0": "成功",
        "-1": "系统内部错误",
        "401": "未授权，请检查token是否有效",
        "403": "无权限访问该资源",
        "404": "请求的资源不存在",
        "500": "服务器内部错误",
        # 认证授权错误码
        "10001": "用户名或密码错误",
        "10002": "用户不存在",
        "10003": "组织ID不存在",
        "10004": "token已过期",
        "10005": "token无效",
        # 文件操作错误码
        "20001": "文件不存在",
        "20002": "路径不存在",
        "20003": "无文件操作权限",
        "20004": "文件上传失败",
        "20005": "文件下载失败",
        "20006": "文件名无效",
        # 作业管理错误码
        "30001": "调度器ID无效",
        "30002": "作业ID不存在",
        "30003": "队列不存在或无权限",
        "30004": "作业提交参数无效",
        "30005": "集群不存在或已下线",
        # 容器管理错误码
        "40001": "资源组不存在",
        "40002": "容器实例不存在",
        "40003": "资源不足",
        "40004": "容器创建失败",
        "40005": "脚本执行失败",
        "40006": "容器删除失败",
    }
