# -*- coding: utf-8 -*-

from typing import Any, Dict

import requests
from funutil import getLogger

from .base import ApiBase

logger = getLogger("funscnet")


class ScNetJobAPI(ApiBase):
    """
    计算服务网络平台作业管理API封装
    用于查询集群信息、提交作业、查询作业等操作
    """

    def __init__(self, *args, **kwargs):
        """
        初始化作业管理API客户端

        Args:
            base_url: API基础URL，默认为示例环境URL
            api_version: API版本，默认为v2
        """
        super().__init__(*args, module="job", **kwargs)

    def get_cluster_info(self, token: str) -> Dict[str, Any]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/jobmanager/list-cluster.html

        查询集群信息

        获取集群信息，获取到的ID号即为后续作业接口需要使用的调度器ID，获取到的text为后续作业接口需要使用的集群名称

        Args:
            token: 访问令牌

        Returns:
            Dict: 集群信息，包含调度器ID和集群名称等

        Raises:
            ApiException: API异常
        """
        headers = {"Content-Type": "application/json", "token": token}

        logger.info("正在获取集群信息")

        endpoint = self._get_endpoint("cluster")
        response = requests.get(endpoint, headers=headers)
        return self._process_response(response, "获取集群信息失败")

    def get_user_queues(self, token: str, scheduler_id: str) -> Dict[str, Any]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/jobmanager/query-user-queue.html

        查询用户可访问队列

        Args:
            token: 访问令牌
            scheduler_id: 调度器ID，可通过查询集群信息获取

        Returns:
            Dict: 用户可访问的队列信息

        Raises:
            ApiException: API异常
        """
        headers = {"Content-Type": "application/json", "token": token}

        params = {"schedulerId": scheduler_id}

        logger.info(f"正在获取用户可访问队列，调度器ID: {scheduler_id}")

        endpoint = self._get_endpoint("scheduler-user/queue")
        response = requests.get(endpoint, headers=headers, params=params)
        return self._process_response(response, "获取用户队列失败")

    def submit_job(
        self, token: str, scheduler_id: str, job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/jobmanager/job.html

        提交作业

        Args:
            token: 访问令牌
            scheduler_id: 调度器ID，可通过查询集群信息获取
            job_data: 作业数据，包含队列名称、作业名称、工作目录、命令等

        Returns:
            Dict: 提交结果

        Raises:
            ApiException: API异常
        """
        headers = {"Content-Type": "application/json", "token": token}

        # 确保作业数据包含调度器ID
        if "schedulerId" not in job_data:
            job_data["schedulerId"] = scheduler_id

        logger.info(f"正在提交作业，调度器ID: {scheduler_id}")

        endpoint = self._get_endpoint("job")
        response = requests.post(endpoint, headers=headers, json=job_data)
        return self._process_response(response, "提交作业失败")

    def get_job_detail(
        self, token: str, job_id: str, scheduler_id: str
    ) -> Dict[str, Any]:
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
        headers = {"Content-Type": "application/json", "token": token}

        params = {"jobId": job_id, "schedulerId": scheduler_id}

        logger.info(f"正在获取作业 {job_id} 详情，调度器ID: {scheduler_id}")

        endpoint = self._get_endpoint("job/detail")
        response = requests.get(endpoint, headers=headers, params=params)
        return self._process_response(response, "获取作业详情失败")
