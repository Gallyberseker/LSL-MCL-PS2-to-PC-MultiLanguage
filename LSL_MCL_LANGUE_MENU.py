"""Gestion des langues : MenuLangues."""
import re
import json
import LSL_MCL_VARIABLES as V

class MenuLangues:
    """Services de MenuLangues."""

    @staticmethod
    def _nom_langue_libre(code):
        """
        Retourne le nom complet d'un code ISO à 2 lettres
        reconnu par googletrans.

        Les langues incompatibles avec le moteur texte actuel
        de Leisure Suit Larry MCL sont refusées.
        """
        code = str(code or '').strip().lower()
        if not re.fullmatch('[a-z]{2}', code):
            return None
        langues_non_compatibles = {'ja': 'Japonais', 'zh': 'Chinois', 'ko': 'Coréen', 'ar': 'Arabe'}
        if code in langues_non_compatibles:
            print()
            print('=' * 60)
            print(' LANGUE NON COMPATIBLE')
            print('=' * 60)
            print(f"{langues_non_compatibles[code]} ({code.upper()}) n'est pas compatible avec le moteur texte actuel.")
            print()
            print("Cette langue nécessite une gestion spécifique de l'encodage et des polices du jeu.")
            print()
            print('Aucun catalogue de traduction ne sera créé.')
            print('=' * 60)
            print()
            return None
        try:
            from googletrans import LANGUAGES
            return LANGUAGES.get(code)
        except (ImportError, AttributeError):
            return None

    @staticmethod
    def _saisie_avec_delai(invite, delai=10, defaut='1'):
        """Attend une saisie sous Windows ; retourne defaut après delai secondes."""
        import sys
        import time
        try:
            import msvcrt
        except ImportError:
            return input(invite).strip() or defaut
        print(invite, end='', flush=True)
        debut = time.monotonic()
        caracteres = []
        while time.monotonic() - debut < delai:
            if msvcrt.kbhit():
                touche = msvcrt.getwch()
                if touche in ('\r', '\n'):
                    print()
                    return ''.join(caracteres).strip() or defaut
                if touche == '\x08':
                    if caracteres:
                        caracteres.pop()
                        print('\x08 \x08', end='', flush=True)
                    continue
                if touche in ('\x00', 'à'):
                    if msvcrt.kbhit():
                        msvcrt.getwch()
                    continue
                if touche.isprintable():
                    caracteres.append(touche)
                    print(touche, end='', flush=True)
            time.sleep(0.05)
        print(f'\n[AUTO] Aucune réponse sous {delai} s -> choix [{defaut}].')
        return defaut

    @classmethod
    def _catalogues_libres_disponibles(cls):
        """
        Liste les catalogues LSL_MCL_others_language_XX.json déjà créés.

        Retourne pour chaque catalogue :
            code
            nom
            fichier
            traduits
            total
            pourcentage

        Le pourcentage correspond aux textes considérés comme terminés
        par le moteur de traduction.
        """
        import LSL_MCL_LANGUAGES_OTHERS
        resultat = []
        motif = re.compile('^LSL_MCL_others_language_([a-z]{2})\\.json$', re.I)
        vus = set()

        def analyser_catalogue(contenu, code):
            """Analyse les langues et traductions du catalogue."""
            nom = str(contenu.get('LanguageName', '')).strip()
            if not nom:
                nom = cls._nom_langue_libre(code) or code.upper()
            entrees = contenu.get('Entries', [])
            total = len(entrees)
            traduits = sum((1 for entree in entrees if str(entree.get('translation', '')).strip()))
            if total:
                pourcentage = traduits / total * 100.0
            else:
                pourcentage = 0.0
            return (nom, traduits, total, pourcentage)
        for fichier in sorted(V.ROOT.glob('LSL_MCL_others_language_*.json')):
            match = motif.match(fichier.name)
            if not match:
                continue
            code = match.group(1).lower()
            try:
                contenu = json.loads(fichier.read_text(encoding='utf-8'))
                nom, traduits, total, pourcentage = analyser_catalogue(contenu, code)
            except (OSError, json.JSONDecodeError):
                continue
            if code not in vus:
                resultat.append((code, nom, fichier, traduits, total, pourcentage))
                vus.add(code)
        legacy = V.ROOT / 'LSL_MCL_others_language.json'
        if legacy.exists():
            try:
                contenu = json.loads(legacy.read_text(encoding='utf-8'))
                code = str(contenu.get('Language', '')).strip().lower()
                if code and code not in vus:
                    nom, traduits, total, pourcentage = analyser_catalogue(contenu, code)
                    resultat.append((code, nom, legacy, traduits, total, pourcentage))
                    vus.add(code)
            except (OSError, json.JSONDecodeError):
                pass
        return resultat

    @classmethod
    def _menu_langues_complet(cls, detection=None):
        """
        Menu commun :
        - langues PS2 ;
        - catalogues texte ;
        - progression des traductions ;
        - création d'une nouvelle langue.
        """
        import LSL_MCL_LANGUAGES_OTHERS
        detection = cls.detecter_langues_ps2() if detection is None else detection
        langues_ps2 = list(dict.fromkeys(detection.get('langues') or []))
        if not langues_ps2:
            langues_ps2 = ['fr', 'en', 'de', 'es', 'it', 'ru']
        libres = []
        codes_ps2 = set(langues_ps2)
        for code, nom, fichier, traduits, total, pourcentage in cls._catalogues_libres_disponibles():
            if code not in codes_ps2 and code not in ('en', 'fr', 'de', 'es', 'it'):
                libres.append((code, nom, fichier, traduits, total, pourcentage))
        while True:
            print()
            print('=' * 60)
            print(' MENU DES LANGUES')
            print('=' * 60)
            if detection.get('version'):
                print('Version PS2_VERSION :', detection['version'])
            correspondances = {}
            numero = 1
            print()
            print('Liste PS2 :')
            for code in langues_ps2:
                nom = V.PROFILS_LANGUES.get(code, {}).get('nom', code.upper())
                correspondances[str(numero)] = ('ps2', code)
                print(f'[{numero}] {code.upper()} - {nom}')
                numero += 1
            print()
            print('Liste Texte non PS2 :')
            if libres:
                for code, nom, fichier, traduits, total, pourcentage in libres:
                    correspondances[str(numero)] = ('libre', code)
                    if total > 0 and traduits >= total:
                        etat = 'Texte complet'
                    else:
                        etat = 'Texte incomplet'
                    print(f'[{numero}] {code.upper()} - {nom} - {etat} {pourcentage:.1f}% ({traduits}/{total})')
                    numero += 1
            else:
                print('Aucune langue texte supplémentaire détectée.')
            print()
            print('Generer nouvelle langue :')
            print('[00] Ajouter nouvelle langue')
            print('[0] Retour / Annuler')
            print()
            print('Sans reponse sous 10 secondes, [1] sera choisi.')
            choix = cls._saisie_avec_delai('Choix : ', 10, '1')
            if choix == '0':
                return None
            if choix == '00':
                while True:
                    code = input('Code langue (2 lettres, ex: nl, pl, pt) > ').strip().lower()
                    nom = cls._nom_langue_libre(code)
                    if nom is None:
                        print('[LANGUE] Code invalide ou langue non reconnue. Entrez exactement 2 lettres.')
                        continue
                    print()
                    print('=' * 60)
                    print(' ATTENTION - TRADUCTION AUTOMATIQUE')
                    print('=' * 60)
                    print("La traduction complète peut prendre jusqu'à environ 2 heures selon le nombre de textes et la disponibilité du service.")
                    print('[TRANSLATE] La progression sera sauvegardée après chaque lot.')
                    print('=' * 60)
                    print()
                    print(f'Vous avez choisi "{nom}" ({code.upper()}).')
                    confirmation = input('Confirmer ? OUI / NON > ').strip().lower()
                    if confirmation in ('oui', 'o', 'yes', 'y'):
                        autre = LSL_MCL_LANGUAGES_OTHERS.LSL_MCL_Languages_others
                        autre.selectionner_catalogue(code)
                        catalogue = autre.lire(code)
                        if not catalogue:
                            nom_local = autre.nom_langue_local(code)
                            catalogue = {'Language': code, 'LanguageName': nom_local, 'AutoTranslate': True, 'Entries': []}
                            autre.ecrire(catalogue)
                        else:
                            nom_local = catalogue.get('LanguageName') or nom
                        print(f'[AUTRE LANGUE] {nom_local} ({code.upper()}) sélectionné.')
                        return code
                    if confirmation in ('non', 'n', 'no'):
                        print('[LANGUE] Creation annulee ; retour au menu des langues.')
                        break
                    print('Reponse invalide : tapez OUI ou NON.')
                continue
            selection = correspondances.get(choix)
            if selection is None:
                print('Choix invalide. Entrez un numero affiche.')
                continue
            origine, code = selection
            if origine == 'libre':
                autre = LSL_MCL_LANGUAGES_OTHERS.LSL_MCL_Languages_others
                autre.selectionner_catalogue(code)
                catalogue = autre.lire(code)
                nom = catalogue.get('LanguageName') if catalogue else None
                if not nom:
                    nom = cls._nom_langue_libre(code) or code.upper()
                print(f'[LANGUE] Sélection texte : {nom} ({code.upper()})')
            else:
                print('[LANGUE] Selection :', V.PROFILS_LANGUES.get(code, {}).get('nom', code.upper()))
            return code

    @classmethod
    def demander_langue_localisation(cls):
        """
        Menu principal actif : conserve le choix PS2 historique + « Autre langue ».
        Menu principal inactif : ouvre directement le menu complet des langues.
        « Autre langue » ouvre exactement le même menu complet.
        """
        detection = cls.detecter_langues_ps2()
        if not V.ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD:
            return cls._menu_langues_complet(detection)
        langues = list(dict.fromkeys(detection.get('langues') or []))
        if not langues:
            langues = ['fr', 'en', 'de', 'es', 'it']
        correspondances = {str(numero): code for numero, code in enumerate(langues, start=1)}
        numero_autre = str(len(langues) + 1)
        while True:
            print()
            print('Choisissez la langue de localisation :')
            print()
            if detection.get('version'):
                print('Version PS2_VERSION :', detection['version'])
                print()
            for numero, code in enumerate(langues, start=1):
                print(f'[{numero}]', V.PROFILS_LANGUES.get(code, {}).get('nom', code.upper()))
            print(f'[{numero_autre}] Autre langue')
            print('[0] Annuler')
            choix = input('\nChoix : ').strip()
            if choix == '0':
                return None
            if choix == numero_autre:
                code = cls._menu_langues_complet(detection)
                if code is None:
                    continue
                return code
            langue = correspondances.get(choix)
            if langue is not None:
                print('[LANGUE] Selection :', V.PROFILS_LANGUES.get(langue, {}).get('nom', langue.upper()))
                return langue
            print('Choix invalide. Entrez un numero affiche.')
