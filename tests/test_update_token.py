import subprocess

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


def test_read_capture_stops_when_both_found(monkeypatch):
    feed = iter([
        "...access_token=238269c236b8064b6cfeeddd9299f6...",
        'Extra-Data: {"sid":"YZ1519722428273684480YZt4jlBdyf"}',
        "此行不应被读取",
    ])
    monkeypatch.setattr("builtins.input", lambda: next(feed))
    text = update_token.read_capture()
    token, sid = update_token.parse_credentials(text)
    assert token == "238269c236b8064b6cfeeddd9299f6"
    assert sid == "YZ1519722428273684480YZt4jlBdyf"
    assert "不应被读取" not in text


def test_read_capture_stops_on_eof(monkeypatch):
    def raise_eof():
        raise EOFError
    monkeypatch.setattr("builtins.input", raise_eof)
    assert update_token.read_capture() == ""


@pytest.mark.parametrize("url", [
    "https://github.com/someone/mediastorm-club-checkin.git",
    "https://github.com/someone/mediastorm-club-checkin",
    "git@github.com:someone/mediastorm-club-checkin.git",
])
def test_get_repo_parses_origin(monkeypatch, url):
    monkeypatch.setattr(
        update_token.subprocess, "run",
        lambda *a, **k: subprocess.CompletedProcess(a[0], 0, stdout=url + "\n"),
    )
    assert update_token.get_repo() == "someone/mediastorm-club-checkin"


def test_update_secrets_passes_values_via_stdin(monkeypatch):
    calls = []
    monkeypatch.setattr(
        update_token.subprocess, "run",
        lambda cmd, **k: calls.append((cmd, k.get("input"))) or subprocess.CompletedProcess(cmd, 0),
    )
    update_token.update_secrets("tok123", "sid456", "someone/repo")
    assert calls == [
        (["gh", "secret", "set", "ACCESS_TOKEN", "-R", "someone/repo"], "tok123"),
        (["gh", "secret", "set", "SESSION_ID", "-R", "someone/repo"], "sid456"),
    ]


@pytest.fixture
def main_env(monkeypatch, tmp_path):
    """让 main() 读到 SAMPLE，并把各步骤替换为记录调用的桩。"""
    calls = []
    env_file = tmp_path / ".env"
    monkeypatch.setattr(update_token, "read_capture", lambda: SAMPLE)
    monkeypatch.setattr(update_token, "verify", lambda t, s: calls.append("verify") or True)
    monkeypatch.setattr(update_token, "get_repo", lambda: "someone/repo")
    monkeypatch.setattr(update_token, "update_secrets", lambda t, s, r: calls.append("secrets"))
    real_write_env = update_token.write_env
    monkeypatch.setattr(
        update_token, "write_env",
        lambda t, s: calls.append("env") or real_write_env(t, s, str(env_file)),
    )
    return calls, env_file


def test_main_verifies_before_updating(main_env):
    calls, env_file = main_env
    update_token.main()
    assert calls == ["verify", "secrets", "env"]
    assert "ACCESS_TOKEN=238269c236b8064b6cfeeddd9299f6" in env_file.read_text()


def test_main_verify_failure_changes_nothing(main_env, monkeypatch):
    calls, env_file = main_env
    monkeypatch.setattr(update_token, "verify", lambda t, s: False)
    with pytest.raises(SystemExit) as exc:
        update_token.main()
    assert exc.value.code == 1
    assert calls == []
    assert not env_file.exists()


@pytest.mark.parametrize("error", [
    FileNotFoundError("gh"),
    subprocess.CalledProcessError(1, ["gh", "secret", "set"]),
])
def test_main_gh_failure_exits_without_writing_env(main_env, monkeypatch, error):
    calls, env_file = main_env

    def fail(t, s, r):
        raise error
    monkeypatch.setattr(update_token, "update_secrets", fail)
    with pytest.raises(SystemExit) as exc:
        update_token.main()
    assert exc.value.code == 1
    assert calls == ["verify"]
    assert not env_file.exists()


def test_verify_overrides_env_and_reports_exit_code(monkeypatch):
    seen = {}

    def fake_run(cmd, env=None, **k):
        seen.update(cmd=cmd, env=env)
        return subprocess.CompletedProcess(cmd, 1)
    monkeypatch.setattr(update_token.subprocess, "run", fake_run)
    assert update_token.verify("tok123", "sid456") is False
    assert seen["cmd"][1].endswith("checkin.py")
    assert seen["env"]["ACCESS_TOKEN"] == "tok123"
    assert seen["env"]["SESSION_ID"] == "sid456"
