"""Traitements d'injection : localisation."""
import LSL_MCL_VARIABLES as V
import LSL_MCL_BASE64
import LSL_MCL_EXTRACTIONS
import LSL_MCL_LANGUAGES
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES
from LSL_MCL_INJECTION_IMAGES import InjectionImages

class InjectionLocalisation:
    """Services d'injection localisation."""

    @staticmethod
    def injecter_langue_ps2(game_root=None):
        """Reconstruit une copie PC propre, puis applique les images et textes de la langue."""
        if not V.ACTIVE_TRADUCTION_TEXTE_JAM:
            print('[TRADUCTION JAM] Désactivée : option de traduction ignorée.')
            return False
        source_propre = LSL_MCL_OUTILS.LSL_MCL_Outils.obtenir_source_pc_construction(game_root)
        if source_propre is None:
            print('[TRADUCTION] Aucune source PC originale disponible.')
            return False
        langue_cible = LSL_MCL_LANGUAGES.LSL_MCL_Languages.demander_langue_localisation()
        if langue_cible is None:
            print('[TRADUCTION] Operation annulee.')
            return False
        from LSL_MCL_CONSTRUCTION import ServiceConstruction
        if langue_cible == 'ru':
            from LSL_MCL_JAMS_RU import ConstructionJamsRusses
            source_propre = ConstructionJamsRusses.choisir_source_pc(
                game_root, source_propre)
        LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(V.PC_VERSION_EDIT_TEMPS)
        V.PC_VERSION_EDIT_TEMPS.mkdir(parents=True, exist_ok=True)
        data_root = V.PC_VERSION_EDIT_TEMPS / 'Data'
        print("[TRADUCTION] Reconstruction d'un TEMP propre depuis :", source_propre)
        LSL_MCL_OUTILS.LSL_MCL_Outils.copier_arbre_avec_progression(
            source_propre, data_root, 'CHARGEMENT PC')
        if V.ACTIVE_IMAGE_EXTRACTION:
            if not V.MANIFEST.exists():
                LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.extraire_images()
            if LSL_MCL_BASE64.LSL_MCL_Base64.generer_ecran_sierra_localise(langue_cible):
                InjectionImages.injecter_images(data_root)
                InjectionImages.injecter_ecran_sierra_localise(data_root, langue_cible)
        else:
            print('[IMAGES] Traitement automatique désactivé.')
        ServiceConstruction._traduire_textes(data_root, langue_cible)
        LSL_MCL_TEXTES.LSL_MCL_Textes.corriger_format_date_sauvegarde(
            data_root, langue_cible)
        print('[TRADUCTION] Version modifiee :', data_root)
        return True

    @staticmethod
    def injecter_images_depuis_menu():
        """Prépare une copie de travail depuis le backup et y injecte les images modifiées."""
        temp_data = V.PC_VERSION_EDIT_TEMPS / 'Data'
        source_data = V.PC_VERSION_BACKUP / 'Data'
        if not source_data.exists():
            print('[IMAGES] Backup PC absent.')
            return
        if not temp_data.exists():
            print("[IMAGES] Creation d'une copie TEMP...")
            LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(V.PC_VERSION_EDIT_TEMPS)
            V.PC_VERSION_EDIT_TEMPS.mkdir(parents=True, exist_ok=True)
            LSL_MCL_OUTILS.LSL_MCL_Outils.copier_arbre_avec_progression(
                source_data, temp_data, 'CHARGEMENT PC')
        InjectionImages.injecter_images(temp_data)
        print()
        print('[IMAGES] Injection terminee dans :')
        print(temp_data)
