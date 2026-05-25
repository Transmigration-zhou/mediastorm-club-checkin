import json
from unittest.mock import patch

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
