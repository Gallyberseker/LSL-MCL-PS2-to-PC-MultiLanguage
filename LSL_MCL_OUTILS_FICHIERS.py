"""Services OperationsFichiers pour Larry MCL."""
from pathlib import Path
import os
import shutil
import stat
import LSL_MCL_VARIABLES as V
from LSL_MCL_SUIVI import SuiviProgression

class OperationsFichiers:
    """Services internes exposés par LSL_MCL_Outils."""

    @staticmethod
    def copier_arbre_avec_progression(source, destination, libelle='COPIE'):
        """Copie un arbre en affichant la progression par fichier."""
        source = Path(source)
        fichiers = sum((f.is_file() for f in source.rglob('*')))
        suivi = SuiviProgression(libelle, fichiers)
        compteur = 0

        def copie(source_fichier, destination_fichier):
            """Copie un fichier et actualise le nombre de fichiers terminés."""
            nonlocal compteur
            resultat = shutil.copy2(source_fichier, destination_fichier)
            compteur += 1
            suivi.avancer(compteur, Path(source_fichier).name)
            return resultat
        resultat = shutil.copytree(source, destination, copy_function=copie)
        suivi.terminer()
        return resultat

    @classmethod
    def copier_dossier(cls, source, destination):
        """Remplace le dossier puis copie à son emplacement définitif, comme OLD GOOD."""
        source, destination = Path(source), Path(destination)
        if destination.exists():
            cls.supprimer(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        return cls.copier_arbre_avec_progression(source, destination, 'INSTALLATION PC')

    @classmethod
    def migrer_dossier_legacy(cls, ancien, nouveau):
        """Migre un ancien dossier vers son emplacement actuel."""
        source = next((element for element in ancien.parent.iterdir() if element.name == ancien.name), None)
        if source is None or source.name == nouveau.name:
            return
        if source.name.lower() == nouveau.name.lower():
            temporaire = nouveau.parent / f'__RENOMMAGE_{nouveau.name}'
            cls.supprimer(temporaire)
            source.rename(temporaire)
            temporaire.rename(nouveau)
            return
        if not nouveau.exists():
            shutil.move(str(source), str(nouveau))
            return
        shutil.copytree(source, nouveau, dirs_exist_ok=True)
        cls.supprimer(source)

    @staticmethod
    def migrer_fichier_legacy(ancien, nouveau):
        """Déplace un ancien fichier si sa destination est absente."""
        if ancien.exists() and (not nouveau.exists()):
            nouveau.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(ancien), str(nouveau))

    @classmethod
    def creer_arborescence(cls):
        """Crée les dossiers du projet et migre les anciens emplacements."""
        import LSL_MCL_IMAGES
        cls.migrer_dossier_legacy(V.ROOT / 'Edit', V.EDIT)
        cls.migrer_dossier_legacy(V.ROOT / 'Outils', V.OUTILS)
        cls.migrer_dossier_legacy(V.ROOT / 'Rapports', V.RAPPORTS)
        dossiers = (V.PC_VERSION_BACKUP, V.PC_VERSION, V.PS2_VERSION, V.EDIT, V.IMAGE_EXTRACT, V.IMAGE_INJECT, V.PC_VERSION_EDIT_TEMPS, V.PC_VERSION_EDIT_FINI, V.OUTILS, V.RAPPORTS)
        for dossier in dossiers:
            dossier.mkdir(parents=True, exist_ok=True)
        LSL_MCL_IMAGES.LSL_MCL_Images.creer_dossiers_images(V.IMAGE_EXTRACT / 'IMG_PC_VERSION_BACKUP')
        LSL_MCL_IMAGES.LSL_MCL_Images.creer_dossiers_images(V.IMAGE_INJECT)
        cls.migrer_fichier_legacy(V.ROOT / 'config.json', V.CONFIG)
        outils_anciens = ((V.ROOT / 'ffmpeg.exe', V.OUTILS / 'ffmpeg.exe'), (V.ROOT / 'ffprobe.exe', V.OUTILS / 'ffprobe.exe'), (V.ROOT / 'sfd-muxer.exe', V.OUTILS / 'sfd-muxer.exe'), (V.ROOT / 'SFD_Muxer.exe', V.OUTILS / 'SFD_Muxer.exe'), (V.ROOT / 'AFSPacker.exe', V.OUTILS / 'AFSPacker.exe'), (V.ROOT / 'AFSPacker' / 'AFSPacker.exe', V.OUTILS / 'AFSPacker.exe'), (V.ROOT / 'SFD_Muxer_C' / 'SFD_Muxer.exe', V.OUTILS / 'SFD_Muxer.exe'))
        for ancien, nouveau in outils_anciens:
            cls.migrer_fichier_legacy(ancien, nouveau)
        ps2_data = V.PS2_VERSION / 'Data'
        dossiers_ps2 = ('Audio/CRI', 'JamFiles/PC', 'JamFiles/PC/Levels', 'Cinema/FMV', 'Cinema/FMV/Arcade', 'Cinema/FMV/Ingame', 'Cinema/FMV/Intro', 'Cinema/FMV/Misc', 'Cinema/FMV/Rath1', 'Cinema/FMV/Rath2', 'Cinema/FMV/TV')
        for relatif in dossiers_ps2:
            (ps2_data / relatif).mkdir(parents=True, exist_ok=True)
        readme = V.OUTILS / 'README_OUTILS.txt'
        if not readme.exists():
            readme.write_text("OUTILS CINEMATIQUES\n===================\n\nFFmpeg :\nhttps://ffmpeg.org/download.html\n\nsfd-muxer :\nhttps://pypi.org/project/sfd-muxer/\n\nPlacez ffmpeg.exe, ffprobe.exe et sfd-muxer.exe dans ce dossier.\n\nAFSPacker.exe n'est pas requis : le script integre son propre moteur AFS.\n", encoding='utf-8')

    @staticmethod
    def supprimer(path):
        """Supprime les copies locales en lecture seule ; ne suit pas les liens symboliques."""
        path = Path(path)
        if path.is_symlink():
            path.unlink()
        elif path.is_dir():

            def forcer_suppression(fonction, chemin, erreur):
                """Rend une copie locale accessible avant de réessayer sa suppression."""
                os.chmod(chemin, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
                fonction(chemin)
            shutil.rmtree(path, onerror=forcer_suppression)
        elif path.exists():
            try:
                os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass
            path.unlink()

    @staticmethod
    def trouver_fichier_ci(dossier, nom):
        """Recherche récursivement un nom de fichier sans distinguer la casse."""
        if not dossier.exists():
            return None
        nom = nom.lower()
        for fichier in dossier.rglob('*'):
            if fichier.is_file() and fichier.name.lower() == nom:
                return fichier
        return None
