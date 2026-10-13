import sys
import types
from urllib.parse import quote

sys.modules.setdefault("decky", types.ModuleType("decky"))
sys.modules.setdefault("aiohttp", types.ModuleType("aiohttp"))
from main import pick_step  # noqa: E402


def openid(return_to):
    return f"https://steamcommunity.com/openid/login?openid.mode=checkid_setup&openid.return_to={quote(return_to, safe='')}"


assert pick_step("https://www.pathofexile.com/login") == "poe"
assert pick_step("https://www.pathofexile.com/login/") == "poe"
assert pick_step("https://www.pathofexile.com/login/steam?openid.mode=id_res") is None
assert pick_step("https://www.pathofexile.com/oauth/authorize?client_id=poe2filter") is None
assert pick_step("https://evilpathofexile.com/login") is None
assert pick_step(openid("https://www.pathofexile.com/login/steam")) == "steam"
assert pick_step(openid("https://evil.example/cb?x=pathofexile.com")) is None
assert pick_step(openid("https://pathofexile.com.evil.example/")) is None
assert pick_step("https://steamcommunity.com.evil.example/openid/login") is None
assert pick_step("https://poe2filter.com/") is None
print("ok")
