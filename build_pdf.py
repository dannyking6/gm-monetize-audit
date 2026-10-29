# -*- coding: utf-8 -*-
"""Rapport d'audit de collecte de données — SDK et plateforme GameMonetize (PDF)."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image)

ACCENT = '#7a0c2e'
ACCENT2 = '#f0435a'


def build_pdf(dest, screenshots):
    doc = SimpleDocTemplate(
        dest, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
        topMargin=1.8*cm, bottomMargin=1.8*cm,
        title="Audit de la collecte de données — GameMonetize",
        author="Étude indépendante de la vie privée")
    st = getSampleStyleSheet()
    h1 = ParagraphStyle('H1', parent=st['Heading1'], fontSize=16, spaceAfter=8,
                        spaceBefore=10, textColor=colors.HexColor(ACCENT))
    h2 = ParagraphStyle('H2', parent=st['Heading2'], fontSize=13, spaceAfter=5,
                        spaceBefore=6, textColor=colors.HexColor(ACCENT2))
    body = ParagraphStyle('Body', parent=st['BodyText'], fontSize=9.5, leading=13)
    code = ParagraphStyle('Code', parent=st['Code'], fontSize=7.5, leading=9.5,
                          backColor=colors.HexColor('#f3f3f3'), borderPadding=3,
                          leftIndent=4, rightIndent=4)
    disc = ParagraphStyle('Disc', parent=st['Italic'], fontSize=9,
                          textColor=colors.HexColor('#555555'))
    bullet = ParagraphStyle('Bul', parent=body, leftIndent=10, spaceAfter=2)

    story = []
    S = story.append

    # ---------- Page de titre ----------
    S(Spacer(1, 1.2*cm))
    S(Paragraph('Audit de la collecte de données', ParagraphStyle(
        'T', parent=st['Title'], fontSize=22, textColor=colors.HexColor(ACCENT))))
    S(Paragraph('SDK HTML5 et plateforme GameMonetize.com', ParagraphStyle(
        'ST', parent=st['Title'], fontSize=15, textColor=colors.HexColor('#333333'))))
    S(Spacer(1, 0.8*cm))
    intro = Table([
        ['Objet de l\'étude',
         "SDK HTML5 « api.gamemonetize.com/sdk.js » (v1.2.4), driver « game-driver.js » "
         "(bridge v8), pages de jeu, site gamemonetize.com et flux publicitaire "
         "(Google AdX / IMA)."],
        ['Jeu analysé',
         "« Dark Hood » — https://uncached.gamemonetize.com/1zhakvwsb80tili3c8p352rmrjt011w5/"],
        ['Méthode',
         "1) Ingénierie inverse du SDK obfusqué (dé-obfuscation + lecture du code). "
         "2) Session de jeu réelle dans Chromium sous X (Xvfb), tout le trafic HTTPS intercepté "
         "et journalisé via mitmproxy. 3) Navigation du site gamemonetize.com sous la même "
         "instrumentation. 4) Déclenchement et observation d'une vraie publicité."],
        ['Trace observée', "1 002 requêtes HTTP(S) captées pendant la session de jeu."],
        ['Date', "29 octobre 2026"],
        ['Contexte',
         "Document informatif indépendant à visée de transparence ; aucune donnée personnelle "
         "réelle n'a été exposée (navigateur instrumenté, session d'observation dédiée)."],
    ], colWidths=[3.6*cm, 13.2*cm])
    intro.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fdeaea')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    S(intro)
    S(Spacer(1, 0.7*cm))
    S(Paragraph('Résumé des principales observations', h2))
    for b in [
        "Avant la moindre publicité, dès le chargement, le SDK transmet le <b>domaine du site "
        "hébergeant le jeu</b> et l'<b>identifiant du jeu</b> (pixel event.php), puis installe "
        "<b>Google Analytics 4</b> avec des cookies qui identifient la session.",
        "La <b>requête de pub</b> envoyée à Google (DoubleClick AdX via IMA) contient l'<b>URL "
        "exacte du jeu joué</b>, une <b>empreinte navigateur</b> (fingerprint UA-CH), la "
        "<b>langue, des timings de chargement</b> et un <b>identifiant de session publicitaire</b>.",
        "Pendant ce même cycle, même sans clic réel sur la créative, le SDK poste vers "
        "<b>api.gamemonetize.com/opphbh.php</b> et <b>opphbh2.php</b> (identifiant du jeu + "
        "domaine du site ; l'adresse IP est visible du serveur).",
        "Une <b>créative publicitaire (confect.io)</b> servie comme pub a aussi appelé "
        "<b>api.ipify.org</b> pour <b>lire l'adresse IP publique du joueur</b>.",
        "Le consentement est présumé : le splash affiche « By clicking “PLAY GAME”, you consent "
        "to transmit your data to our partners » — il n'y a <b>pas de bouton pour refuser</b>. "
        "Le SDK pose alors un cookie <b>ogdpr_tracking=1</b> valant 90 jours.",
        "<b>Incohérence du code :</b> le paramètre <b>npa=0</b> (publicités personnalisées "
        "demandées) est codé en dur ; le drapeau userDeclinedPersonalAds (gdpr-targeting=0) est "
        "lu mais <b>jamais appliqué</b> à la requête de pub.",
    ]:
        S(Paragraph('&bull;  ' + b, bullet))

    S(Spacer(1, 0.5*cm))
    S(Paragraph('1. Ce que le code du SDK contient (audit statique)', h1))

    S(Paragraph('1.1 Balise d\'audience à l\'initialisation (avant toute pub)', h2))
    S(Paragraph("Dès l'initialisation, le SDK envoie un pixel GET via une new Image() :", body))
    S(Paragraph('https://gamemonetize.com/account/event.php?page_url=&lt;domaine hébergeant le '
                'jeu&gt;&amp;game_id=&lt;ID du jeu&gt;&amp;eventtype=1', code))
    S(Paragraph("Données ainsi accumulées : le domaine du site qui héberge le jeu (ici "
                "uncached.gamemonetize.co), l'ID exact du jeu, et implicitement votre adresse IP "
                "visible par le serveur. En parallèle, le SDK stocke dans le localStorage une "
                "variable <b>gd_tag</b> — l'URL <b>complète</b> de la page de jeu — qui sera "
                "réutilisée comme <b>description_url</b> à chaque requête de pub vers Google.", body))

    S(Paragraph('1.2 Balises POST pendant le cycle publicitaire', h2))
    S(Paragraph("Le SDK écoute les événements IMA et déclenche deux POST : l'un sur l'événement "
                "CLICK, l'autre à la fin du cycle de pub (CONTENT_RESUME_REQUESTED) :", body))
    S(Paragraph('POST https://api.gamemonetize.com/opphbh.php?id=&lt;ID jeu&gt;&amp;domain=&lt;domaine&gt;<br/>'
                'POST https://api.gamemonetize.com/opphbh2.php?id=&lt;ID jeu&gt;&amp;domain=&lt;domaine&gt;<br/>'
                'Corps (application/x-www-form-urlencoded) : h=AGt39rRaEEKgamvehwKyOKiCxRMil… (jeton fixe)', code))
    S(Paragraph("Observé en session réelle : ces POST ont été émis automatiquement pendant le "
                "cycle de pub, avec Origin/Referrer de la page de jeu et l'agent utilisateur du "
                "navigateur. Le serveur voit en plus votre IP réelle et l'horodatage exact.", body))

    S(Paragraph('1.3 Consentement (RGPD) et comportement du code', h2))
    S(Paragraph("Le splash du SDK affiche cette notice (texte exact extrait du SDK) :", body))
    S(Paragraph('"We may show personalized ads provided by our partners, and our services can not '
                'be used by children under 16 years old without the consent of their legal '
                'guardian. By clicking &quot;PLAY GAME&quot;, you consent to transmit your data to our '
                'partners for advertising purposes and declare that you are 16 years old […]"', code))
    S(Paragraph('Points relevés :', body))
    for b in [
        "Le <b>consentement est présumé par le clic</b> sur « PLAY GAME » ; il n'existe <b>pas de "
        "bouton pour refuser</b> les partenaires publicitaires.",
        "Au clic, le SDK pose un cookie <b>ogdpr_tracking=1</b> valable 90 jours — un réel "
        "cookie de suivi destiné à mémoriser le pseudo-consentement.",
        "Le SDK sait détecter un refus (paramètre gdpr-targeting=0 ou cookie "
        "ogdpr_advertisement=0 → userDeclinedPersonalAds)… mais <b>n'utilise jamais</b> cette "
        "variable : la requête vers DoubleClick contient toujours <b>npa=0</b> en dur, c'est-à-dire "
        "des <b>publicités personnalisées demandées</b> même si le joueur refuse.",
        "Le SDK charge <b>Google Analytics 4</b> (G-8SK3BC00X8, via ga.js), le <b>Google IMA "
        "SDK</b>, gpt.js (DoubleClick) et des listes de configuration datax.json / dataxx.json / "
        "dataxxx.json qui segmentent les éditeurs (whitelabels : y8.com, pog.com, gamepost.com, "
        "vkplay.ru, dzen.ru, sites.google.com…).",
        "Il lit <b>navigator.userAgent / vendor / opera</b> pour déterminer la plateforme "
        "(Android, iPhone/iPad, BlackBerry, Windows Phone, Opera Mini).",
    ]:
        S(Paragraph('&bull;  ' + b, bullet))

    S(Spacer(1, 0.5*cm))
    S(Paragraph('2. Ce que la session de jeu a réellement envoyé (trafic intercepté)', h1))

    S(Paragraph('2.1 Tiers contactés pendant une seule session de jeu', h2))
    tab = Table([
        ['Tiers', 'Req.', 'Rôle'],
        ['img.gamemonetize.com', '280', 'Serveur de fichiers du jeu (assets)'],
        ['gamemonetize.com', '192', 'SDK, pages, event.php, ga.js, logo'],
        ['uncached.gamemonetize.co', '146', 'Runtime du jeu (c2runtime, médias)'],
        ['confect.io', '134', 'Créative publicitaire (site de l\'annonceur)'],
        ['doubleclick.net (4 hôtes)', '22', 'Distribution publicitaire + identifiants pub Google'],
        ['pagead2.googlesyndication.com', '14', 'Requête de pub VAST + adview + télémétrie gen_204'],
        ['region1.google-analytics.com', '10', 'Google Analytics 4 (G-8SK3BC00X8)'],
        ['imasdk.gstatic/gapis, fundingchoices, googletagmanager', '32', 'IMA SDK, bandeau de consentement Google, gtag'],
        ['api.ipify.org', '4', 'Lecture de votre IP publique par la créative pub'],
        ['api.gamemonetize.com', '16', 'sdk.js, POST opphbh/opphbh2, datax/dataxx.json'],
        ['www.googleadservices.com', '4', 'Suivi publicitaire Google'],
    ], colWidths=[6.2*cm, 1.4*cm, 9.2*cm])
    tab.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fdeaea')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    S(tab)

    S(Paragraph('2.2 Avant la pub (chargement de la page)', h2))
    S(Paragraph("Dès le chargement, avant tout clic de l'utilisateur :", body))
    for b in [
        "<b>GET /account/event.php?page_url=uncached.gamemonetize.co&amp;game_id=1zhakvwsb8…"
        "&amp;eventtype=1</b> — domaine + ID du jeu transmis (plus votre IP).",
        "<b>Google Analytics 4</b> installe les cookies <b>_ga</b> et <b>_ga_8SK3BC00X8</b> sur "
        "le domaine du jeu et envoie des « collect » à region1.google-analytics.com : la session "
        "est déjà identifiée sans aucune action.",
        "Le localStorage reçoit <b>gd_tag</b> (URL complète de la page de jeu), base de la "
        "description_url publicitaire, ainsi que <b>gd_midroll</b>.",
        "Chargement de l'IMA SDK, gpt.js, sdk.js, ga.js et des listes datax.json/dataxx.json.",
    ]:
        S(Paragraph('&bull;  ' + b, bullet))

    S(Paragraph('2.3 La requête de pub elle-même (paramètres captés)', h2))
    S(Paragraph('GET https://pagead2.googlesyndication.com/gampad/ads (Google AdX via IMA) — '
                'paramètres observés :', body))
    tab2 = Table([
        ['Paramètre', 'Valeur observée (extraits)'],
        ['iu', "/21739493398/ca-games-pub-5519830896693885-tag (inventaire AdX de GameMonetize)"],
        ['description_url et url', "https://uncached.gamemonetize.co/1zhakvwsb80tili3c8p352rmrjt011w5/"
                                   " — l'URL exacte de la page où vous jouez"],
        ['npa', "0 — publicités personnalisées demandées (codé en dur, cf. §1.3)"],
        ['uach', "Empreinte client (UA-CH) complète : plateforme Linux, architecture x86, "
                 "64 bits, version du navigateur, toutes les paires marque/version"],
        ['hl', "fr — langue du navigateur"],
        ['sid', "3FEE8024-… — identifiant de session publicitaire (IMA)"],
        ['dlt / idt / dt', "Horodatages : chargement du splash, initialisation du SDK, timing du DOM"],
        ['pvsid et scor', "Identifiants de session multi-domaines de Google"],
        ['correlator, adk, sdkv, omid_p…', "Paramètres techniques de matching de session et de version SDK"],
    ], colWidths=[4.2*cm, 12.6*cm])
    tab2.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fdeaea')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    S(tab2)

    S(Paragraph('2.4 Pendant et après la pub', h2))
    for b in [
        "La pub affichée était une créative <b>confect.io</b> (campagne "
        "« utubeo-display-audiences-performance-0926 », gad_campaignid=24278100412, avec gclid "
        "Google) rendue comme page interactive dans le lecteur du jeu.",
        "<b>La créative a interrogé api.ipify.org deux fois</b> — ce service renvoie à la "
        "créative votre <b>adresse IP publique</b>. La publicité demande elle-même l'IP du joueur.",
        "La créative a aussi pré-chargé ses propres pages internes (pricing, register, demo, agencies).",
        "Google a pingé <b>/pagead/adview</b> (« pub vue »), <b>/pagead/interaction</b> et "
        "plusieurs <b>/pagead/gen_204</b> (télémétrie IMA : slotId, puid, vast_v…).",
        "<b>Après la pub</b>, le SDK a envoyé <b>opphbh.php</b> et <b>opphbh2.php</b> (ID du jeu + "
        "domaine du site), et GA4 a envoyé des « collect ». Google a interrogé /pagead/id pour "
        "ses identifiants publicitaires.",
    ]:
        S(Paragraph('&bull;  ' + b, bullet))

    S(Spacer(1, 0.5*cm))
    S(Paragraph('3. Le site gamemonetize.com (hors jeux)', h1))
    for b in [
        "<b>Google Analytics 4</b> (propriété G-<b>FBJW7DPF00</b>) + cookies <b>_ga</b> et "
        "<b>_ga_FBJW7DPF00</b> (2 ans).",
        "<b>FCCDCF</b> — cookie du CMP Google (Funding Choices), posé par défaut sans interaction ; "
        "il embarque la chaîne de consentement (TC String).",
        "Une <b>iframe YouTube</b> avec les cookies YouTube.",
        "Sur la page même « Privacy Policy », Google a demandé la configuration pub via "
        "<b>purl_config?url=https://gamemonetize.com/privacypolicy</b> : la page de "
        "confidentialité déclenche elle-même des requêtes publicitaires.",
        "Les lecteurs pub (gpt.js, pubads_impl.js) sont chargés sur le site en général.",
    ]:
        S(Paragraph('&bull;  ' + b, bullet))

    S(Paragraph('3.1 Contradiction avec la politique de confidentialité', h2))
    S(Paragraph('La politique de confidentialité (GMO Holding Ltd [939349], mise à jour '
                '27/02/2025) affirme notamment : <b>« We do not use cookies »</b>. Ceci est en '
                "contradiction avec ce qui a été observé : cookies GA4 sur les pages de jeu, "
                "cookies GA4 + FCCDCF sur le site, cookies publicitaires Google, localStorage "
                "(gd_tag, gd_midroll). La politique traite surtout le site B2B ; le suivi de "
                "l'internaute qui joue — la donnée la plus sensible du service — y est très "
                "peu décrit.", body))
    S(Paragraph('Extrait de la page de confidentialité :', body))
    S(Paragraph('"Who is collecting the data? GMO Holding Ltd. [939349] […] acts as Data '
                'Controller […] personal data will be collected only for lawful and relevant '
                'purposes…"', code))

    S(Spacer(1, 0.5*cm))
    S(Paragraph('4. Synthèse : quelles données sur moi ?', h1))
    tab3 = Table([
        ['Donnée', 'Collectée par', 'Quand'],
        ['Adresse IP publique', 'GameMonetize (event/opphbh), Google (ads), la créative pub '
                                'via ipify, et tout serveur contacté', 'Chargement, pubs, clics'],
        ['Domaine du site où vous jouez', 'event.php, opphbh/2, description_url', 'Chargement + chaque pub'],
        ['ID du jeu joué', 'event.php, opphbh/2, iu', 'Chargement + chaque pub'],
        ['URL exacte de la page de jeu', 'gd_tag (localStorage) → description_url, url', 'Chargement + chaque pub'],
        ['Empreinte navigateur (UA-CH)', 'DoubleClick AdX (paramètre uach)', 'Requête de pub'],
        ['Langue du navigateur', 'DoubleClick AdX (hl), GA4', 'Requête de pub'],
        ['Identifiant de session pub (sid)', 'IMA / Google', 'Requête de pub'],
        ['Timings de chargement (dlt/idt/dt)', 'DoubleClick AdX', 'Requête de pub'],
        ['Identifiants GA4', 'Cookies _ga, _ga_8SK3BC00X8 (2 ans)', 'Dès le chargement du jeu'],
        ['Cookie « consentement » ogdpr_tracking=1', 'SDK GameMonetize (90 jours)', 'Au clic PLAY GAME (si splash GDPR)'],
        ['localStorage gd_tag / gd_midroll', 'SDK GameMonetize', 'Persistant jusqu\'à purge manuelle'],
        ['Événements de pub (vue, clic, complétion)', 'IMA gen_204/adview/interaction + opphbh/2', 'Chaque cycle de pub'],
    ], colWidths=[5.0*cm, 7.0*cm, 4.8*cm])
    tab3.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fdeaea')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    S(tab3)

    S(Spacer(1, 0.4*cm))
    S(Paragraph('5. Ce que le driver du jeu (game-driver.js) ne fait PAS', h1))
    S(Paragraph("Pour être équitable : le driver v8 de cette page de jeu (le pont entre le jeu et "
                "window.sdk) est <b>propre</b> : il ne stocke que le localStorage local du jeu "
                "(sauvegardes, score), déclenche les pubs via le SDK et écoute les gestes "
                "utilisateur pour cadencer les interstitiels — il ne transmet rien à un serveur "
                "de lui-même. La collecte vient donc <b>essentiellement du SDK GameMonetize, "
                "d'Analytics/IMA Google et de la créative publicitaire</b>, pas du jeu en "
                "lui-même.", body))

    S(Spacer(1, 0.5*cm))
    S(Paragraph('6. Recommandations pratiques pour le lecteur', h1))
    for b in [
        "Jouer avec un bloqueur de contenu actif (par ex. uBlock Origin) couvrant "
        "doubleclick.net, googlesyndication.com, google-analytics.com, imasdk.googleapis.com "
        "et ipify.org.",
        "Utiliser un navigateur à restriction élevée (cookies tiers bloqués, limitation des "
        "fingerprints), éventuellement derrière un VPN pour masquer l'adresse IP.",
        "Si vous gérez un site hébergeant ces jeux : sachez que le pixel event.php transmet le "
        "<b>nom de domaine de votre site</b> à GameMonetize, et que le SDK envoie des POST "
        "automatiques vers ses propres endpoints pendant chaque cycle de pub.",
        "Pour contester ces pratiques auprès de la CNIL ou d'autres autorités : conservez ce "
        "document — les URLs et horodatages observés y sont reproduits.",
    ]:
        S(Paragraph('&bull;  ' + b, bullet))

    S(Spacer(1, 0.6*cm))
    S(Paragraph('7. Annexes — preuves brutes', h1))
    S(Paragraph('Extrait de la trace mitmproxy (requests.jsonl) — événements clés :', body))
    S(Paragraph('GET  https://gamemonetize.com/account/event.php?page_url='
                'uncached.gamemonetize.co&amp;game_id=1zhakvwsb80tili3c8p352rmrjt011w5&amp;eventtype=1<br/>'
                'POST https://api.gamemonetize.com/opphbh.php?id=1zhakvwsb8…&amp;'
                'domain=uncached.gamemonetize.co  [corps : h=AGt39rR…]<br/>'
                'POST https://api.gamemonetize.com/opphbh2.php?id=1zhakvwsb8…&amp;'
                'domain=uncached.gamemonetize.co  [corps : h=AGt39rR…]<br/>'
                'POST https://region1.google-analytics.com/g/collect?…&amp;tid=G-8SK3BC00X8…<br/>'
                'GET  https://pagead2.googlesyndication.com/gampad/ads?iu=/21739493398/…&amp;'
                'description_url=https://uncached.gamemonetize.co/…&amp;npa=0&amp;uach=…<br/>'
                'GET  https://api.ipify.org/?format=json  [referent : https://confect.io/product/'
                'performance?utm_campaign=utubeo-display-audiences-performance-0926…]', code))
    S(Paragraph('Méthode de capture : mitmproxy 12.2.3 (port 8888), Chromium 150 sous Xvfb. La '
                "trace complète couvre le chargement, les interactions de jeu, le cycle complet "
                "d'une publicité, puis la navigation du site. Les captures d'écran de la session "
                "sont annexées ci-dessous.", body))

    S(Spacer(1, 0.3*cm))
    for path, cap in screenshots:
        try:
            img = Image(path, width=15.5*cm, height=15.5*cm * (800.0/1280))
            S(img)
            S(Paragraph(cap, disc))
            S(Spacer(1, 0.3*cm))
        except Exception as e:
            print('skip', path, e)

    S(Spacer(1, 0.6*cm))
    S(Paragraph('Avertissement : cette étude a été réalisée avec un navigateur instrumenté ; '
                "aucune donnée réelle de joueur n'a été utilisée. Les traces citées correspondent "
                "à nos propres sessions d'observation. Les faits sont présentés à titre "
                "d'information ; l'interprétation juridique (RGPD, ePrivacy) dépend du contexte "
                "et un avis juridique reste le cas échéant nécessaire.", disc))

    doc.build(story)
    print('PDF généré :', dest)


if __name__ == '__main__':
    shots = []
    for p, c in [('shots/game_play.png', 'Session de jeu (Xvfb) : le jeu fonctionne normalement.'),
                 ('shots/game_ads.png', 'Pendant le cycle publicitaire (créative affichée).'),
                 ('shots/site_home.png', "Page d'accueil de gamemonetize.com.")]:
        if os.path.exists(p):
            shots.append((p, c))
    build_pdf('/tmp/gm_audit/GameMonetize_audit_donnees.pdf', shots)
