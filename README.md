# funscnet

面向 ScNet 计算服务网络平台的 Python API 客户端，提供文件、作业、容器和令牌管理接口。

## 安装

```bash
uv sync
```

## 最小示例

```python
from funscnet import ApiBase

api = ApiBase(base_url="https://example.invalid", module="job", token="token")
print(api._get_endpoint("cluster"))
```

输出：`https://example.invalid/hpc/openapi/v2/cluster`。

测试使用 `uv run pytest`，所有网络请求测试均使用 mock。

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
