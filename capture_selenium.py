import json, time, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

LOG = open('/tmp/gm_audit/traffic/pw_log.jsonl', 'a')
def log(o): LOG.write(json.dumps(o, ensure_ascii=False, default=str) + '\n')

GAME_URL = "https://gamemonetize.com/gameshtml5uncached.php?gmdidco=1zhakvwsb80tili3c8p352rmrjt011w5/"
SITE_URL = "https://gamemonetize.com"

opts = Options()
opts.binary_location = '/usr/bin/chromium'
for a in ['--no-sandbox', '--disable-dev-shm-usage', '--window-size=1280,800', '--no-first-run',
          '--proxy-server=http://127.0.0.1:8888', '--ignore-certificate-errors', '--lang=fr-FR']:
    opts.add_argument(a)
prefs = {'intl.accept_languages': 'fr-FR,fr,en'}
opts.add_experimental_option('prefs', prefs)
opts.add_experimental_option('excludeSwitches', ['enable-automation'])

driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=opts)
driver.set_window_size(1280, 800)

def state():
    return driver.execute_script("""return {
        cookies: document.cookie,
        href: location.href,
        ls_keys: Object.keys(localStorage),
        gd_debug: localStorage.getItem('gd_debug'),
        gd_tag: localStorage.getItem('gd_tag'),
        gd_midroll: localStorage.getItem('gd_midroll'),
        has_sdk: typeof window.sdk, has_gd: typeof window.GameDriver,
        ua: navigator.userAgent, lang: navigator.language,
        screens: [screen.width, screen.height, window.innerWidth, window.innerHeight],
    }""")

def dump_cookies(tag):
    cookies = driver.get_cookies()
    log({'type': 'cookies', 'tag': tag, 'cookies': cookies})

# ---- JEU ----
log({'type': 'nav', 'url': GAME_URL})
driver.get(GAME_URL)
time.sleep(8)
# splash / bouton Play
locked = False
for _ in range(12):
    try:
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        for b in buttons:
            try:
                txt = (b.text or '').lower()
                if 'play' in txt:
                    b.click()
                    log({'type': 'click', 'button': txt})
                    locked = True
                    break
            except Exception: pass
        if locked: break
    except Exception: pass
    time.sleep(2)
if not locked:
    log({'type': 'no_play_button'})
time.sleep(4)

# utiliser un peu le jeu : clics canvas + touches
sel_common = None
for _ in range(6):
    try:
        driver.execute_script("var d=document.activeElement||document.body; d.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',code:'ArrowRight',bubbles:true}))"
                              )
        driver.find_elements(By.ID, 'canvas') or None
    except Exception: pass
    try:
        canvas = driver.find_element(By.TAG_NAME, 'canvas')
        from selenium.webdriver.common.action_chains import ActionChains
        ActionChains(driver).move_to_element_with_offset(canvas, 300, 200).click().perform()
        log({'type': 'click', 'sel': 'canvas'})
    except Exception:
        pass
    driver.execute_script("document.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',code:'ArrowRight',bubbles:true})); document.dispatchEvent(new KeyboardEvent('keyup',{key:'ArrowRight',bubbles:true}))")
    time.sleep(1)
time.sleep(4)

st = state()
log({'type': 'state_game', 'state': st})
dump_cookies('game_pre_ads')
driver.save_screenshot('/tmp/gm_audit/shots/game_play.png')

# ---- PUBS ----
for label, expr in [('reward', "window.showAdReward && window.showAdReward()"),
                    ('interstitial', "window.showAdInterstitial && window.showAdInterstitial()")]:
    try:
        r = driver.execute_script(f"return !!({expr})")
        log({'type': 'ad_trigger', 'which': label, 'result': r})
    except Exception as e:
        log({'type': 'ad_trigger_err', 'which': label, 'err': str(e)})
    time.sleep(15)

st2 = state()
log({'type': 'state_after_ads', 'state': st2})
dump_cookies('game_post_ads')
driver.save_screenshot('/tmp/gm_audit/shots/game_ads.png')

# récupérer game-driver.js depuis le contexte du navigateur
try:
    body = driver.execute_script("""
        return fetch('https://gamemonetize.com/game-driver.js').then(r=>r.text())
    """)
    if not isinstance(body, str): body = str(body)
    open('/tmp/gm_audit/game-driver.js', 'w').write(body)
    log({'type': 'fetched', 'f': 'game-driver.js', 'size': len(body)})
except Exception as e:
    log({'type': 'fetch_err', 'err': str(e)})

# ---- SITE PRINCIPAL ----
log({'type': 'nav', 'url': SITE_URL})
try:
    driver.execute_script("window.open('about:blank','_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(SITE_URL)
    time.sleep(12)
    s2 = driver.execute_script("""return {
        cookies: document.cookie,
        ls_keys: Object.keys(localStorage),
        ss_keys: Object.keys(sessionStorage) }""")
    log({'type': 'state_site', 'state': s2})
    ifr = driver.execute_script("return Array.from(document.querySelectorAll('iframe')).map(f=>f.src)")
    log({'type': 'iframes_site', 'iframes': ifr})
    dump_cookies('site_home')
    driver.save_screenshot('/tmp/gm_audit/shots/site_home.png')

    # page confidentialité
    try:
        links = driver.find_elements(By.TAG_NAME, 'a')
        for l in links:
            if 'privacy' in (l.get_attribute('href') or ''):
                driver.get(l.get_attribute('href'))
                time.sleep(6)
                txt = driver.execute_script("return document.body.innerText.substr(0,5000)")
                log({'type': 'privacy_page', 'url': driver.current_url, 'text': txt})
                break
    except Exception as e:
        log({'type': 'privacy_err', 'err': str(e)})
except Exception as e:
    log({'type': 'site_err', 'err': str(e)})

driver.quit()
log({'type': 'done'})
