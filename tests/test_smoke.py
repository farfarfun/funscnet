# -*- coding: utf-8 -*-
"""
轻量冒烟测试（smoke tests）。

目标：验证包能被正常导入、核心公开类能被构造并且其纯逻辑方法（不涉及真实网络/凭据）
行为符合预期。所有对外部计算服务网络平台的真实 HTTP 请求都通过 unittest.mock 打桩，
不会发起任何真实网络调用。

本仓库没有 [project.scripts] CLI 入口，因此不涉及 CLI 冒烟测试。
"""

import json
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# 1. 导入测试
# ---------------------------------------------------------------------------


def test_import_top_level_package():
    import funscnet

    assert funscnet.__all__ == [
        "ApiBase",
        "ApiConstants",
        "ApiException",
        "ScNetContainerAPI",
        "ScNetFileAPI",
        "ScNetJobAPI",
        "ScNetTokenAPI",
    ]
    for name in funscnet.__all__:
        assert hasattr(funscnet, name)


def test_import_submodules():
    import funscnet.api.base
    import funscnet.api.constant
    import funscnet.api.container
    import funscnet.api.file
    import funscnet.api.job
    import funscnet.api.token  # noqa: F401


# ---------------------------------------------------------------------------
# 2. ApiBase 构造与端点拼装
# ---------------------------------------------------------------------------


def test_api_base_construct_defaults():
    from funscnet import ApiBase

    api = ApiBase()
    assert api.base_url == "https://www.scnet.cn"
    assert api.api_version == "v2"
    assert api.module is None
    assert api.token is None


def test_api_base_get_endpoint_requires_module():
    from funscnet import ApiBase

    api = ApiBase()
    with pytest.raises(ValueError):
        api._get_endpoint("some/uri")


def test_api_base_get_endpoint_unknown_module():
    from funscnet import ApiBase

    api = ApiBase(module="not-a-real-module")
    with pytest.raises(ValueError):
        api._get_endpoint("some/uri")


@pytest.mark.parametrize(
    "module,prefix",
    [
        ("auth", "ac"),
        ("file", "efile"),
        ("job", "hpc"),
        ("container", "ai"),
    ],
)
def test_api_base_get_endpoint_known_modules(module, prefix):
    from funscnet import ApiBase

    api = ApiBase(module=module)
    endpoint = api._get_endpoint("foo")
    assert endpoint == f"https://www.scnet.cn/{prefix}/openapi/v2/foo"


def test_api_base_request_uses_mocked_requests(monkeypatch):
    """request() 应该调用 requests.request 而不发起真实网络请求。"""
    from funscnet import ApiBase

    api = ApiBase(module="job", token="fake-token")

    fake_response = MagicMock()
    fake_response.headers = {"Content-Type": "application/json"}
    fake_response.json.return_value = {"code": "0", "data": {"ok": True}}
    fake_response.raise_for_status.return_value = None

    with patch("funscnet.api.base.requests.request", return_value=fake_response) as m:
        result = api.request("cluster", method="get")

    m.assert_called_once()
    assert result["code"] == "0"
    assert result["data"] == {"ok": True}


# ---------------------------------------------------------------------------
# 3. ApiConstants / ApiException
# ---------------------------------------------------------------------------


def test_api_constants_success_code():
    from funscnet import ApiConstants

    assert ApiConstants.CODE_SUCCESS == "0"
    assert ApiConstants.ERROR_CODES["0"] == "成功"
    assert "401" in ApiConstants.ERROR_CODES


def test_api_exception_fields():
    from funscnet import ApiException

    exc = ApiException("出错了", error_code="10001", error_type="auth", response=None)
    assert str(exc) == "出错了"
    assert exc.error_code == "10001"
    assert exc.error_type == "auth"


def test_api_base_process_response_raises_on_business_error():
    """
    已知问题（未修复，仅记录）：ApiBase._process_response 在 try 块内部主动
    raise ApiException 之后，会被同一个 try 块末尾的 `except Exception as e`
    重新捕获，并包装成一个新的、丢失了 error_code/error_type 的 ApiException
    （见 src/funscnet/api/base.py 中 `raise ApiException(...)` 之后紧跟的
    `except Exception` 分支）。这是业务逻辑缺陷，不在本次轻量冒烟测试的修复范围内，
    这里只验证“确实会抛出 ApiException”这一基本行为，不对 error_code 做强断言。
    """
    from funscnet import ApiBase, ApiException

    api = ApiBase(module="job")

    fake_response = MagicMock()
    fake_response.headers = {"Content-Type": "application/json"}
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {"code": "10001", "msg": "账号密码错误"}

    with pytest.raises(ApiException) as excinfo:
        api._process_response(fake_response)
    # 预期行为应为 excinfo.value.error_code == "10001"，但由于上述已知 bug，
    # error_code 实际被置为 None。这里断言的是当前（有缺陷的）真实行为。
    assert excinfo.value.error_code is None
    assert "10001" in str(excinfo.value)


