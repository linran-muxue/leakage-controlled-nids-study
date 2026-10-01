"""Pick a healthy outbound node in Clash Verge, through its control pipe.

The 23.8 GB Gotham download died halfway because the selected proxy node went
down: every foreign TLS handshake started failing while the proxy itself kept
accepting connections, so the failure looked like "TLS handshake failed" rather
than "no network".  Clash Verge exposes the mihomo API on a Windows named pipe
(``\\.\pipe\verge-mihomo``) instead of a TCP port, so this helper speaks HTTP/1.1
over that pipe: it lists the selector groups, delay-tests the member nodes and
switches the group to the fastest one that responds.

Usage:  python scripts/proxy_node_switch_v1.py [--group NAME] [--dry-run]
"""
from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wintypes
import json
import sys
import time
import urllib.parse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PIPE = r"\\.\pipe\verge-mihomo"
SECRET = "set-your-secret"
DELAY_URL = "https://www.gstatic.com/generate_204"

_k32 = ctypes.WinDLL("kernel32", use_last_error=True)
_k32.CreateFileW.restype = ctypes.c_void_p
GENERIC_READ, GENERIC_WRITE, OPEN_EXISTING = 0x80000000, 0x40000000, 3
INVALID = ctypes.c_void_p(-1).value


class Pipe:
    def _open(self) -> int:
        self.handle = _k32.CreateFileW(PIPE, GENERIC_READ | GENERIC_WRITE, 0, None,
                                       OPEN_EXISTING, 0, None)
        if self.handle in (INVALID, None):
            raise SystemExit(f"cannot open {PIPE}: error {ctypes.get_last_error()}")
        return self.handle

    def request(self, method: str, path: str, body: dict | None = None,
                timeout: float = 20.0) -> dict:
        # the pipe speaks HTTP/1.1 with Connection: close, so every request needs
        # a fresh connection; reusing one handle silently returned a truncated
        # response for /proxies (a megabyte-scale payload)
        handle = self._open()
        payload = json.dumps(body).encode() if body is not None else b""
        head = (f"{method} {path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n"
                f"Authorization: Bearer {SECRET}\r\n")
        if payload:
            head += "Content-Type: application/json\r\n"
        head += f"Content-Length: {len(payload)}\r\n\r\n"
        written = wintypes.DWORD(0)
        blob = head.encode() + payload
        if not _k32.WriteFile(ctypes.c_void_p(handle), blob, len(blob),
                              ctypes.byref(written), None):
            raise SystemExit(f"pipe write failed: {ctypes.get_last_error()}")
        buffer = ctypes.create_string_buffer(1 << 20)
        raw = b""
        deadline = time.time() + timeout
        while time.time() < deadline:
            read = wintypes.DWORD(0)
            if not _k32.ReadFile(ctypes.c_void_p(handle), buffer, len(buffer),
                                 ctypes.byref(read), None) or read.value == 0:
                break
            raw += buffer.raw[:read.value]
            head_, _, rest = raw.partition(b"\r\n\r\n")
            length = 0
            for line in head_.split(b"\r\n"):
                if line.lower().startswith(b"content-length:"):
                    length = int(line.split(b":", 1)[1])
            if length and len(rest) >= length:
                break
        _k32.CloseHandle(ctypes.c_void_p(handle))
        header, _, payload_bytes = raw.partition(b"\r\n\r\n")
        status = int(header.split(b"\r\n")[0].split()[1]) if header else 0
        if b"chunked" in header.lower():
            payload_bytes = dechunk(payload_bytes)
        try:
            parsed = json.loads(payload_bytes.decode("utf-8", "replace") or "{}")
        except json.JSONDecodeError:
            parsed = {"raw": payload_bytes.decode("utf-8", "replace")}
        if status >= 400:
            raise SystemExit(f"{method} {path} -> {status}: {parsed}")
        return parsed


def dechunk(body: bytes) -> bytes:
    """Undo HTTP/1.1 chunked transfer encoding; mihomo always answers chunked."""
    out = b""
    while True:
        line, _, rest = body.partition(b"\r\n")
        if not line:
            return out
        try:
            size = int(line.split(b";", 1)[0], 16)
        except ValueError:
            return out + line + b"\r\n" + rest
        if size == 0:
            return out
        out += rest[:size]
        body = rest[size + 2:]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", default=None, help="selector group to switch")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--timeout-ms", type=int, default=3000)
    args = ap.parse_args()

    pipe = Pipe()
    proxies = pipe.request("GET", "/proxies")["proxies"]
    selectors = {name: node for name, node in proxies.items()
                 if node.get("type") in ("Selector", "URLTest", "Fallback")}
    print(f"groups: {', '.join(sorted(selectors))}")
    target = args.group or min(selectors, key=lambda name: len(name))
    node = selectors[target]
    members = [m for m in node["all"] if m in proxies]
    print(f"group {target!r} has {len(members)} members, current {node['now']!r}")

    best: tuple[float, str] | None = None
    for member in members:
        try:
            result = pipe.request(
                "GET", f"/proxies/{member}/delay"
                f"?timeout={args.timeout_ms}&url={urllib.parse.quote(DELAY_URL, safe='')}",
                timeout=12)
        except SystemExit:
            continue
        delay = result.get("delay")
        if delay and delay > 0 and (best is None or delay < best[0]):
            best = (float(delay), member)
        print(f"  {member:<40} {delay if delay else 'timeout'}")
    if best is None:
        raise SystemExit("no node in the group responded")
    print(f"fastest: {best[1]!r} at {best[0]:.0f} ms")
    if args.dry_run:
        return
    if best[1] != node["now"]:
        pipe.request("PUT", f"/proxies/{target}", {"name": best[1]})
        print(f"switched {target!r} -> {best[1]!r}")
    else:
        print("current node is already the fastest responder")
    print("PROXY_NODE_OK")


if __name__ == "__main__":
    main()
