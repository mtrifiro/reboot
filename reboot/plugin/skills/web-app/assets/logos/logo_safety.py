"""The company logos kit's safety checks (web-app/references/company-logos.md).

Copied into the project's `backend/src/` as it stands and used for every
logo fetch and every logo served. These are the parts a build must not
rewrite: each one stops a company's domain, which a user typed, from
aiming the app at its own machine or network, or from getting script
served from the app's own address.

- `normalize_host`: the key a logo is kept under. The web app's
  `logoHost` does the same before it asks.
- `public_name`: a host written as a public DNS name, checked before an
  ask is accepted and before every connection.
- `public_address` / `resolves_publicly`: every address the name
  resolves to is a public one, checked before every connection.
- `fetchable_url`: one hop of a fetch, its scheme and its host; check
  each redirect's target with it again, never follow one unchecked.
- `read_capped`: a body read only up to a cap.
- `sniff` / `keepable`: what an image is and how wide, by its bytes;
  SVG is never a logo here.
- `declared_icons`: the icons a home page's `<head>` declares.
- `SERVE_HEADERS` / `NOT_KEPT_HEADERS`: the headers `/__/logo` answers
  with.

Standard library only, no Reboot, and nothing touches the network on
import: only `resolves_publicly`, when awaited, looks a name up. The
check and the connection are separate lookups, so a name that changes
its answer between the two could still slip through; that is the
accepted limit of doing this without pinning addresses.
"""

import asyncio
import ipaddress
import re
import socket
import struct
from html.parser import HTMLParser
from typing import AsyncIterable, Optional
from urllib.parse import urljoin, urlsplit

DAY = 24 * 60 * 60

# Smaller than this is treated as none: at the sizes the app draws a
# logo, the initials read better than a 16px icon blown up to a blur.
MIN_WIDTH = 32
# Anything larger is not an icon, and is not worth the bytes.
MAX_BYTES = 512 * 1024
# The home page is read only as far as its declared icons.
MAX_PAGE_BYTES = 1024 * 1024
MAX_REDIRECTS = 4

# The top levels nothing on the public internet is named under, and the
# few more that private networks use by convention.
PRIVATE_TLDS = frozenset(
    {
        "test", "example", "invalid", "localhost", "local", "onion",
        "internal", "home", "lan", "corp", "intranet", "arpa",
    }
)
_LABEL = re.compile(r"^(?!-)[a-z0-9-]{1,63}(?<!-)$")

# What a browser sends. Sites behind bot protection stall a request that
# names itself until it times out; a plain browser's headers get the
# same favicon the site shows in a tab.
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept": "text/html,image/avif,image/webp,image/png,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# A kept logo, served from the app's own address, is held to being an
# image: no sniffing it into anything else, nothing it could load or
# run. Served a day at a time; the app refetches every thirty days.
SERVE_HEADERS = {
    "Cache-Control": "public, max-age=86400",
    "X-Content-Type-Options": "nosniff",
    "Content-Security-Policy": "default-src 'none'; sandbox",
    "Cross-Origin-Resource-Policy": "cross-origin",
}
# "None kept yet" (a 404) is never cached: the web app asks for the
# logo and looks again.
NOT_KEPT_HEADERS = {"Cache-Control": "no-store"}


def normalize_host(domain: str) -> str:
    """The key a company's logo is kept under: its domain without a
    scheme, a path, a user, a port or a leading `www.`, in lower case."""
    host = domain.strip().lower()
    host = re.sub(r"^[a-z][a-z0-9+.-]*://", "", host)
    host = re.split(r"[/?#]", host, maxsplit=1)[0]
    host = host.rsplit("@", 1)[-1].split(":", 1)[0].rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    return host


def public_name(host: str) -> bool:
    """Whether a host is written as a public DNS name: already
    normalized, dotted labels, a top level that names somewhere on the
    internet, and not an address."""
    if not host or len(host) > 253 or host != normalize_host(host):
        return False
    try:
        ipaddress.ip_address(host)
        return False
    except ValueError:
        pass
    labels = host.split(".")
    if len(labels) < 2 or not all(_LABEL.match(label) for label in labels):
        return False
    tld = labels[-1]
    if tld in PRIVATE_TLDS:
        return False
    # A top level is letters, or an internationalized one in punycode.
    return (tld.isalpha() and len(tld) >= 2) or tld.startswith("xn--")


def public_address(address: str) -> bool:
    """Whether an address (as `getaddrinfo` gives it, perhaps with an
    IPv6 zone) is a public one: not loopback, private, link-local (the
    cloud metadata address), reserved or otherwise not global."""
    try:
        return ipaddress.ip_address(address.split("%", 1)[0]).is_global
    except ValueError:
        return False


async def resolves_publicly(host: str) -> bool:
    """Whether the name resolves, and every address it resolves to is a
    public one."""
    try:
        infos = await asyncio.get_running_loop().getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except OSError:
        return False
    addresses = {str(info[4][0]) for info in infos}
    return bool(addresses) and all(public_address(a) for a in addresses)


