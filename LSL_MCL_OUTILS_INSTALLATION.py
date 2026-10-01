"""Services InstallationOutils pour Larry MCL."""
from pathlib import Path
import sys
import json
import shutil
import subprocess
import hashlib
import urllib.request
import zipfile
import LSL_MCL_VARIABLES as V
from LSL_MCL_SUIVI import SuiviProgression

class InstallationOutils:
    """Services internes exposés par LSL_MCL_Outils."""

    @classmethod
    def installer_ffmpeg(cls):
        """Installe FFmpeg et FFprobe ensemble depuis le PATH ou leur archive Windows."""
        if not V.ACTIVE_TELECHARGEMENT_OUTILS:
            print('[OUTILS] Téléchargement désactivé : installer_ffmpeg ignoré.')
            return V.OUTILS / 'ffmpeg.exe' if (V.OUTILS / 'ffmpeg.exe').is_file() and (V.OUTILS / 'ffprobe.exe').is_file() else None
        V.OUTILS.mkdir(parents=True, exist_ok=True)
        destination_ffmpeg = V.OUTILS / 'ffmpeg.exe'
        destination_ffprobe = V.OUTILS / 'ffprobe.exe'
        if destination_ffmpeg.exists() and destination_ffprobe.exists():
            print('[OUTIL OK] ffmpeg.exe et ffprobe.exe')
            return destination_ffmpeg
        manquants = []
        if not destination_ffmpeg.exists():
            manquants.append('ffmpeg.exe')
        if not destination_ffprobe.exists():
            manquants.append('ffprobe.exe')
        systeme_ffmpeg = shutil.which('ffmpeg.exe') or shutil.which('ffmpeg')
        systeme_ffprobe = shutil.which('ffprobe.exe') or shutil.which('ffprobe')
        if systeme_ffmpeg and systeme_ffprobe:
            for source, cible in ((systeme_ffmpeg, destination_ffmpeg), (systeme_ffprobe, destination_ffprobe)):
                if not cible.exists():
                    shutil.copy2(source, cible)
            print('[OUTIL OK] FFmpeg et FFprobe copiés depuis le PATH')
            return destination_ffmpeg
        print('[OUTIL] Installation requise :', ', '.join(manquants))
        url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
        archive = V.ROOT / '_ffmpeg.zip'
        temp = V.ROOT / '_ffmpeg_temp'
        try:
            cls.telecharger(url, archive)
            cls.supprimer(temp)
            temp.mkdir(parents=True)
            cls._extraire_zip(archive, temp, 'FFMPEG EXTRACTION')
            candidats_ffmpeg = list(temp.rglob('ffmpeg.exe'))
            candidats_ffprobe = [f.parent / 'ffprobe.exe' for f in candidats_ffmpeg if (f.parent / 'ffprobe.exe').is_file()]
            if not candidats_ffmpeg:
                raise RuntimeError("ffmpeg.exe absent de l'archive.")
            if not candidats_ffprobe:
                raise RuntimeError("ffprobe.exe absent de l'archive.")
            shutil.copy2(candidats_ffprobe[0].parent / 'ffmpeg.exe', destination_ffmpeg)
            shutil.copy2(candidats_ffprobe[0], destination_ffprobe)
            print('[OUTILS INSTALLES]', destination_ffmpeg, 'et', destination_ffprobe)
            return destination_ffmpeg
        finally:
            cls.supprimer(archive)
            cls.supprimer(temp)

    @classmethod
    def installer_vgmstream(cls):
        """Installe le décodeur AHX vgmstream et les DLL de son archive Windows."""
        destination = V.OUTILS / 'vgmstream-cli.exe'
        if destination.is_file():
            print('[OUTIL OK] vgmstream-cli.exe')
            return destination
        systeme = shutil.which('vgmstream-cli.exe') or shutil.which('vgmstream-cli')
        if systeme:
            V.OUTILS.mkdir(parents=True, exist_ok=True)
            shutil.copy2(systeme, destination)
            print('[OUTIL OK] vgmstream-cli.exe copié depuis le PATH')
            return destination
        if not V.ACTIVE_TELECHARGEMENT_OUTILS:
            print('[OUTILS] Téléchargement désactivé : vgmstream-cli absent.')
            return None
        V.OUTILS.mkdir(parents=True, exist_ok=True)
        url = 'https://github.com/vgmstream/vgmstream-releases/releases/download/nightly/vgmstream-win64.zip'
        archive = V.ROOT / '_vgmstream.zip'
        temp = V.ROOT / '_vgmstream_temp'
        try:
            print('[OUTIL] Installation de vgmstream-cli (AHX 0x11)...')
            cls.telecharger(url, archive)
            cls.supprimer(temp)
            temp.mkdir(parents=True, exist_ok=True)
            cls._extraire_zip(archive, temp)
            candidats = list(temp.rglob('vgmstream-cli.exe'))
            if not candidats:
                raise RuntimeError("vgmstream-cli.exe absent de l'archive.")
            dossier_cli = candidats[0].parent
            for fichier in dossier_cli.iterdir():
                if fichier.is_file() and fichier.suffix.lower() in ('.exe', '.dll'):
                    shutil.copy2(fichier, V.OUTILS / fichier.name)
            if not destination.is_file():
                raise RuntimeError('Installation de vgmstream-cli incomplète.')
            print('[OUTILS INSTALLES]', destination)
            return destination
        finally:
            cls.supprimer(archive)
            cls.supprimer(temp)

    @classmethod
    def installer_cricodecs(cls):
        """Installe CriCodecs après vérification du SHA-256 de son archive."""
        if not V.ACTIVE_TELECHARGEMENT_OUTILS:
            print('[OUTILS] Téléchargement désactivé : installer_cricodecs ignoré.')
            return V.OUTILS / 'cricodecs.exe' if (V.OUTILS / 'cricodecs.exe').is_file() else None
        V.OUTILS.mkdir(parents=True, exist_ok=True)
        destination = V.OUTILS / 'cricodecs.exe'
        if destination.is_file():
            print('[OUTIL OK] cricodecs.exe :', destination)
            return destination
        version = '1.2.0'
        nom_archive = f'cricodecs-{version}-cli-windows-x86_64.zip'
        url = f'https://github.com/Youjose/CriCodecs/releases/download/v{version}/{nom_archive}'
        sha256_attendu = '1ddbf214bff6a357fb8a8861ef26f967eadc9279f6260ef41cbaa558170956d0'
        archive = V.ROOT / '_cricodecs.zip'
        provisoire = V.OUTILS / '_cricodecs.exe.tmp'
        print('[OUTIL] Installation de cricodecs.exe (CLI Windows)...')
        try:
            cls.telecharger(url, archive)
            sha256_obtenu = hashlib.sha256(archive.read_bytes()).hexdigest()
            if sha256_obtenu.lower() != sha256_attendu:
                raise RuntimeError("Empreinte SHA-256 de l'archive CriCodecs incorrecte.")
            with zipfile.ZipFile(archive) as contenu:
                candidats = [membre for membre in contenu.infolist() if not membre.is_dir() and Path(membre.filename.replace('\\', '/')).name.lower() == 'cricodecs.exe']
                if len(candidats) != 1:
                    raise RuntimeError("L'archive CriCodecs doit contenir un seul cricodecs.exe.")
                with contenu.open(candidats[0]) as source, provisoire.open('wb') as cible:
                    shutil.copyfileobj(source, cible)
            if provisoire.stat().st_size == 0:
                raise RuntimeError('cricodecs.exe extrait est vide.')
            provisoire.replace(destination)
            print('[OUTIL INSTALLE]', destination)
            return destination
        finally:
            cls.supprimer(provisoire)
            cls.supprimer(archive)

    @classmethod
    def installer_sfd_muxer(cls):
        """Installe le module SFD Muxer local et récupère son lanceur si disponible."""
        if not V.ACTIVE_TELECHARGEMENT_OUTILS:
            print('[OUTILS] Téléchargement désactivé : installer_sfd_muxer ignoré.')
            fichier = V.OUTILS / 'sfd-muxer.exe'
            return fichier if fichier.is_file() else None
        V.OUTILS.mkdir(parents=True, exist_ok=True)
        exe_local = V.OUTILS / 'sfd-muxer.exe'
        module_local = V.VENDOR / 'sfd_muxer'
        if exe_local.exists() and module_local.exists():
            print('[OUTIL OK] sfd-muxer local :', exe_local)
            return exe_local
        print('[OUTIL] Installation locale de SFD Muxer...')
        cls.installer_module_local('sfd-muxer')
        scripts = Path(sys.executable).parent / 'Scripts'
        candidats = list(scripts.glob('sfd-muxer*.exe')) + list(scripts.glob('sfd_muxer*.exe'))
        if candidats:
            shutil.copy2(candidats[0], exe_local)
            print('[OUTIL INSTALLE]', exe_local)
            return exe_local
        print('[SFD] Module Python local installe :', module_local)
        return module_local


    @staticmethod
    def installer_module_local(module_pip):
        """Installe un paquet dans VENDOR et rend ce dossier importable."""
        if not V.ACTIVE_TELECHARGEMENT_OUTILS:
            raise RuntimeError('Téléchargement désactivé : installer_module_local')
        V.VENDOR.mkdir(parents=True, exist_ok=True)
        print('[PYTHON LOCAL]', module_pip)
        commande_pip = [sys.executable, '-m', 'pip', 'install', '--upgrade', '--target', str(V.VENDOR), module_pip]
        resultat = subprocess.run(commande_pip)
        if resultat.returncode != 0:
            raise RuntimeError(f'Installation locale impossible : {module_pip}')
        if str(V.VENDOR) not in sys.path:
            sys.path.insert(0, str(V.VENDOR))
        return True

    @classmethod
    def verifier_outils(cls):
        """Affiche les outils disponibles et les liens d’installation."""
        import LSL_MCL_MENU
        LSL_MCL_MENU.LSL_MCL_Menu.titre('VERIFICATION')
        print('ffmpeg :', cls.outil('ffmpeg.exe') or cls.outil('ffmpeg') or 'ABSENT')
        print('ffprobe :', cls.outil('ffprobe.exe') or cls.outil('ffprobe') or 'ABSENT')
        print('CriCodecs :', cls.outil('cricodecs.exe') or 'ABSENT')
        print('vgmstream :', cls.outil('vgmstream-cli.exe') or 'ABSENT')
        print('sfd-muxer :', cls.outil('sfd-muxer.exe') or cls.outil('sfd-muxer') or 'ABSENT')
        print('AFS : moteur interne Python')
        print()
        print('FFmpeg : https://ffmpeg.org/download.html')
        print('sfd-muxer : https://pypi.org/project/sfd-muxer/')

    @classmethod
    def assurer_outils(cls):
        """Prépare les outils nécessaires et journalise chaque installation en échec."""
        import LSL_MCL_MENU
        if not V.ACTIVE_TELECHARGEMENT_OUTILS:
            print('[OUTILS] Téléchargements automatiques désactivés.')
            return {}
        LSL_MCL_MENU.LSL_MCL_Menu.titre('VERIFICATION DES OUTILS')
        installations = []
        if V.ACTIVE_AUDIO_BUILD or V.ACTIVE_VIDEO_ENCODAGE:
            installations.append(('ffmpeg', cls.installer_ffmpeg))
        if V.ACTIVE_AUDIO_BUILD:
            installations.extend((('cricodecs', cls.installer_cricodecs),
                                  ('vgmstream', cls.installer_vgmstream)))
        if V.ACTIVE_VIDEO_ENCODAGE:
            installations.append(('sfd', cls.installer_sfd_muxer))
        outils = {}
        for nom, installer in installations:
            try:
                outils[nom] = installer()
            except Exception as erreur:
                print('[ERREUR OUTIL]', nom, ':', erreur)
                outils[nom] = None
        if not installations:
            print('[OUTILS] Audio et cinéma désactivés : aucune installation externe.')
        return outils

    @staticmethod
    def _extraire_zip(archive, destination, libelle=None):
        """Valide tous les chemins ZIP avant extraction et affiche la progression demandée."""
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        racine = destination.resolve()
        with zipfile.ZipFile(archive) as contenu:
            membres = contenu.infolist()
            for membre in membres:
                nom = membre.filename.replace('\\', '/')
                if ':' in nom or not (racine / nom).resolve().is_relative_to(racine):
                    raise RuntimeError(f'Chemin dangereux dans l’archive : {membre.filename}')
            suivi = SuiviProgression(libelle, len(membres)) if libelle else None
            for numero, membre in enumerate(membres, 1):
                contenu.extract(membre, destination)
                if suivi:
                    suivi.avancer(numero, Path(membre.filename).name)
            if suivi:
                suivi.terminer()
