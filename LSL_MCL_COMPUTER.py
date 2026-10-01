"""Fonctions du domaine COMPUTER pour Larry MCL."""
import csv
from pathlib import Path
import re
import json
import subprocess
import string
import time
import LSL_MCL_VARIABLES as V

class LSL_MCL_Computer:
    """Détection des installations PC et PS2 et fermeture du jeu sous Windows."""

    @staticmethod
    def chemins_version_probables():
        """Renvoie les racines probables, dont les bibliothèques Steam déclarées."""
        racines = set()
        for lecteur in LSL_MCL_Computer.lister_lecteurs_windows():
            racines.add(lecteur)
            racines.add(lecteur / 'SteamLibrary')
            racines.add(lecteur / 'PC')
            racines.add(lecteur / 'GOG Games')
            racines.add(lecteur / 'Games')
            racines.add(lecteur / 'Jeux')
        racines.add(Path('C:\\Program Files'))
        racines.add(Path('C:\\Program Files (x86)'))
        racines.add(Path('C:\\GOG Games'))
        try:
            import winreg
            cles = ((winreg.HKEY_CURRENT_USER, 'Software\\Valve\\Steam', 'SteamPath'), (winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\WOW6432Node\\Valve\\Steam', 'InstallPath'))
            for hive, cle, valeur in cles:
                try:
                    with winreg.OpenKey(hive, cle) as reg:
                        chemin, _ = winreg.QueryValueEx(reg, valeur)
                        racines.add(Path(chemin))
                except OSError:
                    pass
        except ImportError:
            pass
        for racine in list(racines):
            vdf = racine / 'steamapps' / 'libraryfolders.vdf'
            if not vdf.exists():
                continue
            try:
                contenu = vdf.read_text(encoding='utf-8', errors='ignore')
                for chemin in re.findall('"path"\\s+"([^"]+)"', contenu):
                    racines.add(Path(chemin.replace('\\\\', '\\')))
            except OSError:
                pass
        return sorted(racines, key=lambda p: str(p).lower())

    @staticmethod
    def _installation_pc_valide(chemin):
        """Vérifie que le chemin contient les dossiers requis par le moteur."""
        try:
            chemin = Path(chemin)
            return chemin.is_dir() and (chemin / 'Data' / 'JamFiles' / 'PC').is_dir()
        except (OSError, ValueError, TypeError):
            return False

    @staticmethod
    def _candidats_jeu_depuis_racine(racine):
        """Recherche les installations dans une liste de sous-dossiers, sans scan récursif."""
        racine = Path(racine)
        candidats = (racine, racine / V.GAME_NAME, racine / 'steamapps' / 'common' / V.GAME_NAME, racine / 'GOG Games' / V.GAME_NAME, racine / 'Games' / V.GAME_NAME, racine / 'Jeux' / V.GAME_NAME, racine / 'Program Files' / V.GAME_NAME, racine / 'Program Files (x86)' / V.GAME_NAME)
        for candidat in candidats:
            if LSL_MCL_Computer._installation_pc_valide(candidat):
                yield candidat

    @staticmethod
    def detecter_jeu():
        """Lit le chemin mémorisé ou recherche une installation PC ; renvoie None si aucune n’est choisie."""
        if V.CONFIG.exists():
            try:
                cfg = json.loads(V.CONFIG.read_text(encoding='utf-8'))
                chemin = cfg.get('game_root') if isinstance(cfg, dict) else None
                if isinstance(chemin, str) and chemin.strip():
                    jeu = Path(chemin)
                    if LSL_MCL_Computer._installation_pc_valide(jeu):
                        return jeu
                print("[CONFIG] Chemin absent ou invalide ; recherche de l'installation.")
            except (OSError, ValueError) as erreur:
                print('[CONFIG] Configuration illisible :', erreur)
        candidats = []
        deja_vus = set()
        for racine in LSL_MCL_Computer.chemins_version_probables():
            for jeu in LSL_MCL_Computer._candidats_jeu_depuis_racine(racine):
                cle = str(jeu.resolve()).casefold()
                if cle not in deja_vus:
                    deja_vus.add(cle)
                    candidats.append(jeu)
        if candidats:
            if len(candidats) == 1:
                jeu = candidats[0]
            else:
                print()
                print('Plusieurs installations PC detectees :')
                for i, candidat in enumerate(candidats, 1):
                    print(f' [{i}] {candidat}')
                choix = input("Choisissez l'installation [1] : ").strip()
                try:
                    index = int(choix or '1') - 1
                    if not 0 <= index < len(candidats):
                        raise ValueError('Choix hors limites')
                    jeu = candidats[index]
                except (ValueError, IndexError):
                    print('[CHOIX] Choix invalide ; première installation sélectionnée.')
                    jeu = candidats[0]
            LSL_MCL_Computer._enregistrer_jeu(jeu)
            return jeu
        print()
        print('Leisure Suit Larry - Magna Cum Laude')
        print("n'a pas ete detecte automatiquement.")
        print('PC, GOG, CD/DVD et installations manuelles sont acceptes.')
        manuel = input('Chemin du dossier du jeu : ').strip().strip('"')
        if manuel:
            jeu = Path(manuel)
            if LSL_MCL_Computer._installation_pc_valide(jeu):
                LSL_MCL_Computer._enregistrer_jeu(jeu)
                return jeu
        return None

    @staticmethod
    def lister_lecteurs_windows():
        """Liste les lecteurs Windows accessibles, sans parcourir leur contenu."""
        lecteurs = []
        for lettre in string.ascii_uppercase:
            lecteur = Path(f'{lettre}:\\')
            try:
                if lecteur.exists():
                    lecteurs.append(lecteur)
            except OSError:
                pass
        return lecteurs

    @staticmethod
    def trouver_entree_racine_ci(lecteur, nom_recherche):
        """Trouve une entrée à la racine sans tenir compte de la casse ; renvoie None si elle est absente ou inaccessible."""
        lecteur = Path(lecteur)
        nom_recherche = nom_recherche.lower()
        try:
            for entree in lecteur.iterdir():
                if entree.name.lower() == nom_recherche:
                    return entree
        except OSError:
            return None
        return None

    @staticmethod
    def trouver_executable_ps2(lecteur):
        """Trouve un exécutable PS2 nommé selon les identifiants régionaux reconnus."""
        lecteur = Path(lecteur)
        motif = re.compile('^(?:SLES|SLUS|SCES|SCUS|SLPS|SLPM|SCPS|SCAJ|SCKA)[_\\.-]?\\d+(?:\\.\\d+)?$', re.I)
        try:
            for entree in lecteur.iterdir():
                if entree.is_file() and motif.fullmatch(entree.name):
                    return entree
        except OSError:
            return None
        return None

    @staticmethod
    def fermer_larry():
        """Ferme Larry.exe et attend la libération des fichiers.

Une fermeture impossible lève RuntimeError pour arrêter les opérations
qui nécessitent un jeu fermé. Un jeu déjà arrêté est accepté.
"""
        print('[LARRY.EXE] Fermeture du jeu...')
        try:
            resultat = subprocess.run(['taskkill', '/F', '/IM', 'Larry.exe'], capture_output=True, text=True, errors='replace', timeout=15)
            if resultat.returncode == 0:
                print('[LARRY] Liberation des fichiers en cours...')
                time.sleep(3)
                print('[LARRY.EXE] Jeu ferme.')
                return
            controle = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Larry.exe', '/FO', 'CSV', '/NH'], capture_output=True, text=True, errors='replace', timeout=15)
        except (OSError, subprocess.TimeoutExpired) as erreur:
            print('[LARRY.EXE ERREUR]', erreur)
            raise RuntimeError('Impossible de vérifier ou fermer Larry.exe.') from erreur
        if controle.returncode == 0 and (not any((ligne and ligne[0].casefold() == 'larry.exe' for ligne in csv.reader(controle.stdout.splitlines())))):
            print("[LARRY.EXE] Le jeu n'est pas lancé.")
            return
        message = (resultat.stderr or resultat.stdout or controle.stderr).strip()
        print('[LARRY.EXE ERREUR] Fermeture non confirmée :', message)
        raise RuntimeError("La fermeture de Larry.exe n'a pas pu être confirmée.")

    @staticmethod
    def _enregistrer_jeu(jeu):
        """Mémorise le chemin sans bloquer l'utilisation du jeu si l'écriture échoue."""
        try:
            V.CONFIG.parent.mkdir(parents=True, exist_ok=True)
            V.CONFIG.write_text(json.dumps({'game_root': str(jeu)}, indent=4), encoding='utf-8')
        except OSError as erreur:
            print('[CONFIG] Chemin utilisable mais non enregistré :', erreur)
