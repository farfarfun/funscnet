from typing import Any

from farlog import getLogger

from funscnet.api.base import ApiBase

logger = getLogger("funscnet")


class ScNetJobAPI(ApiBase):
    """
    计算服务网络平台作业管理API封装
    用于查询集群信息、提交作业、查询作业等操作
    """

    def __init__(
        self,
        base_url: str = ApiBase.DEFAULT_BASE_URL,
        api_version: str = ApiBase.API_VERSION,
        token: str | None = None,
    ) -> None:
        """
        初始化作业管理API客户端

        Args:
            base_url: API基础URL，默认为示例环境URL
            api_version: API版本，默认为v2
            token: 默认访问令牌
        """
        super().__init__(base_url, api_version, module="job", token=token)

    def get_cluster_info(self) -> dict[str, Any]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/jobmanager/list-cluster.html

        查询集群信息

        获取集群信息，获取到的ID号即为后续作业接口需要使用的调度器ID，获取到的text为后续作业接口需要使用的集群名称

        Args:

        Returns:
            Dict: 集群信息，包含调度器ID和集群名称等

        Raises:
            ApiException: API异常
        """
        return self.request(uri="cluster", method="get", operation="获取集群信息")

    def get_user_queues(self, scheduler_id: str) -> dict[str, Any]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/jobmanager/query-user-queue.html

        查询用户可访问队列

        Args:
            scheduler_id: 调度器ID，可通过查询集群信息获取

        Returns:
            Dict: 用户可访问的队列信息

        Raises:
            ApiException: API异常
        """
        params = {"schedulerId": scheduler_id}
        logger.info("正在获取用户可访问队列，调度器 ID={}", scheduler_id)
        return self.request(
            uri="scheduler-user/queue",
            method="get",
            params=params,
            operation="获取用户队列",
        )

    def submit_job(self, scheduler_id: str, job_data: dict[str, Any]) -> dict[str, Any]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/jobmanager/job.html

        提交作业

        Args:
            scheduler_id: 调度器ID，可通过查询集群信息获取
            job_data: 作业数据，包含队列名称、作业名称、工作目录、命令等

        Returns:
            Dict: 提交结果

        Raises:
            ApiException: API异常
        """
        # 确保作业数据包含调度器ID
        if "schedulerId" not in job_data:
            job_data["schedulerId"] = scheduler_id
        logger.info("正在提交作业，调度器 ID={}", scheduler_id)
        return self.request(
            uri="job",
            method="get",
            json=job_data,
            operation="提交作业",
        )

    def get_job_detail(self, job_id: str, scheduler_id: str) -> dict[str, Any]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/jobmanager/query-job-detail.html

        查询实时作业详情

        Args:
            token: 访问令牌
            job_id: 作业ID
            scheduler_id: 调度器ID

        Returns:
            Dict: 作业详情

        Raises:
            ApiException: API异常
        """
        params = {"jobId": job_id, "schedulerId": scheduler_id}
        logger.info("正在获取作业 {} 详情，调度器 ID={}", job_id, scheduler_id)
        return self.request(
            uri="job/detail",
            method="get",
            params=params,
            operation="获取作业详情",
        )
