"""Extraction Larry MCL : LSL_MCL_SOURCE_PS2."""
from tkinter import filedialog
import tkinter as tk
from pathlib import Path
import json
import shutil
import LSL_MCL_VARIABLES as V
import LSL_MCL_COMPUTER
import LSL_MCL_Lecteur_ISO9660
import LSL_MCL_MENU
from LSL_MCL_SUIVI import SuiviProgression
import tempfile
from contextlib import contextmanager

class SourcePs2:
    """Traitements hérités par LSL_MCL_Extractions."""

    @classmethod
    def ps2_contient_donnees(cls):
        """Vérifie les fichiers racine et la présence de JAM dans la source PS2 locale."""
        return cls._ps2_valide(V.PS2_VERSION)

    @classmethod
    def detecter_ps2_monte(cls):
        """Recherche une source PS2 montée parmi les lecteurs accessibles."""
        LSL_MCL_MENU.LSL_MCL_Menu.titre('DETECTION DU JEU PS2_VERSION')
        lecteurs = LSL_MCL_COMPUTER.LSL_MCL_Computer.lister_lecteurs_windows()
        if not lecteurs:
            print('Aucun lecteur detecte.')
            return None
        print('Lecteurs detectes :')
        for lecteur in lecteurs:
            print(' -', lecteur)
        print()
        print("Recherche d'un dossier DATA et d'un executable PS2_VERSION...")
        for lecteur in lecteurs:
            try:
                print('[SCAN JEU PS2]', lecteur)
                data = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(lecteur, 'DATA')
                executable = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(lecteur)
                if data is None:
                    print('  -> DATA absent')
                    continue
                if not data.is_dir():
                    print("  -> DATA trouve mais ce n'est pas un dossier :", data)
                    continue
                if executable is None:
                    print('  -> DATA present, mais executable PS2_VERSION absent')
                    continue
                print()
                print('[SCAN JEU PS2_VERSION] Executable detecte :')
                print(executable)
                print('[SCAN JEU PS2_VERSION] Dossier DATA detecte :')
                print(data)
                return lecteur
            except (PermissionError, OSError):
                continue
        return None

    @classmethod
    def copier_ps2_depuis_lecteur(cls, lecteur):
        """Prépare une copie complète du disque monté avant validation et publication."""
        source = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(lecteur, 'DATA')
        destination = V.PS2_VERSION
        if source is None or not source.exists() or (not source.is_dir()):
            raise RuntimeError(f'DATA PS2_VERSION introuvable : {source}')
        print()
        print('[SCAN JEU PS2_VERSION] Copie complete de la version source...')
        print('Source :', source)
        print('Destination :', destination)
        origine, cible = (Path(lecteur).resolve(), destination.resolve())
        if origine == cible or origine in cible.parents or cible in origine.parents:
            raise ValueError('La source PS2 et la destination doivent être indépendantes.')
        with cls._preparer_source(destination) as destination:
            fichiers_source = [f for f in Path(lecteur).rglob('*') if f.is_file()]
            suivi = SuiviProgression('COPIE PS2', len(fichiers_source))
            copies = 0

            def copier_avec_suivi(source, cible):
                """Copie un fichier PS2 et signale son avancement."""
                nonlocal copies
                resultat = shutil.copy2(source, cible)
                copies += 1
                suivi.avancer(copies, Path(source).name)
                return resultat
            shutil.copytree(lecteur, destination, copy_function=copier_avec_suivi)
            suivi.terminer()
            executable = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(lecteur)
            nom_executable = executable.name.upper() if executable is not None else None
            edition = V.EDITIONS_PS2.get(nom_executable, {})
            profil_source = {'lecteur_source': str(lecteur), 'executable_ps2': nom_executable, 'langue_detectee': edition.get('langue'), 'nom_langue': edition.get('nom'), 'edition_connue': bool(edition), 'priorite_actuelle': 'fr', 'edition_francaise': nom_executable == 'SLES_526.42', 'racine_disque': str(lecteur), 'dossier_data': str(source), 'copie_complete': True}
            (destination / 'SOURCE_PS2.json').write_text(json.dumps(profil_source, ensure_ascii=False, indent=2), encoding='utf-8')
            print()
            print('[SCAN JEU PS2_VERSION] Copie terminee.')
            if executable is not None:
                print('[SCAN JEU PS2_VERSION] Version :', executable.name)
            if edition:
                print('[SCAN JEU PS2_VERSION] Langue detectee :', edition['nom'])
            return True

    @classmethod
    def preparer_ps2(cls):
        """Prépare la source PS2."""
        lecteur = cls.detecter_ps2_monte()
        if lecteur is not None:
            executable_lecteur = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(lecteur)
            executable_local = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(V.PS2_VERSION)
            version_lecteur = executable_lecteur.name.upper() if executable_lecteur is not None else None
            version_locale = executable_local.name.upper() if executable_local is not None else None
            copie_valide = cls.ps2_contient_donnees()
            if copie_valide and version_lecteur == version_locale:
                print('[SCAN JEU PS2] Le disque monte correspond deja a la copie locale :', version_locale)
                return True
            if copie_valide:
                print("[SCAN JEU PS2] Changement d'edition detecte :", version_locale, '->', version_lecteur)
            try:
                cls.copier_ps2_depuis_lecteur(lecteur)
            except Exception as erreur:
                print('[ERREUR PS2]', erreur)
                return False
            if cls.ps2_contient_donnees():
                executable_local = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(V.PS2_VERSION)
                print()
                print('[SCAN JEU PS2] Jeu PS2 pret pour la conversion :', executable_local.name if executable_local is not None else 'version inconnue')
                return True
        if lecteur is None:
            try:
                chemin_monte = input('Dossier racine du disque PS2 monté (Entrée pour sélectionner une ISO) : ').strip().strip('"')
            except EOFError:
                chemin_monte = ''
            if chemin_monte:
                candidat = Path(chemin_monte)
                data = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(candidat, 'DATA')
                executable = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(candidat)
                if data is not None and data.is_dir() and (executable is not None):
                    print('[PS2] Disque monté sélectionné :', candidat)
                    try:
                        cls.copier_ps2_depuis_lecteur(candidat)
                    except (OSError, RuntimeError) as erreur:
                        print('[ERREUR PS2] Copie du disque monté :', erreur)
                    else:
                        if cls.ps2_contient_donnees():
                            return True
                else:
                    print('[PS2] Ce dossier ne contient pas DATA et un exécutable PS2.')
        if cls.ps2_contient_donnees():
            executable_local = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(V.PS2_VERSION)
            print()
            print('[SCAN JEU PS2] Aucun disque monte detecte.')
            print('[SCAN JEU PS2] Utilisation de la copie locale :', executable_local.name if executable_local is not None else 'version inconnue')
            return True
        print()
        print('[SCAN JEU PS2] Aucun jeu PS2 monte detecte.')
        print('[SCAN JEU PS2] Aucune copie locale disponible.')
        print()
        print('Vous pouvez selectionner directement une image ISO PS2.')
        iso = cls.demander_iso_ps2()
        if iso is None:
            print()
            print('=' * 70)
            print('AUCUN JEU PS2 DETECTE')
            print('=' * 70)
            print()
            print('Aucun disque PS2 monte et aucune ISO selectionnee.')
            print()
            print('Le programme continue sans source PS2.')
            return False
        print()
        print('[PS2 ISO] ISO selectionnee :')
        print(iso)
        try:
            with LSL_MCL_Lecteur_ISO9660.LSL_MCL_Lecteur_ISO9660(iso) as lecteur_iso:
                with cls._preparer_source(V.PS2_VERSION) as destination_iso:
                    destination_iso.mkdir()
                    version_iso = lecteur_iso.detecter_version_ps2()
                    if not version_iso:
                        print()
                        print('[PS2 ISO] Aucun executable PS2 connu détecté (SLES ou SLUS).')
                        return False
                    version_iso = version_iso.upper()
                    print()
                    print('[PS2 ISO] Version detectee :', version_iso)
                    data_iso = lecteur_iso.trouver('DATA')
                    if data_iso is None:
                        print()
                        print('[PS2 ISO] Dossier DATA introuvable.')
                        return False
                    executable_iso = lecteur_iso.trouver(version_iso)
                    if executable_iso is not None:
                        lecteur_iso.extraire_fichier(executable_iso, destination_iso / version_iso)
                    else:
                        print()
                        print('[PS2 ISO] Executable PS2 introuvable.')
                        return False
                    fichiers_racine = ('SYSTEM.CNF',) if version_iso == 'SLUS_209.56' else ('LARRY.INI', 'SYSTEM.CNF')
                    for nom_racine in fichiers_racine:
                        entree_racine = lecteur_iso.trouver(nom_racine)
                        if entree_racine is None:
                            print()
                            print('[PS2 ISO] Fichier racine requis introuvable :', nom_racine)
                            return False
                        lecteur_iso.extraire_fichier(entree_racine, destination_iso / nom_racine)
                        print('[PS2 ISO] Fichier racine extrait :', nom_racine)
                    destination_data = destination_iso / 'DATA'
                    print()
                    print('[PS2 ISO] Extraction DATA vers :')
                    print(destination_data)
                    lecteur_iso.extraire_dossier(data_iso, destination_data)
                    if not cls._ps2_valide(destination_iso):
                        print()
                        print("[PS2 ISO] La copie locale obtenue n'est pas valide.")
                        data_locale = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(destination_iso, 'DATA')
                        larry_ini = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(destination_iso, 'LARRY.INI')
                        system_cnf = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(destination_iso, 'SYSTEM.CNF')
                        executable_local = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(destination_iso)
                        print('[PS2 ISO] DATA       :', 'OK' if data_locale is not None else 'ABSENT')
                        print('[PS2 ISO] LARRY.INI  :', 'OK' if larry_ini is not None else 'ABSENT')
                        print('[PS2 ISO] SYSTEM.CNF :', 'OK' if system_cnf is not None else 'ABSENT')
                        print('[PS2 ISO] Executable :', executable_local.name if executable_local is not None else 'ABSENT')
                        nombre_jam = 0
                        if data_locale is not None and data_locale.is_dir():
                            nombre_jam = sum((1 for fichier in data_locale.rglob('*') if fichier.is_file() and fichier.suffix.lower() == '.jam'))
                        print('[PS2 ISO] JAM trouves :', nombre_jam)
                        return False
                    executable_local = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(destination_iso)
                    print()
                    print('=' * 70)
                    print('JEU PS2 PRET POUR LA CONVERSION')
                    print('=' * 70)
                    print()
                    print('Version :', executable_local.name if executable_local is not None else version_iso)
                    print('Source  : ISO non montee')
                    print('DATA    :', destination_data)
                    return True
        except Exception as erreur:
            print()
            print('=' * 70)
            print('ERREUR LECTURE ISO PS2')
            print('=' * 70)
            print()
            print('[PS2 ISO]', erreur)
            print()
            print('Le programme continue sans source PS2.')
            return False

    @classmethod
    def demander_iso_ps2(cls):
        """Ouvre une fenêtre Windows permettant de sélectionner une ISO PS2."""
        root = tk.Tk()
        try:
            root.withdraw()
            root.attributes('-topmost', True)
            fichier = filedialog.askopenfilename(title="Sélectionner l'ISO PS2 de Leisure Suit Larry", filetypes=[('Image disque ISO', '*.iso'), ('Tous les fichiers', '*.*')])
        finally:
            root.destroy()
        if not fichier:
            return None
        return Path(fichier)

    @classmethod
    def _ps2_valide(cls, racine):
        """Vérifie une racine PS2, y compris l’édition russe sans LARRY.INI."""
        data = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(racine, 'DATA')
        if data is None or not data.exists() or (not data.is_dir()):
            return False
        jams = any((f.is_file() and f.suffix.lower() == '.jam' for f in data.rglob('*')))
        executable = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(racine)
        edition = executable.name.upper() if executable is not None else None
        fichiers_racine_requis = [LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(racine, 'SYSTEM.CNF'), executable]
        if edition != 'SLUS_209.56':
            fichiers_racine_requis.append(LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(racine, 'LARRY.INI'))
        return jams and all((fichier is not None and fichier.exists() and fichier.is_file() for fichier in fichiers_racine_requis))

    @staticmethod
    @contextmanager
    def _preparer_source(destination):
        """Prépare et valide une source PS2 avant remplacement, avec retour arrière."""
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        preparation = Path(tempfile.mkdtemp(prefix='.ps2_', dir=destination.parent))
        nouveau, ancien = (preparation / 'nouveau', preparation / 'ancien')
        conserver = False
        try:
            yield nouveau
            if not SourcePs2._ps2_valide(nouveau):
                raise RuntimeError('Source PS2 préparée incomplète ; copie locale conservée.')
            if destination.exists():
                destination.rename(ancien)
            try:
                nouveau.rename(destination)
            except OSError:
                if ancien.exists():
                    try:
                        ancien.rename(destination)
                    except OSError as erreur:
                        conserver = True
                        print('[PS2 RECUPERATION] Ancienne source conservée :', ancien)
                        print(erreur)
                raise
        finally:
            if not conserver:
                try:
                    shutil.rmtree(preparation)
                except OSError as erreur:
                    print('[PS2 NETTOYAGE] Dossier temporaire conservé :', preparation)
                    print(erreur)
