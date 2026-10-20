"""The company logos kit's custom steps (web-app/references/company-logos.md):
a fake web, a settable clock, and reads of a logo record and the store.

Copied into the project's `tests/` and imported by the test module that
runs `company_logos.feature`:

    from logo_steps import *  # noqa: F401,F403  (the steps and the fixture)

    @pytest.fixture
    def application() -> Application:
        return Application(servicers=SERVICERS)

    scenarios("company_logos.feature")

What the app provides, and the only things these steps touch. Substitute
`__pkg__` below with the app's package; keep the rest by building to it:

- `logos`, the app's fetch module in `backend/src/logos.py`, with
  - `async def get(client, url, cap, keep_first=False)`: the one call
    that reaches the network, a GET returning `(final_url,
    content_type, body)` or None. Every fetch (page, icon, logo.dev,
    each redirect) goes through it, called as the module's global, so
    the fake below replaces it whole. It does its checks with
    `logo_safety` before connecting; the fake stands in after them.
  - `def now() -> float`: the clock every due-check and `checked_at`
    reads, called as the module's global.
  - `SITE_FETCHER: int`: the site fetcher's version, read when a
    verdict is recorded and when one is judged due.
  - `LOGO_DEV_URL = "https://img.logo.dev/{host}"`: logo.dev's address,
    asked with its query (token, size, format, `fallback=404`).
  - It reads `LOGO_SOURCE` ("site" or "logo.dev") and `LOGO_DEV_TOKEN`
    when it fetches, never at import.
- `logo_store`, in `backend/src/logo_store.py`, with `store()` returning
  an object with `async get(host) -> (content_type, image) | None`.
  `LOGO_STORE=dir` and `LOGO_STORE_DIR` choose a directory store, read
  when `store()` is called.
- The generated `Logo` and `Logos` (the API table in the reference),
  the singleton's id `LOGOS_ID`, and `USER`, the signed-in account the
  Background declares, whom these steps call and read as.
"""

import asyncio
import json
import re
import struct
import time
from pathlib import Path
from typing import Any, Iterator, Optional
from unittest import mock

import logo_store
import logos
import pytest
from __pkg__.v1.__pkg___rbt import Logo, Logos
from reboot.bdd import given, parsers, then
from reboot.bdd.fixtures import World

LOGOS_ID = "logos"
USER = "alice"
DAY = 24 * 60 * 60

# The web, as far as these scenarios can see it: a URL (without its
# query) to what a GET of it answers. Filled by the Given steps before
# anything asks, and only read after, so the fake is a pure function of
# its arguments while a fetch runs: the harness re-runs every memoized
# external call to validate it, and keeps the second answer.
WEB: dict[str, tuple[str, str, bytes]] = {}
# URLs that never answer: a GET of one times out, the way a page behind
# bot protection does.
STALLS: set[str] = set()


try:
    # What an httpx GET raises when a site never answers: the app's fetch
    # counts it, for that one URL, as nothing found there (an
    # `httpx.HTTPError`), and goes on to the next.
    from httpx import ReadTimeout as NeverAnswered
except ImportError:  # An app fetching with another client: its timeout.
    NeverAnswered = TimeoutError  # type: ignore[assignment,misc]


def png(width: int) -> bytes:
    """A PNG's signature and header: all `logo_safety.sniff` reads."""
    return b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct.pack(">II", width, width) + b"\x08\x06\x00\x00\x00"


async def fake_get(client: object, url: str, cap: int, keep_first: bool = False) -> Optional[tuple[str, str, bytes]]:
    bare = url.split("?", 1)[0]
    if bare in STALLS:
        raise NeverAnswered(f"{bare} never answered")
    return WEB.get(bare)


def page(host: str, links: str) -> None:
    url = f"https://{host}/"
    WEB[url] = (url, "text/html", f"<html><head>{links}</head><body></body></html>".encode())


def icon(url: str, width: int) -> None:
    WEB[url] = (url, "image/png", png(width))


