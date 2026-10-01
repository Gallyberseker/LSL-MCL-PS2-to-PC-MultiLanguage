"""Fonctions du domaine MAIN pour Larry MCL."""
import sys
import LSL_MCL_VARIABLES as V

# Les modules image utilisent Pillow dès leur import.
if __name__ == "__main__":
    from LSL_MCL_CONSOLE_LOG import LSL_MCL_Console_log
    from LSL_MCL_DEPENDANCES import LSL_MCL_Dependances
    LSL_MCL_Console_log.activer_log_console()
    if not LSL_MCL_Dependances.verifier_pillow():
        raise SystemExit(1)

import LSL_MCL_BACKUP
import LSL_MCL_COMPUTER
import LSL_MCL_EXTRACTIONS
import LSL_MCL_IMAGES
import LSL_MCL_INJECTIONS
import LSL_MCL_MENU
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES
import LSL_MCL_CONSOLE_LOG
import LSL_MCL_LANGUAGES_OTHERS

class LSL_MCL_Main:
    """Coordonne l’initialisation, les commandes et le menu de localisation."""

    @staticmethod
    def initialiser():
        """Prépare les outils, la sauvegarde PC et les sources requises par les options actives."""
        LSL_MCL_MENU.LSL_MCL_Menu.logo()
        LSL_MCL_MENU.LSL_MCL_Menu.titre('          By  G A L L Y B E R S E K E R')
        LSL_MCL_MENU.LSL_MCL_Menu.titre('       Leisure Suit Larry MCL Translator')
        LSL_MCL_MENU.LSL_MCL_Menu.titre('     EN FR DE ES IT RU  PC ← PS2')
        LSL_MCL_OUTILS.LSL_MCL_Outils.creer_arborescence()
        if V.ACTIVE_TELECHARGEMENT_OUTILS:
            LSL_MCL_OUTILS.LSL_MCL_Outils.assurer_outils()
        else:
            print('[OUTILS] Téléchargement automatique désactivé ; exécutables présents conservés.')
        print('Detection du jeu PC...')
        game_root = LSL_MCL_COMPUTER.LSL_MCL_Computer.detecter_jeu()
        if game_root is None:
            print('Jeu PC introuvable.')
            return (None, False)
        print('Jeu detecte :')
        print(game_root)
        backup = LSL_MCL_BACKUP.LSL_MCL_Backup.backup_pc(game_root)
        if backup is None:
            print()
            print('[ARRET] Sauvegarde PC originale indisponible.')
            print('[ARRET] Data\\Larry_MCL_Localisation.txt detect.')
            print("Le programme s'arrete sans extraire ni modifier le jeu.")
            return (None, False)
        if V.ACTIVE_IMAGE_EXTRACTION and (not V.MANIFEST.exists()):
            print()
            print('> Premiere extraction des images...')
            LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.extraire_images()
        besoin_ps2 = V.ACTIVE_TRADUCTION_TEXTE_JAM or V.ACTIVE_IMAGE_EXTRACTION or V.ACTIVE_AUDIO_BUILD or V.ACTIVE_VIDEO_ENCODAGE
        ps2_ok = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.preparer_ps2() if besoin_ps2 else True
        if not besoin_ps2:
            print('[PS2] Source non requise : traitement des JAM PC uniquement.')
        if ps2_ok and V.ACTIVE_IMAGE_EXTRACTION:
            try:
                LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.extraire_images_ps2_version()
            except Exception as erreur:
                print("[IMAGES PS2] Erreur pendant l'extraction :", erreur)
        if not V.ACTIVE_IMAGE_EXTRACTION:
            print('[IMAGES] Extraction automatique désactivée.')
        return (game_root, ps2_ok)

    @staticmethod
    def main():
        """Initialise le projet puis exécute la commande demandée ou ouvre le menu."""
        game_root, ps2_ok = LSL_MCL_Main.initialiser()
        if game_root is None:
            return
        if '--extract' in sys.argv:
            LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.extraire_images()
            return
        if '--check' in sys.argv:
            LSL_MCL_OUTILS.LSL_MCL_Outils.verifier_outils()
            return
        if '--build' in sys.argv:
            langue_catalogue = LSL_MCL_LANGUAGES_OTHERS.LSL_MCL_Languages_others.langue()
            langue_cible = V.LANGUE_CIBLE if langue_catalogue == 'en' else langue_catalogue
            for argument in sys.argv:
                if argument.startswith('--langue='):
                    try:
                        langue_cible = LSL_MCL_LANGUAGES_OTHERS.LSL_MCL_Languages_others.normaliser_code(
                            argument.split('=', 1)[1])
                    except ValueError as erreur:
                        print('[CONSTRUCTION]', erreur)
                        return
            if ps2_ok or langue_cible not in ('fr', 'en', 'de', 'es', 'it', 'ru'):
                LSL_MCL_INJECTIONS.LSL_MCL_Injection.construire_version_fr(game_root, langue_cible)
            elif LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.preparer_ps2():
                LSL_MCL_INJECTIONS.LSL_MCL_Injection.construire_version_fr(game_root, langue_cible)
            else:
                print('[CONSTRUCTION] Source PS2 indisponible.')
            return
        if not ps2_ok:
            print()
            print("Veuillez monter l'image du jeu PS2_VERSION Leisure Suit Larry - Magna Cum Laude.iso")
            print('Puis relancez le script.')
            return
        LSL_MCL_MENU.LSL_MCL_Menu.menu(game_root, ps2_ok)

    @staticmethod
    def demarrer():
        """Active les logs, synchronise le catalogue comme OLD GOOD puis lance le moteur."""
        LSL_MCL_CONSOLE_LOG.LSL_MCL_Console_log.activer_log_console()
        if V.ACTIVE_TRADUCTION_TEXTE_JAM:
            LSL_MCL_LANGUAGES_OTHERS.LSL_MCL_Languages_others.synchroniser()
        LSL_MCL_Main.main()


if __name__ == "__main__":
    LSL_MCL_Main.demarrer()
