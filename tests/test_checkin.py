import json
from unittest.mock import MagicMock, patch

import pytest

import checkin


def test_build_extra_data_contains_required_fields():
    result = json.loads(checkin.build_extra_data("test_sid"))
    assert result["is_weapp"] == 1
    assert result["sid"] == "test_sid"
    assert result["client"] == "weapp"
    assert result["bizEnv"] == "wsc"
    assert isinstance(result["ftime"], int)
    assert isinstance(result["uuid"], str)


def test_build_extra_data_uuid_contains_ftime():
    result = json.loads(checkin.build_extra_data("test_sid"))
    assert str(result["ftime"]) in result["uuid"]


def test_build_headers_contains_required_keys():
    headers = checkin.build_headers("test_sid")
    assert "User-Agent" in headers
    assert headers["xweb_xhr"] == "1"
    assert headers["Content-Type"] == "application/json"
    assert "Extra-Data" in headers
    assert headers["Referer"] == "https://servicewechat.com/wx92782ef90ebc836d/17/page-frame.html"


def test_build_headers_extra_data_is_valid_json():
    headers = checkin.build_headers("test_sid")
    data = json.loads(headers["Extra-Data"])
    assert data["sid"] == "test_sid"


def test_do_checkin_success(capsys):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "code": 0,
        "data": {
            "success": True,
            "list": [{"infos": {"title": "10积分"}}],
        },
    }
    with patch("checkin.requests.get", return_value=mock_resp):
        checkin.do_checkin("token123", "sid123")
        mock_resp.raise_for_status.assert_called_once()
    captured = capsys.readouterr()
    assert "10积分" in captured.out


def test_do_checkin_nonzero_code_exits(capsys):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"code": 1, "msg": "token失效"}
    with patch("checkin.requests.get", return_value=mock_resp):
        with pytest.raises(SystemExit) as exc_info:
            checkin.do_checkin("bad_token", "sid")
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "签到失败" in captured.out


def test_do_checkin_success_false_exits():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"code": 0, "data": {"success": False}}
    with patch("checkin.requests.get", return_value=mock_resp):
        with pytest.raises(SystemExit) as exc_info:
            checkin.do_checkin("token", "sid")
    assert exc_info.value.code == 1