@pytest.fixture(autouse=True)
def fake_web(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    WEB.clear()
    STALLS.clear()
    monkeypatch.delenv("LOGO_SOURCE", raising=False)
    monkeypatch.delenv("LOGO_DEV_TOKEN", raising=False)
    # A store of this scenario's own, on disk: never the bucket.
    monkeypatch.setenv("LOGO_STORE", "dir")
    monkeypatch.setenv("LOGO_STORE_DIR", str(tmp_path / "logos"))
    with mock.patch.object(logos, "get", fake_get):
        yield
    WEB.clear()
    STALLS.clear()


# -- the web --------------------------------------------------------------


@given(parsers.parse('the company site "{host}" offers a {width:d}px icon'))
def _site_offers(host: str, width: int) -> None:
    page(host, f'<link rel="apple-touch-icon" href="/icon-{width}.png">')
    icon(f"https://{host}/icon-{width}.png", width)


@given(parsers.parse('the company site "{host}" offers a {small:d}px icon and a {large:d}px icon'))
def _site_offers_two(host: str, small: int, large: int) -> None:
    page(
        host,
        f'<link rel="icon" sizes="{small}x{small}" href="/icon-{small}.png">'
        f'<link rel="icon" sizes="{large}x{large}" href="/icon-{large}.png">',
    )
    icon(f"https://{host}/icon-{small}.png", small)
    icon(f"https://{host}/icon-{large}.png", large)


@given(parsers.parse('the company site "{host}" never answers for its page, and serves a {width:d}px favicon'))
def _site_stalls(host: str, width: int) -> None:
    STALLS.add(f"https://{host}/")
    icon(f"https://{host}/favicon.ico", width)


@given(parsers.parse('the company site "{host}" offers no icon'))
def _site_offers_none(host: str) -> None:
    page(host, "")


@given(parsers.parse('logo.dev offers a {width:d}px logo for "{host}"'))
def _logo_dev_has(host: str, width: int) -> None:
    icon(logos.LOGO_DEV_URL.format(host=host), width)


@given(parsers.parse('logos come from "{source}"'))
def _logos_come_from(monkeypatch: pytest.MonkeyPatch, source: str) -> None:
    monkeypatch.setenv("LOGO_SOURCE", source)
    monkeypatch.setenv("LOGO_DEV_TOKEN", "pk_test")


@given(parsers.parse('logos come from "{source}" without a key'))
def _logos_come_from_without_key(monkeypatch: pytest.MonkeyPatch, source: str) -> None:
    monkeypatch.setenv("LOGO_SOURCE", source)
    monkeypatch.delenv("LOGO_DEV_TOKEN", raising=False)


# -- the record and the clock ---------------------------------------------


async def _read(world: World, host: str) -> Optional[Any]:
    """A logo as the app keeps it, or None before the ask's workflow has
    brought it into being. The built-in 'eventually has' aborts on a
    state that does not exist yet rather than waiting for it, which is
    why these scenarios wait with their own step."""
    try:
        return await Logo.ref(host).get(world.context(USER))
    except Logo.GetAborted:
        return None


_CLAUSE = re.compile(r"`(?P<field>\w+)=(?P<value>[^`]*)`")
_JOIN = re.compile(r"\s*(?:,|and)\s*")


def _expected(clauses: str) -> dict[str, Any]:
    """`status="kept"` and `width=180`: each field and its JSON value."""
    expected: dict[str, Any] = {}
    rest = clauses
    while rest:
        match = _CLAUSE.match(rest)
        assert match, f"Not a clause: {rest!r}; write `field=value`, joined by 'and'"
        expected[match["field"]] = json.loads(match["value"])
        rest = rest[match.end() :]
        joined = _JOIN.match(rest)
        rest = rest[joined.end() :] if joined and rest.strip() else rest.strip()
    return expected


def _mismatch(logo: Any, expected: dict[str, Any]) -> Optional[str]:
    for field, value in expected.items():
        actual = getattr(logo, field)
        if actual != value:
            return f"`{field}` is {actual!r}, not {value!r}"
    return None


async def _checked_days_ago(world: World, host: str, days: int, status: str) -> None:
    """Ask for a logo with the clock set back, and wait for the answer,
    so it reads as checked that many days ago."""
    then_ = time.time() - days * DAY
    with mock.patch.object(logos, "now", lambda: then_):
        await Logos.ref(LOGOS_ID).ask(world.context(USER), hosts=[host])
        deadline = time.time() + 10
        while True:
            logo = await _read(world, host)
            if logo is not None and logo.status == status and not logo.fetching:
                return
            assert time.time() < deadline, f"{host} never became {status!r}: {logo}"
            await asyncio.sleep(0.1)


@then(parsers.re(r'the logo of "(?P<host>[^"]+)" eventually has (?P<clauses>.+) within (?P<seconds>\d+) seconds$'))
async def _logo_eventually_has(world: World, host: str, clauses: str, seconds: str) -> None:
    expected = _expected(clauses)
    deadline = time.time() + int(seconds)
    last = "it was never asked for"
    while True:
        logo = await _read(world, host)
        if logo is not None:
            problem = _mismatch(logo, expected)
            if problem is None:
                return
            last = problem
        assert time.time() < deadline, f"Waited {seconds}s for the logo of {host!r}, but {last}"
        await asyncio.sleep(0.1)


@given(parsers.parse('the logo of "{host}" was kept from "site" {days:d} days ago'))
async def _kept_days_ago(world: World, host: str, days: int) -> None:
    _site_offers(host, 180)
    await _checked_days_ago(world, host, days, "kept")


@given(parsers.parse('the logo of "{host}" was found missing {days:d} days ago'))
async def _missing_days_ago(world: World, host: str, days: int) -> None:
    _site_offers_none(host)
    await _checked_days_ago(world, host, days, "missing")


@given(parsers.parse('the logo of "{host}" was found missing by an older fetcher {days:d} days ago'))
async def _missing_by_older_fetcher(world: World, host: str, days: int) -> None:
    _site_offers_none(host)
    with mock.patch.object(logos, "SITE_FETCHER", logos.SITE_FETCHER - 1):
        await _checked_days_ago(world, host, days, "missing")


@then(parsers.parse('the store holds a {width:d}px "{content_type}" for "{host}"'))
async def _store_holds(width: int, content_type: str, host: str) -> None:
    kept = await logo_store.store().get(host)
    assert kept is not None, f"the store holds nothing for {host}"
    kept_type, image = kept
    assert kept_type == content_type, f"the store holds a {kept_type!r} for {host}, not {content_type!r}"
    # The PNG header's width, as `png()` above wrote it.
    (kept_width,) = struct.unpack(">I", image[16:20])
    assert kept_width == width, f"the store holds a {kept_width}px image for {host}, not {width}px"


@then(parsers.parse('the logo of "{host}" was last checked {days:d} days ago'))
async def _last_checked(world: World, host: str, days: int) -> None:
    # Long enough for a fetch that should not have started to have
    # finished if it had.
    await asyncio.sleep(2)
    logo = await _read(world, host)
    assert logo is not None, f"{host} was never asked for"
    expected = time.time() - days * DAY
    assert abs(logo.checked_at - expected) < 60 * 60, (
        f"{host} was last checked {(time.time() - logo.checked_at) / DAY:.2f} days ago, not {days}"
    )


@then(parsers.parse('the logo of "{host}" is eventually checked again within {seconds:d} seconds'))
async def _checked_again(world: World, host: str, seconds: int) -> None:
    deadline = time.time() + seconds
    while True:
        logo = await _read(world, host)
        if logo is not None and time.time() - logo.checked_at < 60 and not logo.fetching:
            return
        assert time.time() < deadline, f"{host} was not checked again: {logo}"
        await asyncio.sleep(0.1)
