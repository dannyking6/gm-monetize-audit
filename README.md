# GameMonetize — Audit de traçabilité / vie privée

Analyse du SDK, de la plateforme et du flux publicitaire de GameMonetize
pour un jeu intégré via `https://uncached.gamemonetize.com/1zhakvwsb80tili3c8p352rmrjt011w5/`.

Le rapport PDF complet est : `GameMonetize_audit_donnees.pdf`.

## Ce qui a été fait

1. **Analyse statique du SDK** (`sdk.js` / `game-driver.js`) :
   - désomification complète (`deobfuscate.js`) → `sdk.readable.js`, `sdk.beauty.js`
   - extraction des chaînes de caractères → `strings.json`
   - identification des endpoints de télémétrie (`opphbh.php`, `event.php`),
     de GA4 (`G-8SK3BC00X8`, `ga.js`), et du tag publicitaire Google IMA/ADX.

2. **Analyse dynamique** :
   - jeu exécuté sous Xvfb + Chromium (Selenium) derrière mitmproxy (`run_campaign.sh`).
   - toutes les requêtes interceptées dans `traffic/requests.jsonl` (> 1000 requêtes),
     avec logs Selenium (`traffic/pw_log.jsonl`).

3. **Flux publicitaire** :
   - tag `pubads.g.doubleclick.net/gampad/ads` (Google ADX) pour les prérolls.
   - créative confect.io, qui elle-même appelle `api.ipify.org` pour récupérer
     l'adresse IP publique du joueur.
   - données envoyées à Google : `uach`, `sid`, `hl`, `pvsid`, `scor`, horodatages,
     URL exacte de la page, `npa=0`, etc.

4. **Rapport PDF** : `build_pdf.py` → `GameMonetize_audit_donnees.pdf`.

## Fichiers principaux

- `sdk.js` — SDK original (obfusqué).
- `sdk.readable.js` / `sdk.beauty.js` — SDK désomifié.
- `game-driver.js` / `gd_real.js` — bridge GameDriver récupéré depuis le jeu.
- `game_page.html` — page d'intégration du jeu.
- `ga.js` — Google Analytics 4 tel que chargé par le SDK.
- `build_pdf.py` — génération du rapport PDF.
- `run_campaign.sh` — lancement mitm + Selenium + Xvfb.
- `traffic/requests.jsonl` / `traffic/pw_log.jsonl` — journaux de requêtes.
- `shots/*.png` — captures d'écran (jeu, page d'accueil, pub).

## Dépendances

- Python : reportlab (pour le PDF), selenium, mitmproxy-related tooling.
- Node : pour la désomification du SDK (js-beautify optionnel).
- Xvfb, Chromium (Selenium), mitmproxy / mitmdump.

## Auteur

Audit réalisé par Codebuff (Buffy) sur Freebuff.

Generated with Codebuff 🤖
Co-Authored-By: Codebuff <noreply@codebuff.com>
