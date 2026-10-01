"""Gestion des langues : CatalogueLangue."""
from collections import Counter
import asyncio
import json
import os
import shutil
import time
import LSL_MCL_TEXTES
import LSL_MCL_VARIABLES as V
from LSL_MCL_SUIVI import SuiviProgression

class CatalogueLangue:
    """Services de CatalogueLangue."""

    @classmethod
    def normaliser_code(cls, code):
        """Valide et normalise le code de langue."""
        code = str(code or '').strip().lower()
        if not cls.LANGUE_RE.fullmatch(code):
            raise ValueError('Language : code de langue invalide (exemple : pt ou pt-BR)')
        return code

    @staticmethod
    def nom_langue_local(code):
        """
        Récupère automatiquement le nom de la langue
        écrit dans cette même langue.

        Exemples :
            nl -> Nederlands
            de -> Deutsch
            it -> Italiano
            es -> Español
            pt -> Português

        En cas d'échec de Google, utilise le nom anglais
        fourni par googletrans.
        """
        code = str(code or '').strip().lower()
        try:
            from googletrans import LANGUAGES, Translator
            nom_anglais = LANGUAGES.get(code)
            if not nom_anglais:
                return code.upper()

            async def traduire_nom():
                """Traduit de façon asynchrone le nom affiché de la langue."""
                async with Translator() as client:
                    resultat = await client.translate(nom_anglais, src='en', dest=code)
                    return resultat.text
            return asyncio.run(traduire_nom())
        except Exception:
            try:
                from googletrans import LANGUAGES
                return LANGUAGES.get(code, code.upper()).title()
            except (ImportError, AttributeError):
                return code.upper()

    @classmethod
    def chemin_catalogue(cls, code):
        """Calcule le chemin du catalogue de traduction de la langue."""
        code = cls.normaliser_code(code)
        return V.ROOT / f"LSL_MCL_others_language_{code.replace('-', '_')}.json"

    @classmethod
    def selectionner_catalogue(cls, code):
        """Sélectionne le JSON propre à la langue sans toucher aux autres langues."""
        code = cls.normaliser_code(code)
        cible = cls.chemin_catalogue(code)
        if not cible.exists() and cls.CATALOGUE_LEGACY.exists():
            try:
                ancien = json.loads(cls.CATALOGUE_LEGACY.read_text(encoding='utf-8'))
                if str(ancien.get('Language', '')).lower() == code:
                    shutil.copy2(cls.CATALOGUE_LEGACY, cible)
                    print(f'[AUTRE LANGUE] Catalogue {code.upper()} migré : {cible.name}')
            except (OSError, json.JSONDecodeError):
                pass
        cls.CATALOGUE = cible
        return cible

    @classmethod
    def lire(cls, code=None):
        """Charge et décode le catalogue enregistré sur disque."""
        if code is not None:
            cls.selectionner_catalogue(code)
        if not cls.CATALOGUE.exists():
            return {}
        try:
            return json.loads(cls.CATALOGUE.read_text(encoding='utf-8'))
        except json.JSONDecodeError as erreur:
            raise RuntimeError(f'Catalogue JSON invalide : {cls.CATALOGUE}\n{erreur}') from erreur

    @classmethod
    def langue(cls):
        """Lit la langue du catalogue actif/legacy ; conserve la compatibilité du menu actuel."""
        catalogue = cls.lire()
        if not catalogue and cls.CATALOGUE_LEGACY.exists():
            try:
                catalogue = json.loads(cls.CATALOGUE_LEGACY.read_text(encoding='utf-8'))
            except (OSError, json.JSONDecodeError):
                catalogue = {}
        return cls.normaliser_code(catalogue.get('Language', 'en'))

    @staticmethod
    def source_originale():
        """Localise les fichiers JAM PC servant de source originale."""
        for base in (V.PC_VERSION_BACKUP, V.PC_VERSION):
            dossier = base / 'Data' / 'JamFiles' / 'PC'
            if dossier.is_dir():
                return dossier
        return None

    @staticmethod
    def identite(entree):
        """Construit une clé stable pour une entrée de traduction."""
        return (entree['file'].casefold(), entree['block'], entree['key'], entree['occurrence'])

    @classmethod
    def inventorier(cls, dossier):
        """Inventorie les chaînes des JAM de la source choisie."""
        import LSL_MCL_TEXTES
        textes = LSL_MCL_TEXTES.LSL_MCL_Textes
        entrees = []
        fichiers_jam = sorted((fichier for fichier in dossier.rglob('*') if fichier.is_file() and fichier.suffix.lower() == '.jam'))
        suivi = SuiviProgression('CHARGEMENT TEXTES', len(fichiers_jam))
        for numero, fichier in enumerate(fichiers_jam, 1):
            suivi.avancer(numero - 1, fichier.name)
            relatif = fichier.relative_to(dossier).as_posix()
            for bloc in textes.blocs_texte(fichier.read_bytes()):
                occurrences = Counter()
                for ligne in V.ENTRY.finditer(bloc['payload']):
                    cle = ligne.group(2).decode('latin1')
                    numero = occurrences[cle]
                    occurrences[cle] += 1
                    entrees.append({'index': len(entrees), 'file': relatif, 'block': bloc['chunk_index'], 'namespace': bloc['namespace'], 'key': cle, 'occurrence': numero, 'English': ligne.group(4).decode('cp1252', errors='replace'), 'translation': ''})
        suivi.terminer()
        return entrees

    @classmethod
    def ecrire(cls, contenu, tentatives=8):
        """Écriture atomique ; conserve le .tmp si Windows verrouille momentanément le JSON."""
        cls.CATALOGUE.parent.mkdir(parents=True, exist_ok=True)
        temporaire = cls.CATALOGUE.with_suffix(cls.CATALOGUE.suffix + '.tmp')
        temporaire.write_text(json.dumps(contenu, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        for essai in range(1, tentatives + 1):
            try:
                os.replace(temporaire, cls.CATALOGUE)
                return True
            except PermissionError:
                if essai == tentatives:
                    print(f'[AUTRE LANGUE] JSON verrouillé ; secours conservé : {temporaire}')
                    return False
                time.sleep(0.35)
        return False

    @classmethod
    def synchroniser(cls, dossier=None, code=None):
        """
        Synchronise le catalogue avec les JAM PC originaux.

        SECURITE :
        - une traduction existante non vide n'est jamais supprimée ;
        - une nouvelle entrée reçoit une traduction vide ;
        - si l'identité exacte change, une récupération de secours est tentée ;
        - aucune ancienne traduction n'est remplacée par "" ;
        - les anciennes entrées non retrouvées sont conservées en OrphanedEntries.
        """
        dossier = dossier or cls.source_originale()
        if dossier is None:
            print('[AUTRE LANGUE] JAM PC originaux absents ; génération différée.')
            return None
        if code is not None:
            cls.selectionner_catalogue(code)
        ancien = cls.lire()
        langue = cls.normaliser_code(code or ancien.get('Language', 'en'))
        if code is not None:
            cls.selectionner_catalogue(langue)
            ancien = cls.lire()
        anciennes_entrees = ancien.get('Entries', [])
        precedents = {cls.identite(entree): entree for entree in anciennes_entrees}
        secours = {}
        for entree in anciennes_entrees:
            cle_secours = (str(entree.get('file', '')).casefold(), str(entree.get('namespace', '')), str(entree.get('key', '')), str(entree.get('English', '')))
            secours.setdefault(cle_secours, []).append(entree)
        entrees = cls.inventorier(dossier)
        ids = set()
        changements = 0
        traductions_preservees = 0
        traductions_secours = 0
        for entree in entrees:
            identifiant = cls.identite(entree)
            ids.add(identifiant)
            precedent = precedents.get(identifiant)
            if precedent is not None:
                ancienne_traduction = precedent.get('translation', '')
                if ancienne_traduction:
                    entree['translation'] = ancienne_traduction
                    traductions_preservees += 1
                else:
                    entree['translation'] = ''
                if precedent.get('English') != entree['English']:
                    entree['source_changed'] = True
                    changements += 1
                elif precedent.get('source_changed'):
                    entree['source_changed'] = True
                continue
            cle_secours = (str(entree.get('file', '')).casefold(), str(entree.get('namespace', '')), str(entree.get('key', '')), str(entree.get('English', '')))
            candidats = secours.get(cle_secours, [])
            if len(candidats) == 1:
                candidat = candidats[0]
                ancienne_traduction = candidat.get('translation', '')
                if ancienne_traduction:
                    entree['translation'] = ancienne_traduction
                    traductions_preservees += 1
                    traductions_secours += 1
                    print('[AUTRE LANGUE] Traduction récupérée par secours :', entree['file'], entree['key'], 'index', entree['index'])
        nom_langue = ancien.get('LanguageName')
        if not nom_langue:
            nom_langue = cls.nom_langue_local(langue)
        catalogue = {'Language': langue, 'LanguageName': nom_langue, 'AutoTranslate': ancien.get('AutoTranslate', True), 'Entries': entrees}
        orphelines = [entree for identifiant, entree in precedents.items() if identifiant not in ids]
        for entree in ancien.get('OrphanedEntries', []):
            identifiant = cls.identite(entree)
            if identifiant not in ids and identifiant not in precedents:
                orphelines.append(entree)
        if orphelines:
            catalogue['OrphanedEntries'] = orphelines
        anciennes_traductions = sum((1 for entree in anciennes_entrees if entree.get('translation')))
        nouvelles_traductions = sum((1 for entree in entrees if entree.get('translation')))
        print('[AUTRE LANGUE] Traductions avant synchro :', anciennes_traductions)
        print('[AUTRE LANGUE] Traductions après synchro :', nouvelles_traductions)
        print('[AUTRE LANGUE] Traductions préservées :', traductions_preservees, '| récupérées par secours :', traductions_secours)
        if anciennes_traductions > 0 and nouvelles_traductions < anciennes_traductions:
            print()
            print('[SECURITE] ATTENTION : la synchronisation ferait perdre des traductions.')
            print('[SECURITE] Anciennes :', anciennes_traductions, '| nouvelles :', nouvelles_traductions)
            print("[SECURITE] Le catalogue original N'A PAS ETE ECRASE.")
            raise RuntimeError('Synchronisation annulée : perte de traductions détectée.')
        propages = cls.propager_traductions_connues(catalogue)
        if propages:
            cls.ecrire(catalogue)
        if langue not in ('en', 'fr', 'de', 'es', 'it') and catalogue['AutoTranslate']:
            cls.traduire_automatiquement(catalogue)
        if catalogue != ancien:
            cls.ecrire(catalogue)
        print(f'[AUTRE LANGUE] {len(entrees)} entrées ; {changements} textes anglais actualisés : {cls.CATALOGUE}')
        return catalogue
