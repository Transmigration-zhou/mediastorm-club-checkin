import pytest

import update_token

SAMPLE = (
    "https://h5.youzan.com/wscump/checkin/checkinV2.json?checkinId=6287727"
    "&app_id=wx92782ef90ebc836d&kdt_id=149536603&access_token=238269c236b8064b6cfeeddd9299f6\n"
    'Extra-Data: {"is_weapp":1,"sid":"YZ1519722428273684480YZt4jlBdyf","version":"2.226.7.101"}\n'
)


def test_parse_credentials_extracts_token_and_sid():
    token, sid = update_token.parse_credentials(SAMPLE)
    assert token == "238269c236b8064b6cfeeddd9299f6"
    assert sid == "YZ1519722428273684480YZt4jlBdyf"


def test_parse_credentials_missing_token_raises():
    with pytest.raises(ValueError):
        update_token.parse_credentials('Extra-Data: {"sid":"YZabc"}')


def test_parse_credentials_missing_sid_raises():
    with pytest.raises(ValueError):
        update_token.parse_credentials("...access_token=abc123...")


def test_write_env_writes_both_keys(tmp_path):
    env_file = tmp_path / ".env"
    update_token.write_env("tok123", "sid456", str(env_file))
    content = env_file.read_text()
    assert "ACCESS_TOKEN=tok123" in content
    assert "SESSION_ID=sid456" in content
