"""Gestion des langues : TraductionLangue."""
import asyncio
from datetime import datetime
import html
import json
import os
import re
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

class TraductionLangue:
    """Services de TraductionLangue."""

    @classmethod
    def propager_traductions_connues(cls, catalogue):
        """
        Propage une traduction déjà connue aux doublons encore en anglais.

        Exemple :
            GIRLS -> MEISJES

        Si d'autres entrées contiennent :
            GIRLS -> GIRLS

        elles deviennent :
            GIRLS -> MEISJES

        SECURITE :
        Si un même texte anglais possède plusieurs traductions différentes,
        aucune propagation n'est effectuée pour ce texte.
        """
        entrees = catalogue.get('Entries', [])
        traductions_connues = {}
        for entree in entrees:
            anglais = str(entree.get('English', '')).strip()
            traduction = str(entree.get('translation', '')).strip()
            if not anglais or not traduction:
                continue
            if traduction.casefold() == anglais.casefold():
                continue
            if not cls.marqueurs_valides(entree.get('English', ''), entree.get('translation', '')):
                continue
            cle = anglais.casefold()
            traductions_connues.setdefault(cle, set()).add(traduction)
        traductions_uniques = {}
        for cle, traductions in traductions_connues.items():
            if len(traductions) == 1:
                traductions_uniques[cle] = next(iter(traductions))
        compteur = 0
        textes_propages = set()
        for entree in entrees:
            anglais_original = str(entree.get('English', ''))
            traduction_originale = str(entree.get('translation', ''))
            anglais = anglais_original.strip()
            traduction = traduction_originale.strip()
            if not anglais:
                continue
            if traduction.casefold() != anglais.casefold():
                continue
            cle = anglais.casefold()
            nouvelle = traductions_uniques.get(cle)
            if not nouvelle:
                continue
            if not cls.marqueurs_valides(anglais_original, nouvelle):
                continue
            entree['translation'] = nouvelle
            compteur += 1
            textes_propages.add(anglais)
        print('[AUTRE LANGUE] Propagation interne :', compteur, 'entrée(s) récupérée(s) depuis', len(textes_propages), 'traduction(s) connue(s).')
        print('[AUTRE LANGUE] Textes anglais avec traduction unique connue :', len(traductions_uniques))
        return compteur

    @classmethod
    def traduire_automatiquement(cls, catalogue):
        """Traduit les entrées restantes et actualise le catalogue."""
        cle = os.environ.get('GOOGLE_CLOUD_TRANSLATE_API_KEY')
        try:
            from googletrans import Translator
        except ImportError:
            Translator = None
        if Translator is None and (not cle):
            print('[AUTRE LANGUE] Pour traduire sans clé : python -m pip install googletrans==4.0.2')
            return
        for entree in catalogue['Entries']:
            if 'TranslationDone' in entree:
                continue
            traduction = str(entree.get('translation', '')).strip()
            entree['TranslationDone'] = bool(traduction)
        attente = [e for e in catalogue['Entries'] if e['English'].strip() and (not e.get('TranslationDone', False))]
        total_global = len(catalogue['Entries'])
        deja_effectue = sum((1 for entree in catalogue['Entries'] if entree.get('TranslationDone', False)))
        restant_initial = len(attente)
        if not attente:
            return
        debut = datetime.now()
        pourcentage_reprise = deja_effectue / total_global * 100 if total_global else 0.0
        print(f"[AUTRE LANGUE] Traduction {catalogue['Language'].upper()} : {len(attente)} texte(s) restant(s) à traiter.")
        print(f'[TRANSLATE] Reprise à {pourcentage_reprise:.1f}% ({deja_effectue}/{total_global})')

        async def traduire_sans_cle(textes):
            """Traduit un lot de textes sans clé API dédiée."""
            async with Translator() as client:
                traductions = await client.translate(textes, src='en', dest=catalogue['Language'])
                return [element.text for element in traductions]
        TAILLE_LOT = 32
        MAX_TENTATIVES = 5
        ATTENTES = [5, 10, 20, 40]
        for offset in range(0, len(attente), TAILLE_LOT):
            lot = attente[offset:offset + TAILLE_LOT]
            textes = []
            groupes = []
            for entree in lot:
                protege, jetons = cls.proteger_texte(entree['English'])
                textes.append(protege)
                groupes.append(jetons)
            resultat = None
            for tentative in range(1, MAX_TENTATIVES + 1):
                try:
                    if Translator is not None:
                        resultat = asyncio.run(traduire_sans_cle(textes))
                    else:
                        url = 'https://translation.googleapis.com/language/translate/v2?' + urlencode({'key': cle})
                        corps = json.dumps({'q': textes, 'source': 'en', 'target': catalogue['Language'], 'format': 'text'}).encode()
                        with urlopen(Request(url, data=corps, headers={'Content-Type': 'application/json'}), timeout=30) as reponse:
                            resultat = [item['translatedText'] for item in json.load(reponse)['data']['translations']]
                    break
                except Exception as erreur:
                    resultat = None
                    print(f'[TRANSLATE] Echec tentative {tentative}/{MAX_TENTATIVES} : {type(erreur).__name__} {erreur}')
                    if tentative < MAX_TENTATIVES:
                        delai = ATTENTES[min(tentative - 1, len(ATTENTES) - 1)]
                        print(f'[TRANSLATE] Nouvelle tentative dans {delai} seconde(s)...')
                        time.sleep(delai)
            if resultat is None:
                print('[AUTRE LANGUE] Google indisponible après 5 tentatives.')
                print('[AUTRE LANGUE] Les traductions déjà effectuées sont sauvegardées.')
                cls.ecrire(catalogue)
                break
            if len(resultat) != len(lot):
                print('[AUTRE LANGUE] Réponse incomplète : lot conservé pour le prochain lancement.')
                cls.ecrire(catalogue)
                break
            for entree, texte, jetons in zip(lot, resultat, groupes):
                traduction = cls.restaurer_jetons(html.unescape(texte), jetons)
                traduction = cls.normaliser_texte_ais(traduction)
                if cls.marqueurs_valides(entree['English'], traduction):
                    entree['translation'] = traduction
                    entree['TranslationDone'] = True
                else:
                    print('[AUTRE LANGUE] Marqueurs non conservés :', entree['key'], 'index', entree['index'])
            cls.ecrire(catalogue)
            effectue_global = sum((1 for entree in catalogue['Entries'] if entree.get('TranslationDone', False)))
            cls.afficher_progression(effectue_global, total_global, lot[-1]['file'], debut, offset + 1, offset + len(lot), tentative, MAX_TENTATIVES, deja_effectue)
        print()

    @classmethod
    def doit_retraduire_identique(cls, entree):
        """Détermine si une traduction identique à la source doit être reprise."""
        original = entree.get('English', '').strip()
        traduit = entree.get('translation', '').strip()
        if not original or original != traduit:
            return False
        if len(original) <= 2 or re.fullmatch('[\\d\\W_]+', original):
            return False
        if original.upper() in {'KB', 'MB', 'GB', 'FPS', 'CPU', 'GPU', 'OK', 'BONUS', 'CONTROLLER 1', 'DUMMYSTR'}:
            return False
        return bool(re.search('[A-Za-z]{3,}', original))

    @classmethod
    def afficher_progression(cls, effectuer, total, fichier, debut, lot_debut=None, lot_fin=None, tentative=1, max_tentatives=5, deja_effectue=0):
        """
        Affiche un bloc de progression fixe.

        Le bloc est réécrit sur place à chaque actualisation
        afin de ne pas remplir la console.
        """
        from datetime import datetime, timedelta
        ratio = effectuer / total if total else 0.0
        maintenant = datetime.now()
        ecoule = (maintenant - debut).total_seconds()
        effectue_session = max(0, effectuer - deja_effectue)
        restant = max(0, total - effectuer)
        if effectue_session > 0 and ecoule > 0:
            secondes_par_texte = ecoule / effectue_session
            secondes_restantes = restant * secondes_par_texte
            fin_estimee = maintenant + timedelta(seconds=secondes_restantes)
            texte_fin = fin_estimee.strftime('%Hh%Mm%Ss')
        else:
            texte_fin = 'Calcul...'
        texte_debut = debut.strftime('%Hh%Mm%Ss')
        largeur = 50
        rempli = int(largeur * ratio)
        barre = '▌' * rempli + '_' * (largeur - rempli)
        if lot_debut is None:
            lot_debut = effectuer
        if lot_fin is None:
            lot_fin = effectuer
        if getattr(cls, '_progression_affichee', False):
            print('\x1b[6F', end='')
        lignes = [f'Heure début : {texte_debut}', f'Fin estimée : {texte_fin}', f'[TRANSLATE] Lot {lot_debut}-{lot_fin} | tentative {tentative}/{max_tentatives}', f'Fichier actuel traité : {fichier}', f'Progression : {effectuer:,} / {total:,}'.replace(',', ' '), f'[{barre}] {ratio * 100:5.1f} %']
        for ligne in lignes:
            print('\x1b[2K' + ligne)
        cls._progression_affichee = True
