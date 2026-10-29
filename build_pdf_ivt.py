# -*- coding: utf-8 -*-
"""PDF 2 — Données collectées pendant la session et utilisables par Google
pour déclarer une impression publicitaire valide ou invalude (IVT)."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

ACCENT = '#7a0c2e'
ACCENT2 = '#f0435a'


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def build_pdf(dest):
    doc = SimpleDocTemplate(
        dest, pagesize=A4, leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=1.6*cm, bottomMargin=1.6*cm,
        title="Données collectées et utilisation pour la validation d'une impression (IVT)",
        author="Suite de l'audit GameMonetize")
    st = getSampleStyleSheet()
    h1 = ParagraphStyle('H1', parent=st['Heading1'], fontSize=14, spaceAfter=8,
                        spaceBefore=10, textColor=colors.HexColor(ACCENT))
    h2 = ParagraphStyle('H2', parent=st['Heading2'], fontSize=11.5, spaceAfter=4,
                        spaceBefore=6, textColor=colors.HexColor(ACCENT2))
    body = ParagraphStyle('Body', parent=st['BodyText'], fontSize=9.5, leading=13)
    disc = ParagraphStyle('Disc', parent=st['Italic'], fontSize=8.5,
                          textColor=colors.HexColor('#555555'))

    story = []
    S = story.append

    S(Paragraph("Données collectées et leur rôle dans la validation d'une impression", h1))
    S(Paragraph("Suite de l'audit GameMonetize — ce second rapport liste, donnée par donnée, "
                "ce que Google a reçu pendant la session de jeu capturée et comment chaque "
                "donnée peut servir, dans son scoring de fraude publicitaire (Invalid Traffic / IVT), "
                "à déclarer l'impression <b>valide</b> ou <b>invalide</b>.", body))
    S(Spacer(1, 0.5*cm))

    S(Paragraph("A. Les données reçues par Google à la requête de pub", h2))
    tab = Table([
        ['Donnée (paramètre)', 'Valeur observée dans notre trace', 'Comment Google l\u2019utilise pour juger valide / invalide'],
        ['IP publique (implicite)', 'IP du réseau de sortie (datacenter ici)',
         'Signal n°1 : IP de datacenter, VPN, proxy ou réputation de botnet = flag fort. '
         'Plusieurs impressions depuis la même IP sur la même fenêtre = click-farm. IP résidentielle = neutre'],
        ['User-Agent (en-tête HTTP)', '"Mozilla/5.0 (X11; Linux x86_64) … Chrome/150.0.0.0 Safari/537.36"',
         'Croisé avec l\u2019uach : une incohérence UA / plateforme réelle = automatisation. '
         'Un UA headless ou un Chromium brut (sans marque « Google Chrome ») = flag automation'],
        ['uach (fingerprint UA-CH)', '[«Linux», «x86», «64», «150.0.7871.181», brands [Not;A=Brand / Chromium]]',
         'Profil matériel complet. Ici : marque « Chromium » au lieu de « Google Chrome » = le navigateur '
         'n\u2019est pas un Chrome officiel (typique d\u2019un moteur automatisé) → flag. '
         'Aussi utilisé pour la cohérence (un Linux x86 qui se déclare Windows = flag)'],
        ['_ga / _ga_8SK3BC00X8 (cookies GA4)', '_ga=GA1.1.391762364.1793271050 (créés à cette seconde)',
         'La mémoire de l\u2019écosystème Google. Un client_id neuf = visiteur « vierge ». '
         'Seul, ce n\u2019est pas un flag (des milliards de nouveaux visiteurs existent) ; '
         'mais un client_id neuf + IP datacenter + comportement scripté = cumul flagrant'],
        ['sid (session id IMA)', '3FEE8024-0D02-45A4-A935-A904939043BD',
         'Regroupe toutes les pubs d\u2019une même session. N impressions rapprochées dans le même sid '
         'avec un cadencement trop uniforme = machine'],
        ['pvsid / scor', '8442129275665853 / 1466087060819860',
         'Identifiants de session multi-domaines Google. Permettent de relier la session à tout '
         '\u00e9ventuel passage précédent de ce visiteur chez Google. Session sans passé = visiteur vierge'],
        ['correlator / adk', '1836537041127467 / 3940389611',
         'Clé de déduplication : deux impressions identiques dédupliquées = tentative de flooding'],
        ['dlt / idt / dt (timings)', 'dlt=1793271048870, idt=5107 ms, dt=1793271091378',
         'Chargement instantané ou timings trop réguliers = automation. Timings crédibles '
         '(variations humaines) = neutre'],
        ['url / description_url', 'https://uncached.gamemonetize.co/1zhakvwsb80tili3c8p352rmrjt011w5/',
         'L\u2019URL exacte du jeu. Détecte les pages dédiées à la ferme de clics, les inventaires '
         'chirurgicaux (une seule page répétée), et catégorise le contenu pour des pubs appropriées'],
        ['npa=0 / tfcd=0', 'npa=0 (pubs personnalisées demandées)',
         'Si le consentement est présumé / falsifié, l\u2019inventaire entier est conforme à risque : '
         'l\u2019impression peut être payée mais le compte éditeur (GameMonetize) est celui qui est sanctionné'],
        ['hl=fr', 'fr',
         'Langue. Incohérence avec la géo de l\u2019IP (pays anglophone avec hl=fr) = flag de trafic manipulé'],
        ['vis / frm / sdr', 'vis=1 (visible), frm=0 (page principale)',
         'La créative doit être réellement visible. Une impression servie dans un iframe caché (vis=0) '
         'ou une frame non visible = impression invalide (viewability)'],
    ], colWidths=[3.6*cm, 4.6*cm, 8.6*cm])
    tab.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fdeaea')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    S(tab)

    S(Spacer(1, 0.4*cm))
    S(Paragraph("B. Les données reçues pendant et après la diffusion de la pub", h2))
    tab2 = Table([
        ['Événement', 'Chronologie observée', 'Rôle dans le verdict'],
        ['adview (impression pinguée)', '0.114 s après la réponse VAST',
         'L\u2019impression est considérée « vue ». Pour une créative display c\u2019est normal ; '
         'pour une pub vidéo, un adview instantané sans lecture du moindre quartile est un flag de vue falsifiée'],
        ['interaction label=part2viewed', 'même instant que l\u2019adview',
         'Confirme la diffusion de la créative. S\u2019il manque des événements attendus '
         '(start, quartiles, close) c\u2019est un flag'],
        ['interaction label=elementclick', '+4.3 s puis +10.2 s après l\u2019impression',
         'Le pattern clic est plausible (temps réactionnel suffisant). Mais des positions de clics '
         'identiques ou répétées au pixel près = clic de ferme'],
        ['télémétrie gen_204 (slotId, puid, vast_v…)', 'plusieurs pings pendant le cycle',
         'Journal d\u2019événements du lecteur IMA : slot, protocole VAST, version SDK. '
         'Aucun quartile traversé sur une vidéo = lecture non réalisée → impression invalide'],
        ['IP lue par la créative via api.ipify.org', '4 appels à ipify depuis la créative confect.io',
         'La créative (annonceur) dispose de son propre check anti-fraude indépendant de Google : '
         'elle peut signaler à son tour une incohérence IP / géo / réputation'],
        ['POST opphbh / opphbh2 (GameMonetize)', 'à t+45 s et t+56 s, avec ID du jeu + domaine',
         'Côté GameMonetize : journaliser l\u2019événement pub. Pas utilisé par Google pour le verdict, '
         'mais sert à GameMonetize de preuve d\u2019inventaire livré'],
        ['collect GA4 (G-8SK3BC00X8)', 'heartbeat régulier (~15 s) pendant et après la pub',
         'Audience et engagement. La régularité déterministe des collect est un signal (des humains '
         'ont un rythme plus chaotique)'],
    ], colWidths=[4.2*cm, 4.4*cm, 8.2*cm])
    tab2.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fdeaea')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    S(tab2)

    S(Spacer(1, 0.4*cm))
    S(Paragraph("C. Ce que Google n\u2019a PAS reçu", h2))
    for b in [
        "Le <b>mouvement de la souris</b> : aucune trace de mousemove n\u2019est transmise.",
        "L\u2019<b>historique du navigateur</b> : impossible à lire côté web.",
        "Les clics <b>dans le jeu</b> (canvas) : restent locaux, non transmis.",
        "Le <b>nom</b> ou une identité réelle : jamais transmis dans nos traces.",
    ]:
        S(Paragraph('&bull;  ' + b, body))

    S(Spacer(1, 0.4*cm))
    S(Paragraph("D. Réponse sur le cookie de la trace ( explication )", h2))
    tab3 = Table([
        ['Question', 'Réponse'],
        ['Qui a créé le cookie _ga ?',
         'Le SDK de Google Analytics 4 (chargé via ga.js de GameMonetize) l\u2019a créé en JavaScript '
         'dès le chargement de la page de jeu. Ce n\u2019est pas « ton » cookie que le serveur t\u2019impose : '
         'c\u2019est le script éditeur qui le crée localement dans le navigateur.'],
        ['Le cookie est-il associé au navigateur ?',
         'Oui : il est stocké dans le fichier de profil du navigateur, pour le domaine gamemonetize.co. '
         'Il ne suit pas l\u2019utilisateur d\u2019un navigateur à l\u2019autre, ni d\u2019un appareil à l\u2019autre.'],
        ['Que se passe-t-il si le navigateur est supprimé puis réinstallé ?',
         'Tous les cookies et localStorage du profil sont perdus. Au prochain passage, GA4 recrée un '
         'client_id NEUF : le visiteur repart de zéro (mémoire vide), jusqu\u2019à ce que de nouveaux passages '
         'reconstruisent de la crédibilité.'],
        ['Peut-on « utiliser n\u2019importe quel cookie » ?',
         'Techniquement oui (le navigateur contrôle ses cookies, on peut injecter un _ga arbitraire). '
         'Mais ça n\u2019apporte rien : un client_id inventé n\u2019a aucun historique réel chez Google, '
         'il est donc aussi « vierge » qu\u2019un nouveau. La mémoire est du côté du serveur, pas dans le fichier.'],
        ['Et si le cookie est légitime mais venu d\u2019un autre appareil ?',
         'Ça donne un client_id avec de l\u2019âge mais dont l\u2019UDR réelle est un autre appareil : '
         'le verdict porterait alors sur l\u2019IP + le fingerprint (uach) de la demande, pas sur l\u2019âge du client_id seul.'],
    ], colWidths=[5.2*cm, 11.6*cm])
    tab3.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fdeaea')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    S(tab3)

    S(Spacer(1, 0.4*cm))
    S(Paragraph("E. Verdict sur notre session de capture", h2))
    S(Paragraph("Nos impressions cumulent les drapeaux : IP datacenter, navigateur Chromium "
                "automatisé (sans marque « Google Chrome »), client_id GA4 créé à l\u2019instant, "
                "clics scriptés à des positions fixes, aucune mémoire écosystème Google. "
                "Il est donc <b>probable</b> que ces impressions soient déclarées invalides "
                "a posteriori par le scoring IVT de Google, avec remboursement de l\u2019annonceur "
                "(confect.io). Le pattern est typique de « trafic automatisé », pas de fraude "
                "humaine, et ne conduit en pratique qu\u2019à l\u2019invalidation de l\u2019impression.", body))

    S(Spacer(1, 0.6*cm))
    S(Paragraph("Avertissement : analyse d\u2019une session instrumentée dédiée ; aucune donnée "
                "réelle de joueur n\u2019a été utilisée. Les mécanismes exacts de scoring anti-fraude "
                "de Google ne sont pas publics : ce document décrit les signaux observés et les "
                "usages plausibles connus publiquement du mécanisme IVT.", disc))

    doc.build(story)
    print('PDF généré :', dest)


if __name__ == '__main__':
    build_pdf('/tmp/gm_audit/IVT_impression_donnees.pdf')
