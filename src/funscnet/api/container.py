# -*- coding: utf-8 -*-


from typing import Any, Dict, List

import requests
from funutil import getLogger

from .base import ApiBase

logger = getLogger("funscnet")


class ScNetContainerAPI(ApiBase):
    """
    计算服务网络平台容器管理API封装
    用于查询节点资源限额、创建容器实例和查询容器详情等操作
    """

    def __init__(self, *args, **kwargs):
        """
        初始化容器管理API客户端

        Args:
            base_url: API基础URL，默认为示例环境URL
            api_version: API版本，默认为v2
        """
        super().__init__(*args, module="container", **kwargs)

    def get_resources(
        self, token: str, resource_group: str = None, accelerator_type: str = None
    ) -> Dict[str, Any]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/container/resources.html

        获取节点资源限额

        Args:
            token: 访问令牌
            resource_group: 资源组，如"TeslaM40"
            accelerator_type: 加速器类型，如"gpu"

        Returns:
            Dict: 节点资源限额信息

        Raises:
            ApiException: API异常
        """
        headers = {"Content-Type": "application/json", "token": token}

        params = {}
        if resource_group:
            params["resourceGroup"] = resource_group
        if accelerator_type:
            params["acceleratorType"] = accelerator_type

        logger.info(
            f"正在获取节点资源限额，资源组: {resource_group}, 加速器类型: {accelerator_type}"
        )

        endpoint = self._get_endpoint("instance-service/resources")
        response = requests.get(endpoint, headers=headers, params=params)
        return self._process_response(response, "获取节点资源限额失败")

    def get_resource_groups(self, token: str) -> Dict[str, Any]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/container/group.html

        获取资源分组

        Args:
            token: 访问令牌

        Returns:
            Dict: 资源分组信息

        Raises:
            ApiException: API异常
        """
        headers = {"Content-Type": "application/json", "token": token}

        logger.info("正在获取资源分组")

        endpoint = self._get_endpoint("instance-service/resource-group")
        response = requests.get(endpoint, headers=headers)
        return self._process_response(response, "获取资源分组失败")

    def create_container(
        self, token: str, container_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/container/create.html

        创建容器实例

        Args:
            token: 访问令牌
            container_data: 容器实例数据，包含资源组、工作目录、CPU数量等

        Returns:
            Dict: 创建结果

        Raises:
            ApiException: API异常
        """
        headers = {"Content-Type": "application/json", "token": token}

        logger.info("正在创建容器实例")

        endpoint = self._get_endpoint("instance-service/instance/create")
        response = requests.post(endpoint, headers=headers, json=container_data)
        return self._process_response(response, "创建容器实例失败")

    def get_container_detail(self, token: str, instance_id: str) -> Dict[str, Any]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/container/detail.html

        查询容器实例详情

        Args:
            token: 访问令牌
            instance_id: 容器实例ID

        Returns:
            Dict: 容器实例详情

        Raises:
            ApiException: API异常
        """
        headers = {"Content-Type": "application/json", "token": token}

        params = {"instanceId": instance_id}

        logger.info(f"正在获取容器实例 {instance_id} 详情")

        endpoint = self._get_endpoint("instance-service/instance/detail")
        response = requests.get(endpoint, headers=headers, params=params)
        return self._process_response(response, "获取容器实例详情失败")

    def execute_script(
        self, token: str, instance_ids: List[str], script: str
    ) -> Dict[str, Any]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/container/execute.html

        批量执行脚本

        Args:
            token: 访问令牌
            instance_ids: 容器实例ID列表
            script: 要执行的脚本内容

        Returns:
            Dict: 执行结果

        Raises:
            ApiException: API异常
        """
        headers = {"Content-Type": "application/json", "token": token}

        data = {"instanceIds": instance_ids, "script": script}

        logger.info(f"正在执行脚本，实例ID列表: {instance_ids}")

        endpoint = self._get_endpoint("instance-service/instance/execute")
        response = requests.post(endpoint, headers=headers, json=data)
        return self._process_response(response, "执行脚本失败")

    def delete_containers(self, token: str, instance_ids: List[str]) -> Dict[str, Any]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/container/delete.html

        批量删除容器

        Args:
            token: 访问令牌
            instance_ids: 容器实例ID列表

        Returns:
            Dict: 删除结果

        Raises:
            ApiException: API异常
        """
        headers = {"Content-Type": "application/json", "token": token}

        data = {"instanceIds": instance_ids}

        logger.info(f"正在删除容器实例，实例ID列表: {instance_ids}")

        endpoint = self._get_endpoint("instance-service/instance/delete")
        response = requests.post(endpoint, headers=headers, json=data)
        return self._process_response(response, "删除容器实例失败")
