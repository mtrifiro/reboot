"""Unit tests of the company logos kit's safety checks (`logo_safety.py`).

Copied with it into the project's `tests/`; standard library only, so
`python3 -m unittest logo_safety_test` runs them from the directory
holding both, and `pytest` runs them with the rest of the suite.
"""

import asyncio
import struct
import unittest
from unittest import mock

import logo_safety as s

HEAD = '<html><head><link rel="apple-touch-icon" href="/icon.png"></head><body>'


def png(width: int) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct.pack(">II", width, width) + b"\x08\x06\x00\x00\x00"


def ico(*widths: int) -> bytes:
    entries = b"".join(bytes([w % 256]) + b"\x00" * 15 for w in widths)
    return b"\x00\x00\x01\x00" + struct.pack("<H", len(widths)) + entries


def chunks(body: bytes, size: int = 256):
    async def gen():
        for i in range(0, len(body), size):
            yield body[i : i + size]

    return gen()


def read(body: bytes, cap: int, keep_first: bool = False):
    return asyncio.run(s.read_capped(chunks(body), cap, keep_first))


class NormalizeHost(unittest.TestCase):
    def test_scheme_path_www_port_and_case_go(self) -> None:
        self.assertEqual(s.normalize_host("https://www.Acme.dev:8443/about?x=1#y"), "acme.dev")

    def test_a_user_part_goes(self) -> None:
        self.assertEqual(s.normalize_host("http://user:pw@acme.dev/"), "acme.dev")

    def test_a_trailing_dot_goes(self) -> None:
        self.assertEqual(s.normalize_host("acme.dev."), "acme.dev")

    def test_an_email_address_gives_its_domain(self) -> None:
        self.assertEqual(s.normalize_host("ann@acme.dev"), "acme.dev")


class PublicName(unittest.TestCase):
    def test_public_names(self) -> None:
        for host in ("acme.dev", "a.b.example.co.uk", "xn--bcher-kva.xn--p1ai"):
            self.assertTrue(s.public_name(host), host)

    def test_what_the_feature_refuses(self) -> None:
        for host in ("127.0.0.1", "localhost", "10.0.0.5", "metadata.google.internal", "northwind.test"):
            self.assertFalse(s.public_name(host), host)

    def test_more_that_is_not_a_public_name(self) -> None:
        for host in (
            "", "::1", "[::1]", "169.254.169.254", "printer.local", "nas.lan",
            "acme", "acme.d3v", "-acme.dev", "acme-.dev", "a..dev", "Acme.dev",
            "www.acme.dev", "acme.dev/x", "a" * 64 + ".dev", "under_score.dev",
        ):
            self.assertFalse(s.public_name(host), host)


class PublicAddress(unittest.TestCase):
    def test_public(self) -> None:
        for address in ("93.184.216.34", "2606:4700::6810:84e5"):
            self.assertTrue(s.public_address(address), address)

    def test_not_public(self) -> None:
        for address in (
            "127.0.0.1", "10.0.0.5", "172.16.0.1", "192.168.1.1", "169.254.169.254",
            "100.64.0.1", "0.0.0.0", "::1", "fe80::1%en0", "fc00::1", "::ffff:127.0.0.1", "nonsense",
        ):
            self.assertFalse(s.public_address(address), address)

    def resolve(self, *addresses: str) -> bool:
        infos = [(None, None, None, "", (a, 443)) for a in addresses]

        async def go() -> bool:
            loop = asyncio.get_running_loop()
            with mock.patch.object(loop, "getaddrinfo", mock.AsyncMock(return_value=infos)):
                return await s.resolves_publicly("acme.dev")

        return asyncio.run(go())

    def test_a_name_resolving_only_publicly(self) -> None:
        self.assertTrue(self.resolve("93.184.216.34", "2606:4700::6810:84e5"))

    def test_one_private_answer_among_public_ones_refuses(self) -> None:
        self.assertFalse(self.resolve("93.184.216.34", "10.0.0.5"))

    def test_no_answer_refuses(self) -> None:
        self.assertFalse(self.resolve())

    def test_a_failed_lookup_refuses(self) -> None:
        async def go() -> bool:
            loop = asyncio.get_running_loop()
            with mock.patch.object(loop, "getaddrinfo", mock.AsyncMock(side_effect=OSError("no such name"))):
                return await s.resolves_publicly("nowhere.dev")

        self.assertFalse(asyncio.run(go()))


class FetchableUrl(unittest.TestCase):
    def test_fetchable(self) -> None:
        for url in ("https://acme.dev/", "http://www.acme.dev/favicon.ico", "https://img.logo.dev/acme.dev?size=128"):
            self.assertTrue(s.fetchable_url(url), url)

    def test_not_fetchable(self) -> None:
        for url in (
            "file:///etc/passwd", "ftp://acme.dev/", "https://127.0.0.1/", "http://localhost:8080/",
            "http://169.254.169.254/latest/meta-data/", "https://[::1]/", "//acme.dev/", "https:///x",
            "http://metadata.google.internal/", "https://[not-an-address/",
        ):
            self.assertFalse(s.fetchable_url(url), url)


