"""Services SourcesPC pour Larry MCL."""
from pathlib import Path
import LSL_MCL_VARIABLES as V

class SourcesPC:
    """Services internes exposés par LSL_MCL_Outils."""

    @staticmethod
    def obtenir_data_de_travail():
        """Choisit les données finales, temporaires ou originales pour le diagnostic."""

        def contient_fichiers(chemin):
            """Indique si le dossier contient au moins un fichier, même dans un sous-dossier."""
            if not chemin.exists() or not chemin.is_dir():
                return False
            return next((fichier for fichier in chemin.rglob('*') if fichier.is_file()), None) is not None
        candidats = (V.PC_VERSION_EDIT_FINI / 'Data', V.PC_VERSION_EDIT_TEMPS / 'Data', V.PC_VERSION_BACKUP / 'Data')
        for chemin in candidats:
            if contient_fichiers(chemin):
                return chemin
        return None

    @staticmethod
    def obtenir_source_pc_construction(game_root):
        """Choisit une source PC contenant AppInit.JAM, en privilégiant le backup."""
        candidats = [('BACKUP ORIGINAL', V.PC_VERSION_BACKUP / 'Data'), ('COPIE PC_VERSION', V.PC_VERSION / 'Data')]
        if game_root is not None:
            try:
                candidats.append(('JEU PC INSTALLE', Path(game_root) / 'Data'))
            except Exception:
                pass
        for nom, chemin in candidats:
            appinit = chemin / 'JamFiles' / 'PC' / 'AppInit.JAM'
            if chemin.exists() and chemin.is_dir() and appinit.exists():
                print('[SOURCE PC]', nom, ':', chemin)
                if nom != 'BACKUP ORIGINAL':
                    print('[SOURCE PC ATTENTION] Backup absent : utilisation de', nom)
                return chemin
        print()
        print('[SOURCE PC] Aucune source Data valide.')
        for nom, chemin in candidats:
            print(' -', nom, ':', chemin, '=>', 'PRESENT' if chemin.exists() else 'ABSENT')
        return None

    @staticmethod
    def obtenir_source_pc_geometrie():
        """Sans traduction, conserve les éditions ou utilise PC_VERSION si vides.

        Une édition non vide mais incomplète bloque le build pour éviter de
        l'effacer en revenant par erreur aux JAM anglais de PC_VERSION.
        """
        for nom, data in (('PC_VERSION_EDIT_FINI', V.PC_VERSION_EDIT_FINI / 'Data'), ('PC_VERSION_EDIT_TEMPS', V.PC_VERSION_EDIT_TEMPS / 'Data')):
            jam = data / 'JamFiles' / 'PC'
            if (jam / 'AppInit.JAM').is_file() and (jam / 'AppInit.JAM').stat().st_size:
                print('[SOURCE GEOMETRIE]', nom, ':', data)
                return data
            if data.is_dir() and any(data.iterdir()):
                raise RuntimeError('[SOURCE GEOMETRIE] ' + nom + '/Data contient des fichiers mais AppInit.JAM est absent ou vide : construction arrêtée pour ne pas écraser cette version modifiée.')
            print('[SOURCE GEOMETRIE]', nom, 'vide ou absent :', data)
        base = V.PC_VERSION / 'Data'
        appinit = base / 'JamFiles' / 'PC' / 'AppInit.JAM'
        if appinit.is_file() and appinit.stat().st_size:
            print("[SOURCE GEOMETRIE] Dossiers d'édition vides ; repli sur PC_VERSION :", base)
            return base
        raise RuntimeError("[SOURCE GEOMETRIE] Dossiers d'édition vides et PC_VERSION/Data sans JAM valide : construction arrêtée.")

    @staticmethod
    def normaliser_chemin_jam(chemin):
        """Normalise un chemin JAM et retire les préfixes JamFiles et PC ou PS2."""
        morceaux = [morceau for morceau in str(chemin).replace('\\', '/').strip('/').lower().split('/') if morceau]
        if 'jamfiles' in morceaux:
            morceaux = morceaux[morceaux.index('jamfiles') + 1:]
        if morceaux and morceaux[0] in ('pc', 'ps2'):
            morceaux = morceaux[1:]
        return '/'.join(morceaux)
