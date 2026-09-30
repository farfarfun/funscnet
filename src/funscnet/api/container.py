from typing import Any

from farlog import getLogger

from .base import ApiBase

logger = getLogger("funscnet")


class ScNetContainerAPI(ApiBase):
    """
    计算服务网络平台容器管理API封装
    用于查询节点资源限额、创建容器实例和查询容器详情等操作
    """

    def __init__(
        self,
        base_url: str = ApiBase.DEFAULT_BASE_URL,
        api_version: str = ApiBase.API_VERSION,
        token: str | None = None,
    ) -> None:
        """
        初始化容器管理API客户端

        Args:
            base_url: API基础URL，默认为示例环境URL
            api_version: API版本，默认为v2
            token: 默认访问令牌
        """
        super().__init__(base_url, api_version, module="container", token=token)

    def get_resources(
        self,
        token: str,
        resource_group: str | None = None,
        accelerator_type: str | None = None,
    ) -> dict[str, Any]:
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
            "正在获取节点资源限额，资源组={}，加速器类型={}",
            resource_group,
            accelerator_type,
        )
        return self.request(
            "instance-service/resources",
            method="get",
            headers=headers,
            params=params,
            operation="获取节点资源限额",
        )

    def get_resource_groups(self, token: str) -> dict[str, Any]:
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

        return self.request(
            "instance-service/resource-group",
            method="get",
            headers=headers,
            operation="获取资源分组",
        )

    def create_container(
        self, token: str, container_data: dict[str, Any]
    ) -> dict[str, Any]:
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

        return self.request(
            "instance-service/instance/create",
            headers=headers,
            json=container_data,
            operation="创建容器实例",
        )

    def get_container_detail(self, token: str, instance_id: str) -> dict[str, Any]:
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

        logger.info("正在获取容器实例 {} 详情", instance_id)
        return self.request(
            "instance-service/instance/detail",
            method="get",
            headers=headers,
            params=params,
            operation="获取容器实例详情",
        )

    def execute_script(
        self, token: str, instance_ids: list[str], script: str
    ) -> dict[str, Any]:
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

        logger.info("正在执行脚本，实例 ID 列表={}", instance_ids)
        return self.request(
            "instance-service/instance/execute",
            headers=headers,
            json=data,
            operation="执行容器脚本",
        )

    def delete_containers(self, token: str, instance_ids: list[str]) -> dict[str, Any]:
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

        logger.info("正在删除容器实例，实例 ID 列表={}", instance_ids)
        return self.request(
            "instance-service/instance/delete",
            headers=headers,
            json=data,
            operation="删除容器实例",
        )
