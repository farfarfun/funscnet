# 变更日志

## 未发布

### 修复

- `pyproject.toml` 的 `description` 不再是占位项目名，改为据实描述 ScNet API 客户端功能。
- README 最小示例改为调用公开接口 `ScNetJobAPI`，不再构造私有方法 `_get_endpoint` 和不可用的
  `https://example.invalid` 占位地址。
- `[tool.ruff.lint]` 增加 `ignore = ["PLE1205"]`，消除 ruff 对 farlog `{}` 参数化日志的误报。

## 1.0.7 - 未发布

### 新增

- 增加 API 基类和各资源接口的根级测试覆盖。

### 修复

- 保留业务错误的错误码和错误类型，避免被宽泛异常重新包装。
- 修复用户队列响应被重复处理的问题。
- HTTP 请求统一增加超时，并保留网络、状态和 JSON 错误链。

### 变更

- 日志统一迁移到 `farlog`，依赖补充版本下限。
- 使用 uv 锁定依赖并统一 README 安装方式。
- 所有 API 请求携带准确的操作上下文，公开构造器使用明确类型。

### 废弃

- 无。