def fetchable_url(url: str) -> bool:
    """Whether one hop of a fetch may be made: http or https, to a public
    name. Check every redirect's target (`urljoin` of the hop and its
    `Location`) with this, then `resolves_publicly`, before connecting."""
    try:
        parts = urlsplit(url)
        hostname = parts.hostname
    except ValueError:
        return False
    if parts.scheme not in ("http", "https") or not hostname:
        return False
    return public_name(normalize_host(hostname))


async def read_capped(chunks: AsyncIterable[bytes], cap: int, keep_first: bool = False) -> Optional[bytes]:
    """A body read from its chunks (`response.aiter_bytes()`), never
    more than `cap` bytes of it. A longer body is None, unless
    `keep_first`: then its first `cap` bytes. A page is read that way,
    since the icons it declares are in its `<head>`; an image cut short
    is no image, so it never is."""
    body = bytearray()
    async for chunk in chunks:
        body.extend(chunk)
        if len(body) > cap:
            if not keep_first:
                return None
            del body[cap:]
            break
    return bytes(body)


def sniff(data: bytes) -> Optional[tuple[str, int]]:
    """What an image is, by its first bytes, and how wide: PNG, GIF,
    JPEG, ICO or WebP. Anything else, SVG included, is not a logo: an
    SVG can carry script, and the app serves these from its own
    address. Never trust the content type a site sends instead."""
    try:
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            return "image/png", struct.unpack(">I", data[16:20])[0]
        if data[:6] in (b"GIF87a", b"GIF89a"):
            return "image/gif", struct.unpack("<H", data[6:8])[0]
        if data[:4] == b"\x00\x00\x01\x00":
            count = struct.unpack("<H", data[4:6])[0]
            if count == 0:
                return None
            # Each directory entry is 16 bytes; a width byte of 0 means 256.
            widths = [data[6 + 16 * i] or 256 for i in range(count)]
            return "image/x-icon", max(widths)
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            chunk = data[12:16]
            if chunk == b"VP8X":
                return "image/webp", 1 + int.from_bytes(data[24:27], "little")
            if chunk == b"VP8L":
                bits = int.from_bytes(data[21:25], "little")
                return "image/webp", 1 + (bits & 0x3FFF)
            if chunk == b"VP8 ":
                return "image/webp", struct.unpack("<H", data[26:28])[0] & 0x3FFF
            return None
        if data[:2] == b"\xff\xd8":
            i = 2
            while i + 9 < len(data):
                if data[i] != 0xFF:
                    return None
                marker = data[i + 1]
                length = struct.unpack(">H", data[i + 2 : i + 4])[0]
                # A start-of-frame marker carries the height, then the width.
                if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                    return "image/jpeg", struct.unpack(">H", data[i + 7 : i + 9])[0]
                i += 2 + length
            return None
    except (struct.error, IndexError):
        return None
    return None


def keepable(data: bytes) -> Optional[tuple[str, int]]:
    """The content type and width of an image worth keeping as a logo:
    one `sniff` knows, at least `MIN_WIDTH` wide, at most `MAX_BYTES`.
    None for anything else, which counts as no logo."""
    if len(data) > MAX_BYTES:
        return None
    found = sniff(data)
    if found is None or found[1] < MIN_WIDTH:
        return None
    return found


class _DeclaredIcons(HTMLParser):
    """The icons a page's `<link>` tags declare, with the size each says
    it is (0 when it does not say), until the page's body begins."""

    def __init__(self) -> None:
        super().__init__()
        self.icons: list[tuple[int, str]] = []
        self.done = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if self.done:
            return
        if tag == "body":
            self.done = True
            return
        if tag != "link":
            return
        a = {k: (v or "") for k, v in attrs}
        rel = a.get("rel", "").lower().split()
        href = a.get("href", "").strip()
        # No data: URLs and no SVG, by name or by declared type.
        if not href or href.startswith("data:") or href.lower().split("?", 1)[0].endswith(".svg"):
            return
        if "svg" in a.get("type", "").lower():
            return
        declared = 0
        for size in a.get("sizes", "").lower().split():
            w = size.split("x", 1)[0]
            if w.isdigit():
                declared = max(declared, int(w))
        if "apple-touch-icon" in rel or "apple-touch-icon-precomposed" in rel:
            # Undeclared, an apple-touch-icon is the 180px Apple asks for.
            self.icons.append((declared or 180, href))
        elif "icon" in rel:
            self.icons.append((declared, href))


def declared_icons(page_url: str, html: str) -> list[str]:
    """The icons a page declares, largest first, as absolute URLs. Each
    is still fetched only through `fetchable_url` and the rest."""
    parser = _DeclaredIcons()
    try:
        parser.feed(html)
    except Exception:  # A page that will not parse declares nothing.
        pass
    ordered = sorted(enumerate(parser.icons), key=lambda item: (-item[1][0], item[0]))
    urls: list[str] = []
    for _, (_, href) in ordered:
        url = urljoin(page_url, href)
        if url not in urls:
            urls.append(url)
    return urls
