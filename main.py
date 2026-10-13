import asyncio
from urllib.parse import parse_qs, urlparse

import aiohttp
import decky

CEF = "http://127.0.0.1:8080"  # Steam's CEF devtools, enabled by Decky
ARM_SECONDS = 300

# pathofexile.com login page: click the same-site "sign in through Steam" link/form.
# ponytail: heuristic match on "steam" in a same-host href/action (page is behind Cloudflare,
# markup not inspectable from here); swap for an exact selector once seen on-device.
POE_STEAM_JS = """(() => {
  const hit = s => { try { const u = new URL(s, location.href);
    return u.host === location.host && /steam/i.test(u.pathname + u.search); } catch { return false; } };
  const a = [...document.querySelectorAll('a[href]')].find(e => hit(e.getAttribute('href')));
  if (a) { a.click(); return true; }
  const f = [...document.querySelectorAll('form[action]')].find(e => hit(e.getAttribute('action')));
  if (f) { f.requestSubmit(); return true; }
  return false;
})()"""

# Steam OpenID confirm page (only shown when the browser already has a Steam session).
STEAM_SIGNIN_JS = """(() => {
  const b = document.querySelector('#imageLogin, #openidForm [type=submit]');
  if (b) { b.click(); return true; }
  return false;
})()"""

SCRIPTS = {"poe": POE_STEAM_JS, "steam": STEAM_SIGNIN_JS}


def _is_poe(host):
    return host == "pathofexile.com" or host.endswith(".pathofexile.com")


def pick_step(url):
    u = urlparse(url)
    host = u.hostname or ""
    if _is_poe(host) and u.path.rstrip("/") == "/login":
        return "poe"
    # Never auto-approve OpenID for anything but GGG: that would hand our Steam identity to any site.
    if host == "steamcommunity.com" and u.path.startswith("/openid/login"):
        return_to = parse_qs(u.query).get("openid.return_to", [""])[0]
        if _is_poe(urlparse(return_to).hostname or ""):
            return "steam"
    return None


async def _eval(session, tab_id, js):
    async with session.ws_connect(f"ws://127.0.0.1:8080/devtools/page/{tab_id}") as ws:
        await ws.send_json({"id": 1, "method": "Runtime.evaluate",
                            "params": {"expression": js, "returnByValue": True}})
        async for msg in ws:
            data = msg.json()
            if data.get("id") == 1:
                return data.get("result", {}).get("result", {}).get("value")


async def _watch():
    loop = asyncio.get_running_loop()
    end = loop.time() + ARM_SECONDS
    done = set()  # each step fires at most once per arm, so a failing login can't loop
    async with aiohttp.ClientSession() as session:
        while loop.time() < end and len(done) < len(SCRIPTS):
            try:
                async with session.get(f"{CEF}/json", timeout=aiohttp.ClientTimeout(total=3)) as r:
                    tabs = await r.json()
                for tab in tabs:
                    step = pick_step(tab.get("url", ""))
                    if step and step not in done and await asyncio.wait_for(
                            _eval(session, tab["id"], SCRIPTS[step]), 5):
                        done.add(step)
                        decky.logger.info(f"auto-login: clicked {step}")
            except Exception as e:
                decky.logger.warning(f"auto-login: {e!r}")
            await asyncio.sleep(1)


class Plugin:
    task = None

    async def arm_auto_login(self):
        if self.task:
            self.task.cancel()
        self.task = asyncio.get_running_loop().create_task(_watch())

    async def _unload(self):
        if self.task:
            self.task.cancel()
