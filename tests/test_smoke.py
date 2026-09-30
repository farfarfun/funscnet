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
    """业务错误应保留服务端错误码和错误类型。"""
    from funscnet import ApiBase, ApiException

    api = ApiBase(module="job")

    fake_response = MagicMock()
    fake_response.headers = {"Content-Type": "application/json"}
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {"code": "10001", "msg": "账号密码错误"}

    with pytest.raises(ApiException) as excinfo:
        api._process_response(fake_response)
    assert excinfo.value.error_code == "10001"
    assert excinfo.value.error_type == "auth"
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


def test_api_base_request_wraps_network_error_with_operation():
    import requests

    from funscnet import ApiBase, ApiException

    api = ApiBase(module="job")
    error = requests.Timeout("timed out")
    with (
        patch("funscnet.api.base.requests.request", side_effect=error) as request_mock,
        pytest.raises(ApiException, match="获取集群信息失败") as excinfo,
    ):
        api.request("cluster", method="get", operation="获取集群信息")

    assert excinfo.value.__cause__ is error
    assert request_mock.call_args.kwargs["timeout"] == 30


def test_api_base_process_response_preserves_http_error_chain():
    import requests

    from funscnet import ApiBase, ApiException

    api = ApiBase(module="job")
    response = MagicMock(status_code=503)
    error = requests.HTTPError("unavailable", response=response)
    response.raise_for_status.side_effect = error

    with pytest.raises(ApiException, match="获取集群信息失败") as excinfo:
        api._process_response(response, "获取集群信息失败")

    assert excinfo.value.__cause__ is error
    assert excinfo.value.error_code == "503"


def test_api_base_process_response_preserves_json_error_chain():
    from funscnet import ApiBase, ApiException

    api = ApiBase(module="job")
    response = MagicMock(headers={"Content-Type": "application/json"})
    error = json.JSONDecodeError("bad", "x", 0)
    response.json.side_effect = error

    with pytest.raises(ApiException, match="响应不是有效 JSON") as excinfo:
        api._process_response(response, "获取集群信息失败")

    assert excinfo.value.__cause__ is error


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

    with patch("funscnet.api.base.requests.request", return_value=fake_response) as m:
        result = api.get_resources(token="fake-token", resource_group="TeslaM40")

    m.assert_called_once()
    assert result["code"] == "0"


def test_container_api_public_operations_forward_context():
    from funscnet import ScNetContainerAPI

    api = ScNetContainerAPI(token="client-token")
    result = {"code": "0", "data": {}}
    with patch.object(api, "request", return_value=result) as request_mock:
        assert api.get_resource_groups("token") is result
        assert api.create_container("token", {"name": "demo"}) is result
        assert api.get_container_detail("token", "instance-1") is result
        assert api.execute_script("token", ["instance-1"], "pwd") is result
        assert api.delete_containers("token", ["instance-1"]) is result

    assert [item.kwargs["operation"] for item in request_mock.call_args_list] == [
        "获取资源分组",
        "创建容器实例",
        "获取容器实例详情",
        "执行容器脚本",
        "删除容器实例",
    ]


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


def test_file_api_upload_download_and_check_mocked(tmp_path):
    import requests

    from funscnet import ScNetFileAPI

    api = ScNetFileAPI(token="fake-token")
    source = tmp_path / "source.bin"
    source.write_bytes(b"source")
    payload = MagicMock(spec=requests.Response)
    payload.iter_content.return_value = [b"one", b"", b"two"]
    result = {"code": "0", "data": payload}

    with patch.object(api, "request", return_value=result) as request_mock:
        assert api.upload_file(str(source), "/remote") is result
        assert api.download_file("/remote/file") is payload
        save_path = tmp_path / "downloads" / "file.bin"
        assert api.download_file("/remote/file", str(save_path)) == str(save_path)
        assert save_path.read_bytes() == b"onetwo"
        assert api.download_check(["/remote/file"]) is True

    assert [item.kwargs["operation"] for item in request_mock.call_args_list] == [
        "上传文件",
        "下载文件",
        "下载文件",
        "检查文件下载权限",
    ]


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


def test_job_api_operations_return_processed_response_once():
    from funscnet import ScNetJobAPI

    api = ScNetJobAPI(token="fake-token")
    result = {"code": "0", "data": ["queue"]}
    with (
        patch.object(api, "request", return_value=result) as request_mock,
        patch.object(
            api,
            "_process_response",
            side_effect=AssertionError("response processed twice"),
        ),
    ):
        assert api.get_user_queues("scheduler-1") is result
        assert api.submit_job("scheduler-1", {"name": "demo"}) is result
        assert api.get_job_detail("job-1", "scheduler-1") is result

    assert [item.kwargs["operation"] for item in request_mock.call_args_list] == [
        "获取用户队列",
        "提交作业",
        "获取作业详情",
    ]
    assert request_mock.call_args_list[1].kwargs["json"]["schedulerId"] == "scheduler-1"


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

    with patch("funscnet.api.base.requests.request", return_value=fake_response):
        result = api.get_user_tokens("user", "password", "org-1")

    assert result["data"][0]["token"] == "abc"


def test_token_api_get_platform_token_mocked():
    """平台 token 从 clusterId=0 的 mock 响应中读取，无需真实凭据。"""
    from funscnet import ScNetTokenAPI

    api = ScNetTokenAPI()
    with patch.object(
        api,
        "get_user_tokens",
        return_value={
            "code": "0",
            "data": [{"clusterId": "0", "clusterName": "ac", "token": "abc"}],
        },
    ):
        assert api.get_platform_token("user", "password", "org-1") == "abc"


def test_token_api_missing_cluster_and_center_info_mocked():
    from funscnet import ScNetTokenAPI

    api = ScNetTokenAPI()
    with patch.object(api, "get_user_tokens", return_value={"code": "0", "data": []}):
        assert api.get_token_by_cluster_id("u", "p", "o", "missing") is None

    result = {"code": "0", "data": {"center": "demo"}}
    with patch.object(api, "request", return_value=result) as request_mock:
        assert api.get_center_info("token") is result
    request_mock.assert_called_once_with(
        "center",
        method="get",
        headers={"Content-Type": "application/json", "token": "token"},
        operation="获取授权区域",
    )
