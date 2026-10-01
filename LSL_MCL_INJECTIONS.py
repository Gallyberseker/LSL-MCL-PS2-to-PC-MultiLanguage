"""Interface des services d'injection de Larry MCL."""
from pathlib import Path
from LSL_MCL_INJECTION_JAM import InjectionJam
from LSL_MCL_INJECTION_IMAGES import InjectionImages
from LSL_MCL_INJECTION_LOCALISATION import InjectionLocalisation


class LSL_MCL_Injection(InjectionJam, InjectionImages, InjectionLocalisation):
    """Expose les injections de ressources et le déploiement de la version PC."""

    @staticmethod
    def construire_version_fr(game_root, langue_cible='fr'):
        """Délègue la construction de la langue au service dédié."""
        from LSL_MCL_CONSTRUCTION import ServiceConstruction
        return ServiceConstruction.construire_version_fr(game_root, langue_cible)

    @staticmethod
    @staticmethod
    def injecter_data_version_edit_fini(game_root):
        """Injecte le Data final par copie directe après fermeture du jeu, comme OLD GOOD."""
        import shutil
        import LSL_MCL_VARIABLES as V
        import LSL_MCL_ANALISES
        import LSL_MCL_COMPUTER
        import LSL_MCL_MENU
        import LSL_MCL_OUTILS
        LSL_MCL_MENU.LSL_MCL_Menu.titre('INJECTION DATA PC VERSION EDIT FINI')
        LSL_MCL_COMPUTER.LSL_MCL_Computer.fermer_larry()
        source = V.PC_VERSION_EDIT_FINI / 'Data'
        destination = Path(game_root) / 'Data'
        if not source.exists():
            print('[INJECTION] PC_VERSION_EDIT_FINI\\Data introuvable :')
            print(source)
            return False
        print()
        print('[INJECTION] Source :')
        print(source)
        print()
        print('[INJECTION] Destination PC :')
        print(destination)
        print()
        print('[INJECTION] Suppression du Data PC actuel...')
        try:
            LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(destination)
        except PermissionError as erreur:
            print()
            print('[INJECTION IMPOSSIBLE]')
            print('Un fichier du jeu est encore utilise.')
            if erreur.filename:
                print('Fichier verrouille :')
                print(erreur.filename)
            return False
        except Exception as erreur:
            print()
            print('[ERREUR SUPPRESSION]')
            print(erreur)
            return False
        print()
        print('[INJECTION] Copie de PC_VERSION_EDIT_FINI\\Data...')
        try:
            shutil.copytree(source, destination)
            marqueur_localisation = LSL_MCL_ANALISES.LSL_MCL_Analises.ecrire_marqueur_localisation_pc(destination, V.LANGUE_CIBLE)
        except Exception as erreur:
            print()
            print('[ERREUR INJECTION]')
            print(erreur)
            return False
        print()
        print('[INJECTION OK]')
        print('PC_VERSION_EDIT_FINI\\Data a ete injecte dans le jeu PC.')
        return True
