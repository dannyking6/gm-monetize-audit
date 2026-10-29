import asyncio, json, time
from playwright.async_api import async_playwright

GAME_URL = "https://gamemonetize.com/gameshtml5uncached.php?gmdidco=1zhakvwsb80tili3c8p352rmrjt011w5/"
SITE_URL = "https://gamemonetize.com"

LOG = open('/tmp/gm_audit/traffic/pw_log.jsonl', 'a')


def log(o):
    LOG.write(json.dumps(o, ensure_ascii=False) + '\n')


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path='/usr/bin/chromium',
            headless=False,
            proxy={'server': 'http://127.0.0.1:8888'},
            ignore_https_errors=True,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--no-first-run', '--window-size=1280,800'])
        ctx = await browser.new_context(viewport={'width': 1280, 'height': 800}, locale='fr-FR',
                                        timezone_id='Europe/Paris',
                                        geolocation={'longitude': 2.35, 'latitude': 48.85},
                                        permissions=['geolocation'])
        page = await ctx.new_page()
        page.on('request', lambda r: log({'type': 'req', 'url': r.url, 'method': r.method, 'from': 'page'}))
        page.on('console', lambda m: log({'type': 'console', 'level': m.type, 'text': m.text[:2000]}))
        page.on('websocket', lambda w: log({'type': 'websocket', 'url': w.url}))

        log({'type': 'nav', 'url': GAME_URL, 'ts': 'start-game'})
        await page.goto(GAME_URL, wait_until='load', timeout=90000)
        t0 = time.time()
        while time.time() - t0 < 20:
            for sel in ['button', 'div[role=button]', 'a']:
                pass
            buttons = await page.query_selector_all('button')
            clicked = False
            for b in buttons:
                txt = (await b.inner_content() or '').lower()
                if 'play' in txt or 'jouer' in txt:
                    try:
                        await b.click(timeout=2000)
                        log({'type': 'click', 'button': txt})
                        clicked = True
                        break
                    except Exception:
                        pass
            if clicked:
                break
            await page.wait_for_timeout(2000)

        # clic sur le canvas pour jouer un peu
        await page.wait_for_timeout(3000)
        for sel in ['canvas', '#gameArea', 'body']:
            try:
                await page.click(sel, timeout=2000, position={'x': 640, 'y': 400})
                log({'type': 'click', 'sel': sel})
            except Exception:
                pass
        # quelques touches
        for k in ['ArrowRight', 'Space', 'ArrowRight', 'ArrowUp', 'Space', 'MouseLeft']:
            try:
                await page.keyboard.press(k)
                await page.wait_for_timeout(1000)
            except Exception:
                pass
        await page.wait_for_timeout(3000)

        # état stockage + cookies
        st = await page.evaluate("""() => ({
            cookies: document.cookie,
            location: location.href,
            gitop: localStorage.getItem('gd_debug'), gdtag: localStorage.getItem('gd_tag'),
            gdmidroll: localStorage.getItem('gd_midroll'),
            ls_keys: Object.keys(localStorage),
            ssid: sessionStorage.length,
            has_sdk: typeof window.sdk, has_gd: typeof window.GameDriver,
            ua: navigator.userAgent, lang: navigator.language,
            screen: [screen.width, screen.height, window.innerWidth, window.innerHeight],
        })""")
        log({'type': 'state_game', 'state': st})

        # déclencher les pubs (interstitiel + récompense)
        for label, fn in [('reward', 'window.showAdReward && window.showAdReward()'),
                          ('interstitial', 'window.showAdInterstitial && window.showAdInterstitial()')]:
            try:
                ok = await page.evaluate(fn)
                log({'type': 'ad_trigger', 'which': label, 'ok': ok})
            except Exception as e:
                log({'type': 'ad_trigger_err', 'which': label, 'err': str(e)})
            await page.wait_for_timeout(12000)

        st2 = await page.evaluate("""() => ({
            cookies: document.cookie, gdtag: localStorage.getItem('gd_tag'),
            ls_keys: Object.keys(localStorage) })""")
        log({'type': 'state_after_ads', 'state': st2})

        # récupérer game-driver.js via le navigateur (contourne le blocage curl)
        try:
            r = await page.request.get('https://gamemonetize.com/game-driver.js', timeout=30000)
            body = await r.text()
            open('/tmp/gm_audit/game-driver.js', 'w').write(body)
            log({'type': 'fetched', 'f': 'game-driver.js', 'code': r.status, 'size': len(body)})
        except Exception as e:
            log({'type': 'fetch_err', 'err': str(e)})

        # SITE PRINCIPAL gamemonetize.com
        log({'type': 'nav', 'url': SITE_URL, 'ts': 'start-site'})
        page2 = await ctx.new_page()
        await page2.goto(SITE_URL, wait_until='networkidle', timeout=90000)
        await page2.wait_for_timeout(8000)
        s2 = await page2.evaluate("""() => ({
            cookies: document.cookie, ls_keys: Object.keys(localStorage),
            ss_keys: Object.keys(sessionStorage), href: location.href })""")
        log({'type': 'state_site', 'state': s2})
        iframes = await page2.evaluate("""() => Array.from(document.querySelectorAll('iframe')).map(f=>f.src)""")
        log({'type': 'iframes_site', 'iframes': iframes})

        await browser.close()
        log({'type': 'done'})


asyncio.run(main())
