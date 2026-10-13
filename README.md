# poe2filter for Decky

Quick Access button that opens [poe2filter.com](https://poe2filter.com) in the Steam browser.
Pressing it also turns on auto-login for 5 minutes: the backend watches the browser through
CEF devtools and clicks "Sign in through Steam" on pathofexile.com and "Sign In" on Steam's
OpenID page, reusing the Steam session the Deck already has. Nobody types a password.
You still tap **Log in** on poe2filter and **Authorize** on GGG's consent page yourself, plus
Cloudflare's "verify you are human" check on pathofexile.com if it shows up.

## Build & install

```sh
pnpm install && pnpm build
ssh deck@steamdeck mkdir -p /tmp/poe2filter
scp -r dist main.py plugin.json package.json deck@steamdeck:/tmp/poe2filter/
ssh -t deck@steamdeck 'sudo rm -rf ~/homebrew/plugins/poe2filter && sudo mv /tmp/poe2filter ~/homebrew/plugins/ && sudo systemctl restart plugin_loader'
```

Check: `python3 test_main.py`. Logs: `~/homebrew/logs/poe2filter/` on the Deck.
