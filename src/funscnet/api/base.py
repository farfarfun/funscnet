# -*- coding: utf-8 -*-

import json
from typing import Any, Dict
from urllib.parse import urljoin

import requests
from funutil import getLogger

from funscnet.api.constant import ApiConstants, ApiException

logger = getLogger("funscnet")


class ApiBase:
    """API基类，提供通用方法"""

    API_VERSION = "v2"
    DEFAULT_BASE_URL = "https://www.scnet.cn"

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_version: str = API_VERSION,
        module: str = None,
        token: str = None,
    ):
        """
        初始化API基类

        Args:
            base_url: API基础URL
            api_version: API版本，默认为v2
            module: API模块
        """
        self.base_url = base_url.rstrip("/")
        self.api_version = api_version
        self.module = module
        self.token = token

    def _get_endpoint(self, uri: str) -> str:
        """
        获取API端点URL

        Args:
            uri: API端点相对路径

        Returns:
            API完整URL
        """
        if not self.module:
            raise ValueError("API模块未定义")

        # 获取模块对应的前缀
        module_prefix = {
            "auth": "ac",
            "file": "efile",
            "job": "hpc",
            "container": "ai",
        }.get(self.module)

        if not module_prefix:
            raise ValueError(f"未知的API模块: {self.module}")

        path = f"/{module_prefix}/openapi/{self.api_version}/{uri}"
        return urljoin(self.base_url, path)

    def _process_response(
        self, response: requests.Response, error_msg: str = "API请求失败"
    ) -> Dict[str, Any]:
        """
        处理API响应

        Args:
            response: 请求响应对象
            error_msg: 错误提示

        Returns:
            处理后的响应数据

        Raises:
            ApiException: API异常
        """
        try:
            response.raise_for_status()

            # 对于下载文件等返回二进制内容的API，不解析JSON
            if "application/json" in response.headers.get("Content-Type", ""):
                result = response.json()

                if result.get("code") != ApiConstants.CODE_SUCCESS:
                    error_code = result.get("code", "unknown")
                    error_detail = ApiConstants.ERROR_CODES.get(error_code, "未知错误")
                    error_type = (
                        "auth"
                        if error_code.startswith("1")
                        else "resource"
                        if error_code.startswith(("2", "3", "4"))
                        else "api"
                    )
                    error_msg = f"{error_msg}: {result.get('msg', error_detail)} (错误码: {error_code})"

                    logger.error(f"API错误: {error_msg}")

                    raise ApiException(error_msg, error_code, error_type, result)

                return result
            return {"code": ApiConstants.CODE_SUCCESS, "data": response}

        except requests.HTTPError as e:
            status_code = str(response.status_code)
            error_detail = ApiConstants.ERROR_CODES.get(
                status_code, f"HTTP错误: {str(e)}"
            )
            error_type = "auth" if status_code in ["401", "403"] else "api"
            error_msg = f"{error_msg}: {error_detail} (状态码: {status_code})"

            logger.error(error_msg)

            raise ApiException(error_msg, status_code, error_type, response)

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {str(e)}")
            raise ApiException(
                f"响应解析失败，无效的JSON格式: {str(e)}", response=response
            )
        except Exception as e:
            logger.error(f"未知错误: {str(e)}")
            raise ApiException(f"未知错误: {str(e)}", response=response)

    def request(self, uri, method="post", headers=None, data=None, *args, **kwargs):
        headers = headers or {}
        headers.update({"Content-Type": "application/json", "token": self.token})
        endpoint = self._get_endpoint(uri)
        response = requests.request(
            method, endpoint, headers=headers, data=data, *args, **kwargs
        )
        return self._process_response(response, "上传文件失败")
