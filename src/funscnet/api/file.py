# -*- coding: utf-8 -*-

import os
from typing import Any, BinaryIO, Dict, List, Optional, Union

from funutil import getLogger

from funscnet.api.base import ApiBase

logger = getLogger("funscnet")


class ScNetFileAPI(ApiBase):
    """
    计算服务网络平台文件API封装
    用于文件列表查询、文件下载等操作
    """

    def __init__(self, *args, **kwargs):
        """
        初始化文件API客户端

        Args:
            base_url: API基础URL，默认为示例环境URL
            api_version: API版本，默认为v2
        """
        super().__init__(module="file", *args, **kwargs)

    def list_files(
        self,
        path: str = None,
        limit: int = 20,
        start: int = 0,
        order: str = "asc",
        order_by: str = "name",
    ) -> Dict[str, Any]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/efile/list.html

        查询文件列表

        Args:
            path: 文件路径
            limit: 每页限制数量
            start: 起始索引
            order: 排序方式，asc或desc
            order_by: 排序字段

        Returns:
            Dict: 文件列表信息

        Raises:
            ApiException: API异常
        """
        params = {"limit": limit, "start": start, "order": order, "orderBy": order_by}
        if path:
            params["path"] = path
        logger.info(f"正在获取文件列表，路径: {path}")
        return self.request(uri="list", method="get", params=params)

    def upload_file(
        self, file_path: str, remote_dir: str, cover: str = "uncover"
    ) -> Dict[str, Any]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/efile/upload.html

        上传文件到服务器

        Args:
            file_path: 本地文件路径
            remote_dir: 远程服务器目录
            cover: 是否覆盖，默认为"uncover"不覆盖

        Returns:
            Dict: 上传结果

        Raises:
            ApiException: API异常
            FileNotFoundError: 本地文件不存在
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"本地文件不存在: {file_path}")
        file_name = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            files = {"file": (file_name, f, "application/octet-stream")}
            data = {"cover": cover, "path": remote_dir}
            logger.info(f"正在上传文件 {file_name} 到 {remote_dir}")
            return self.request(uri="upload", method="post", data=data, files=files)

    def download_file(
        self, path: str, save_path: Optional[str] = None
    ) -> Union[BinaryIO, str]:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/efile/download.html

        下载文件/文件夹

        下载文件或文件夹，文件夹会被压缩为zip格式

        Args:
            token: 访问令牌
            path: 要下载的文件路径
            save_path: 保存文件的本地路径，如果为None则返回文件内容

        Returns:
            Union[BinaryIO, str]: 如果save_path为None，返回文件内容；否则返回保存的文件路径

        Raises:
            ApiException: API异常
            IOError: 文件保存错误
        """
        params = {"path": path}
        logger.info(f"正在下载文件 {path}")
        response = self.request(
            uri="download",
            method="get",
            params=params,
            stream=True,  # 流式下载，适合大文件
        )

        # 如果没有指定保存路径，直接返回文件内容
        if save_path is None:
            return response.get("data")

        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

        # 保存文件
        with open(save_path, "wb") as f:
            for chunk in response.get("data").iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logger.info(f"文件已保存至: {save_path}")
        return save_path

    def download_check(self, paths: List[str]) -> bool:
        """
        API文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/efile/download-check.html

        文件下载校验

        检查文件是否可以下载

        Args:
            paths: 文件路径列表

        Returns:
            bool: 如果所有文件都可以下载则返回True，否则抛出异常

        Raises:
            ApiException: API异常
        """
        params = {"paths": ",".join(paths)}
        logger.info(f"正在检查文件下载权限，路径: {paths}")
        self.request(uri="download-check", method="get", params=params)
        return True
