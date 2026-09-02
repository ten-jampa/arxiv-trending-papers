import io
import urllib.error
from email.message import Message

import pytest

from founder_radar.arxiv import (
    ArxivRateLimiter,
    USER_AGENT,
    _fetch_url_with_backoff,
    fetch_arxiv_entry,
)


def test_rate_limiter_does_not_sleep_on_first_call() -> None:
    clock = iter([100.0])
    sleeps = []
    limiter = ArxivRateLimiter(min_interval=3.0)

    slept = limiter.wait(clock_fn=lambda: next(clock), sleep_fn=sleeps.append)

    assert slept == 0.0
    assert sleeps == []


def test_rate_limiter_sleeps_remaining_time_within_window() -> None:
    # first call at t=100 (no sleep), second call at t=101 -> only 1s elapsed, need 2s more
    clock_values = iter([100.0, 101.0])
    sleeps = []
    limiter = ArxivRateLimiter(min_interval=3.0)

    limiter.wait(clock_fn=lambda: next(clock_values), sleep_fn=sleeps.append)
    second_sleep = limiter.wait(clock_fn=lambda: next(clock_values), sleep_fn=sleeps.append)

    assert second_sleep == pytest.approx(2.0)
    assert sleeps == [pytest.approx(2.0)]


def test_rate_limiter_does_not_sleep_after_full_interval_elapsed() -> None:
    clock_values = iter([100.0, 104.0])
    sleeps = []
    limiter = ArxivRateLimiter(min_interval=3.0)

    limiter.wait(clock_fn=lambda: next(clock_values), sleep_fn=sleeps.append)
    second_sleep = limiter.wait(clock_fn=lambda: next(clock_values), sleep_fn=sleeps.append)

    assert second_sleep == 0.0
    assert sleeps == []


def _http_error(code: int, retry_after: str | None = None) -> urllib.error.HTTPError:
    headers = Message()
    if retry_after is not None:
        headers["Retry-After"] = retry_after
    return urllib.error.HTTPError(url="https://example.com", code=code, msg="error", hdrs=headers, fp=io.BytesIO(b""))


def test_fetch_url_with_backoff_retries_on_429_then_succeeds() -> None:
    attempts = {"count": 0}

    def fake_opener(request, timeout):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise _http_error(429)
        return io.BytesIO(b"<ok/>")

    sleeps = []
    result = _fetch_url_with_backoff(
        "https://example.com",
        timeout=5,
        max_retries=3,
        base_delay=3.0,
        opener=fake_opener,
        sleep_fn=sleeps.append,
    )

    assert result == b"<ok/>"
    assert attempts["count"] == 2
    assert sleeps == [3.0]


def test_fetch_url_with_backoff_respects_retry_after_header() -> None:
    attempts = {"count": 0}

    def fake_opener(request, timeout):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise _http_error(429, retry_after="10")
        return io.BytesIO(b"<ok/>")

    sleeps = []
    _fetch_url_with_backoff(
        "https://example.com",
        timeout=5,
        max_retries=3,
        base_delay=3.0,
        opener=fake_opener,
        sleep_fn=sleeps.append,
    )

    assert sleeps == [10.0]


def test_fetch_url_with_backoff_raises_after_max_retries() -> None:
    def fake_opener(request, timeout):
        raise _http_error(429)

    sleeps = []
    with pytest.raises(RuntimeError):
        _fetch_url_with_backoff(
            "https://example.com",
            timeout=5,
            max_retries=2,
            base_delay=3.0,
            opener=fake_opener,
            sleep_fn=sleeps.append,
        )

    assert sleeps == [3.0, 6.0]


def test_fetch_url_with_backoff_does_not_retry_non_429_http_errors() -> None:
    def fake_opener(request, timeout):
        raise _http_error(404)

    sleeps = []
    with pytest.raises(urllib.error.HTTPError):
        _fetch_url_with_backoff(
            "https://example.com",
            timeout=5,
            max_retries=3,
            base_delay=3.0,
            opener=fake_opener,
            sleep_fn=sleeps.append,
        )

    assert sleeps == []


def test_fetch_arxiv_entry_sends_descriptive_user_agent() -> None:
    captured = {}

    atom_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<feed xmlns="http://www.w3.org/2005/Atom">'
        '<entry><id>http://arxiv.org/abs/1234.5678v1</id></entry>'
        "</feed>"
    ).encode()

    def fake_opener(request, timeout):
        captured["user_agent"] = request.get_header("User-agent")
        return io.BytesIO(atom_xml)

    limiter = ArxivRateLimiter(min_interval=0.0)
    fetch_arxiv_entry(
        "1234.5678v1",
        timeout=5,
        rate_limiter=limiter,
        opener=fake_opener,
        sleep_fn=lambda _seconds: None,
    )

    assert captured["user_agent"] == USER_AGENT
    assert "founder-radar" in USER_AGENT