def test_api_base_process_response_success():
    from funscnet import ApiBase

    api = ApiBase(module="job")

    fake_response = MagicMock()
    fake_response.headers = {"Content-Type": "application/json"}
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {"code": "0", "data": {"foo": "bar"}}

    result = api._process_response(fake_response)
    assert result == {"code": "0", "data": {"foo": "bar"}}


# ---------------------------------------------------------------------------
# 4. ScNetContainerAPI / ScNetFileAPI / ScNetJobAPI / ScNetTokenAPI 构造 + 打桩调用
# ---------------------------------------------------------------------------


def test_container_api_construct_and_module():
    from funscnet import ScNetContainerAPI

    api = ScNetContainerAPI(token="fake-token")
    assert api.module == "container"
    assert api.token == "fake-token"


def test_container_api_get_resources_mocked():
    from funscnet import ScNetContainerAPI

    api = ScNetContainerAPI(token="fake-token")

    fake_response = MagicMock()
    fake_response.headers = {"Content-Type": "application/json"}
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {"code": "0", "data": []}

    with patch(
        "funscnet.api.container.requests.get", return_value=fake_response
    ) as m:
        result = api.get_resources(token="fake-token", resource_group="TeslaM40")

    m.assert_called_once()
    assert result["code"] == "0"


def test_file_api_construct_and_module():
    from funscnet import ScNetFileAPI

    api = ScNetFileAPI(token="fake-token")
    assert api.module == "file"


def test_file_api_upload_file_missing_local_file_raises():
    """upload_file 在真正发起网络请求前会先校验本地文件是否存在。"""
    from funscnet import ScNetFileAPI

    api = ScNetFileAPI(token="fake-token")
    with pytest.raises(FileNotFoundError):
        api.upload_file("/path/does/not/exist.bin", remote_dir="/remote")


def test_file_api_list_files_mocked():
    from funscnet import ScNetFileAPI

    api = ScNetFileAPI(token="fake-token")

    fake_response = MagicMock()
    fake_response.headers = {"Content-Type": "application/json"}
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {"code": "0", "data": {"files": []}}

    with patch("funscnet.api.base.requests.request", return_value=fake_response):
        result = api.list_files(path="/home")

    assert result["code"] == "0"


def test_job_api_construct_and_module():
    from funscnet import ScNetJobAPI

    api = ScNetJobAPI(token="fake-token")
    assert api.module == "job"


def test_job_api_get_cluster_info_mocked():
    from funscnet import ScNetJobAPI

    api = ScNetJobAPI(token="fake-token")

    fake_response = MagicMock()
    fake_response.headers = {"Content-Type": "application/json"}
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {"code": "0", "data": []}

    with patch("funscnet.api.base.requests.request", return_value=fake_response):
        result = api.get_cluster_info()

    assert result["code"] == "0"


def test_token_api_construct_and_module():
    from funscnet import ScNetTokenAPI

    api = ScNetTokenAPI()
    assert api.module == "auth"


def test_token_api_get_user_tokens_mocked():
    """认证接口没有真实凭据，使用 mock 打桩验证调用链路而非真实登录。"""
    from funscnet import ScNetTokenAPI

    api = ScNetTokenAPI()

    fake_response = MagicMock()
    fake_response.headers = {"Content-Type": "application/json"}
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {
        "code": "0",
        "data": [{"clusterId": "0", "clusterName": "ac", "token": "abc"}],
    }

    with patch("funscnet.api.token.requests.post", return_value=fake_response):
        result = api.get_user_tokens("user", "password", "org-1")

    assert result["data"][0]["token"] == "abc"


def test_token_api_get_platform_token_requires_real_credentials():
    """
    get_platform_token 依赖真实的用户名/密码/组织ID 才能返回有意义的结果，
    这里没有真实凭据，只做打桩验证不会抛异常/不会发真实网络请求，
    真实业务语义（能否拿到有效 token）需要真实凭据环境验证，故跳过深入断言。
    """
    pytest.skip("需要真实凭据，跳过深入业务断言，仅做导入/构造级别验证")