class ReadCapped(unittest.TestCase):
    """Ported from reboot-crm's `logo_fetch_test.py`."""

    def test_a_page_longer_than_the_cap_keeps_its_head(self) -> None:
        got = read(HEAD.encode() + b"x" * 5000, cap=1000, keep_first=True)
        assert got is not None
        self.assertEqual(len(got), 1000)
        self.assertEqual(s.declared_icons("https://big.dev/", got.decode()), ["https://big.dev/icon.png"])

    def test_an_image_longer_than_the_cap_is_refused(self) -> None:
        self.assertIsNone(read(b"\x89PNG" + b"x" * 5000, cap=1000))

    def test_a_body_within_the_cap_is_kept_whole(self) -> None:
        self.assertEqual(read(HEAD.encode(), cap=1000), HEAD.encode())

    def test_a_body_exactly_the_cap_is_kept(self) -> None:
        self.assertEqual(read(b"x" * 1000, cap=1000), b"x" * 1000)


class Sniff(unittest.TestCase):
    def test_png(self) -> None:
        self.assertEqual(s.sniff(png(180)), ("image/png", 180))

    def test_gif(self) -> None:
        self.assertEqual(s.sniff(b"GIF89a" + struct.pack("<HH", 64, 64)), ("image/gif", 64))

    def test_ico_takes_its_widest_entry_and_zero_means_256(self) -> None:
        self.assertEqual(s.sniff(ico(16, 48)), ("image/x-icon", 48))
        self.assertEqual(s.sniff(ico(32, 256)), ("image/x-icon", 256))

    def test_an_empty_ico_is_none(self) -> None:
        self.assertIsNone(s.sniff(b"\x00\x00\x01\x00\x00\x00"))

    def test_jpeg_reads_its_frame(self) -> None:
        app0 = b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00" + b"\x00" * 9
        sof0 = b"\xff\xc0" + struct.pack(">HBHH", 17, 8, 120, 200) + b"\x00" * 10
        self.assertEqual(s.sniff(b"\xff\xd8" + app0 + sof0), ("image/jpeg", 200))

    def test_webp_vp8x(self) -> None:
        data = b"RIFF" + b"\x00" * 4 + b"WEBP" + b"VP8X" + b"\x00" * 8 + (95).to_bytes(3, "little") + b"\x00" * 3
        self.assertEqual(s.sniff(data), ("image/webp", 96))

    def test_svg_is_never_a_logo(self) -> None:
        svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="512"><script>alert(1)</script></svg>'
        self.assertIsNone(s.sniff(svg))
        self.assertIsNone(s.sniff(b'<?xml version="1.0"?>' + svg))

    def test_html_and_truncation_are_none(self) -> None:
        self.assertIsNone(s.sniff(b"<html></html>"))
        self.assertIsNone(s.sniff(png(180)[:12]))
        self.assertIsNone(s.sniff(b""))


class Keepable(unittest.TestCase):
    def test_wide_enough(self) -> None:
        self.assertEqual(s.keepable(png(32)), ("image/png", 32))

    def test_narrower_than_32px_is_none(self) -> None:
        self.assertIsNone(s.keepable(png(16)))

    def test_over_the_size_cap_is_none(self) -> None:
        self.assertIsNone(s.keepable(png(180) + b"\x00" * s.MAX_BYTES))

    def test_svg_is_none(self) -> None:
        self.assertIsNone(s.keepable(b"<svg width='512'></svg>"))


class DeclaredIcons(unittest.TestCase):
    def test_largest_first_and_absolute(self) -> None:
        html = (
            '<head><link rel="icon" sizes="32x32" href="/i32.png">'
            '<link rel="icon" sizes="192x192" href="https://cdn.acme.dev/i192.png">'
            '<link rel="apple-touch-icon" href="touch.png"></head>'
        )
        self.assertEqual(
            s.declared_icons("https://acme.dev/en/", html),
            ["https://cdn.acme.dev/i192.png", "https://acme.dev/en/touch.png", "https://acme.dev/i32.png"],
        )

    def test_svg_and_data_urls_are_skipped(self) -> None:
        html = (
            '<link rel="icon" href="/logo.svg">'
            '<link rel="icon" href="/logo.SVG?v=2">'
            '<link rel="icon" type="image/svg+xml" href="/logo">'
            '<link rel="icon" href="data:image/png;base64,AAAA">'
            '<link rel="icon" href="/ok.png">'
        )
        self.assertEqual(s.declared_icons("https://acme.dev/", html), ["https://acme.dev/ok.png"])

    def test_links_in_the_body_are_not_read(self) -> None:
        html = '<head></head><body><link rel="icon" href="/late.png"></body>'
        self.assertEqual(s.declared_icons("https://acme.dev/", html), [])

    def test_a_stylesheet_is_not_an_icon(self) -> None:
        html = '<link rel="stylesheet" href="/a.css"><link rel="shortcut icon" href="/f.ico">'
        self.assertEqual(s.declared_icons("https://acme.dev/", html), ["https://acme.dev/f.ico"])

    def test_a_page_that_will_not_parse_declares_nothing(self) -> None:
        self.assertEqual(s.declared_icons("https://acme.dev/", "<<<<"), [])


class Headers(unittest.TestCase):
    def test_a_served_logo_cannot_run_anything(self) -> None:
        self.assertEqual(s.SERVE_HEADERS["X-Content-Type-Options"], "nosniff")
        self.assertIn("sandbox", s.SERVE_HEADERS["Content-Security-Policy"])
        self.assertEqual(s.NOT_KEPT_HEADERS["Cache-Control"], "no-store")


if __name__ == "__main__":
    unittest.main()
