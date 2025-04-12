# -*- coding: utf-8 -*-

import json
from typing import Any, Dict, List, Optional

import requests
from funutil import getLogger

from .base import ApiBase

logger = getLogger("funscnet")


class ScNetTokenAPI(ApiBase):
    """
    计算服务网络平台认证授权API封装
    用于获取用户token、集群token和平台token等操作
    """

    def __init__(self, *args, **kwargs):
        """
        初始化认证授权API客户端

        Args:
            base_url: API基础URL，默认为示例环境URL
            api_version: API版本，默认为v2
        """
        super().__init__(*args, module="auth", **kwargs)

    def get_user_tokens(self, user: str, password: str, org_id: str) -> Dict[str, Any]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/safecertification/get-user-tokens.html

        获取用户访问凭证

        调用认证授权接口，认证成功后返回各区域ID、名称以及区域接口访问凭证token

        Args:
            user: 用户名
            password: 用户密码
            org_id: 组织ID

        Returns:
            Dict: 包含认证结果的字典，成功时返回各计算区域的token信息

        Raises:
            ApiException: API异常
        """
        headers = {
            "Content-Type": "application/json",
            "user": user,
            "password": password,
            "orgid": org_id,
        }

        logger.info(f"正在获取用户 {user} 的访问凭证")

        endpoint = self._get_endpoint("tokens")
        response = requests.post(endpoint, headers=headers, data=json.dumps({}))
        return self._process_response(response, "获取访问凭证失败")

    def get_cluster_tokens(
        self, user: str, password: str, org_id: str
    ) -> List[Dict[str, str]]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/safecertification/get-user-tokens.html

        获取所有可用区域的token信息

        Args:
            user: 用户名
            password: 用户密码
            org_id: 组织ID

        Returns:
            List[Dict]: 包含区域信息和token的列表，每个元素包含clusterName、clusterId和token
        """
        result = self.get_user_tokens(user, password, org_id)
        return result.get("data", [])

    def get_token_by_cluster_id(
        self, user: str, password: str, org_id: str, cluster_id: str
    ) -> Optional[str]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/safecertification/get-user-tokens.html

        获取指定计算区域的token

        Args:
            user: 用户名
            password: 用户密码
            org_id: 组织ID
            cluster_id: 计算区域ID

        Returns:
            Optional[str]: 如果指定区域存在且用户有权限，返回token字符串；否则返回None
        """
        logger.info(f"正在获取集群 {cluster_id} 的token")
        clusters = self.get_cluster_tokens(user, password, org_id)

        for cluster in clusters:
            if cluster.get("clusterId") == cluster_id:
                return cluster.get("token")

        logger.warning(f"未找到集群 {cluster_id} 的token")
        return None

    def get_platform_token(
        self, user: str, password: str, org_id: str
    ) -> Optional[str]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/safecertification/get-user-tokens.html

        获取平台自身token (clusterId为0，clusterName为ac的区域)

        Args:
            user: 用户名
            password: 用户密码
            org_id: 组织ID

        Returns:
            Optional[str]: 平台token字符串，如果不存在则返回None
        """
        logger.info("正在获取平台token")
        return self.get_token_by_cluster_id(user, password, org_id, "0")

    def get_center_info(self, token: str) -> Dict[str, Any]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/safecertification/get-center-info.html

        获取授权区域

        返回用户可用区域的信息及url地址、用户集群用户名及家目录等

        Args:
            token: 访问令牌

        Returns:
            Dict: 包含区域信息的字典，包括URL地址、用户集群用户名及家目录等

        Raises:
            ApiException: API异常
        """
        headers = {"Content-Type": "application/json", "token": token}

        logger.info("正在获取授权区域信息")

        endpoint = self._get_endpoint("center-info")
        response = requests.get(endpoint, headers=headers)
        return self._process_response(response, "获取授权区域失败")
