# funscnet

面向 ScNet 计算服务网络平台的 Python API 客户端，提供文件、作业、容器和令牌管理接口。

## 安装

需要 Python 3.10 或更高版本。

安装已发布版本：

```bash
pip install funscnet
```

使用 uv：

```bash
uv add funscnet
```

## 本地开发

克隆仓库后使用以下命令创建本地开发环境并安装测试、格式化工具：

```bash
uv sync
```

## 最小示例

```python
import os

from funscnet import ScNetJobAPI

# token 建议从环境变量或密钥管理服务读取，不要在代码中硬编码
api = ScNetJobAPI(token=os.environ["SCNET_TOKEN"])

# 查询集群信息，返回的 id 即为后续作业接口所需的调度器 ID
clusters = api.get_cluster_info()
scheduler_id = clusters["data"][0]["id"]

# 查询当前用户在该调度器下可访问的队列
queues = api.get_user_queues(scheduler_id)
print(queues)

# 查询指定作业在该调度器上的实时详情
job_detail = api.get_job_detail("job-id", scheduler_id)
print(job_detail)
```

没有真实凭据时，可参考 `tests/test_smoke.py` 中对 `requests` 的 mock 用法在本地跑通调用链路。
所有网络请求测试均使用 mock。开发环境中可运行以下检查：

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
