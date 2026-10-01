"""Service de construction d'une version localisée du jeu."""
from pathlib import Path
import LSL_MCL_VARIABLES as V
import LSL_MCL_ACX
import LSL_MCL_ANALISES
import LSL_MCL_AUDIOS
import LSL_MCL_BASE64
import LSL_MCL_COMPUTER
import LSL_MCL_EXTRACTIONS
import LSL_MCL_GEOMETRIES
import LSL_MCL_MENU
import LSL_MCL_OUTILS
import LSL_MCL_REFERENCES_TECHNICS
import LSL_MCL_TEXTES
import LSL_MCL_VIDEOS
from LSL_MCL_INJECTIONS import LSL_MCL_Injection
from LSL_MCL_MODE import LSL_MCL_Mode

class ServiceConstruction:
    """Coordonne les étapes d'installation à partir de la version PC."""

    @staticmethod
    def construire_version_fr(game_root, langue_cible='fr'):
        """Construit puis installe la version localisée ; une erreur bloquante interrompt le build avant publication."""
        langue_cible = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible)
        V.LANGUE_CIBLE = langue_cible
        import LSL_MCL_LANGUAGES_OTHERS
        autre = LSL_MCL_LANGUAGES_OTHERS.LSL_MCL_Languages_others
        if langue_cible.lower() not in ('fr', 'en', 'de', 'es', 'it', 'ru'):
            return autre.construire_version(game_root, langue_cible)
        LSL_MCL_MENU.LSL_MCL_Menu.titre('CONSTRUCTION DE LA VERSION LOCALISEE - ' + V.PROFILS_LANGUES.get(langue_cible, V.PROFILS_LANGUES['fr'])['nom'].upper())
        if V.ACTIVE_TRADUCTION_TEXTE_JAM:
            source_propre = LSL_MCL_OUTILS.LSL_MCL_Outils.obtenir_source_pc_construction(game_root)
        else:
            source_propre = LSL_MCL_OUTILS.LSL_MCL_Outils.obtenir_source_pc_geometrie()
        if source_propre is None:
            raise RuntimeError('Aucune source PC valide : PC_VERSION_BACKUP, PC_VERSION et jeu PC absents.')
        if langue_cible.lower() == 'ru' and V.ACTIVE_TRADUCTION_TEXTE_JAM:
            from LSL_MCL_JAMS_RU import ConstructionJamsRusses
            source_propre = ConstructionJamsRusses.choisir_source_pc(game_root, source_propre)
        temp_data = V.PC_VERSION_EDIT_TEMPS / 'Data'
        final_data = V.PC_VERSION_EDIT_FINI / 'Data'
        if Path(source_propre).resolve() == temp_data.resolve():
            print('[1/8] Réutilisation des JAM modifiés dans TEMP ; aucune copie.')
        else:
            LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(V.PC_VERSION_EDIT_TEMPS)
            V.PC_VERSION_EDIT_TEMPS.mkdir(parents=True, exist_ok=True)
            print('[1/8] Copie de la source sélectionnée vers TEMP :', source_propre)
            LSL_MCL_OUTILS.LSL_MCL_Outils.copier_arbre_avec_progression(source_propre, temp_data, 'CHARGEMENT PC')
        ServiceConstruction._traiter_images(temp_data, langue_cible)
        ServiceConstruction._traiter_textes_et_geometrie(temp_data, langue_cible)
        LSL_MCL_Mode.debloquer_option(temp_data)
        ServiceConstruction._traiter_audio(temp_data, langue_cible)
        ServiceConstruction._traiter_video(temp_data, langue_cible)
        if V.ACTIVE_REFERENCES_TECHNIQUES:
            LSL_MCL_REFERENCES_TECHNICS.LSL_MCL_References_technics.verifier_references_techniques(V.PC_VERSION_BACKUP / 'Data', temp_data)
        print('[8/8] Creation du dossier final...')
        LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(V.PC_VERSION_EDIT_FINI)
        V.PC_VERSION_EDIT_FINI.mkdir(parents=True, exist_ok=True)
        LSL_MCL_OUTILS.LSL_MCL_Outils.copier_arbre_avec_progression(
            temp_data, final_data, 'COMPILATION FINALE')
        marqueur = LSL_MCL_ANALISES.LSL_MCL_Analises.ecrire_marqueur_localisation_pc(
            final_data, langue_cible)
        print('[LOCALISATION] Marqueur créé :', marqueur)
        print('[COMPILATION] Langue :', langue_cible.upper())
        print('[COMPILATION] Source PC :', source_propre)
        print('[COMPILATION] Source PS2 :', V.PS2_VERSION / 'Data')
        print('[COMPILATION] Sortie :', final_data)
        LSL_MCL_MENU.LSL_MCL_Menu.titre('VERSION ' + langue_cible.upper() + ' PRETE')
        print('Le Dossier final :')
        print(final_data)
        print('Va etre Copier dans : ')
        print(game_root)
        print()
        print('Fermeture du jeu : Larry Leisure Suite : Magna Cum Laude')
        LSL_MCL_COMPUTER.LSL_MCL_Computer.fermer_larry()
        print(V.PC_VERSION_EDIT_FINI)
        print('\ndans :')
        print(game_root)
        data_final = V.PC_VERSION_EDIT_FINI / 'Data'
        data_version = Path(game_root) / 'Data'
        if not data_final.exists():
            raise RuntimeError('Le dossier Data final est introuvable.')
        print()
        print('[INSTALLATION PC] Copie de la version localisee...')
        LSL_MCL_OUTILS.LSL_MCL_Outils.copier_dossier(data_final, data_version)
        print('[INSTALLATION PC] Version localisee installee :')
        print(data_version)
        print()
        print("En cas d'erreur au lancement du jeu :")
        print('restaurez PC_VERSION_BACKUP\\Data ou utilisez la verification / reinstallation PC.')

    @staticmethod
    def _traiter_images(temp_data, langue_cible):
        """Extrait et injecte les images conformément aux options actives."""
        if V.ACTIVE_IMAGE_EXTRACTION and (not V.MANIFEST.exists()):
            print('[2/8] Manifest images...')
            LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.extraire_images()
        elif V.ACTIVE_IMAGE_EXTRACTION:
            print('[2/8] Manifest images deja present.')
        else:
            print('[2/8] Extraction des images desactivee.')
        if V.ACTIVE_IMAGE_EXTRACTION:
            print("[3/8] Generation de l'image Sierra " + langue_cible.upper() + '...')
            LSL_MCL_BASE64.LSL_MCL_Base64.generer_ecran_sierra_localise(langue_cible)
            print('[3/8] Injection des images modifiees...')
            LSL_MCL_Injection.injecter_images(temp_data)
            print("[3/8] Verification de l'ecran Sierra " + langue_cible.upper() + '...')
            LSL_MCL_Injection.injecter_ecran_sierra_localise(temp_data, langue_cible)
        else:
            print('[3/8] Traitement des images desactive pour les tests.')

    @staticmethod
    def _traduire_textes(temp_data, langue_cible):
        """Utilise le constructeur PS2, RU ou catalogue adapté à la langue."""
        langue_cible = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible)
        V.LANGUE_CIBLE = langue_cible
        if V.ACTIVE_TRADUCTION_TEXTE_JAM:
            print('[4/8] Traduction JAM PC <- PS2_VERSION ' + langue_cible.upper() + '...')
            if langue_cible.lower() == 'ru':
                from LSL_MCL_JAMS_RU import ConstructionJamsRusses
                fichiers, chaines, erreurs = ConstructionJamsRusses.construire(temp_data, V.PS2_VERSION / 'Data', temp_data)
                print(f'[RU] {fichiers} JAM, {chaines} chaînes')
                if erreurs:
                    raise RuntimeError(f'JAM RU : {erreurs} erreur(s) ; voir les logs console.')
            elif langue_cible in V.PROFILS_LANGUES:
                LSL_MCL_TEXTES.LSL_MCL_Textes.traduire_tous_jam_localises(temp_data, langue_cible)
                LSL_MCL_TEXTES.LSL_MCL_Textes.finaliser_textes_pc_specifiques(temp_data, langue_cible)
            else:
                from LSL_MCL_LANGUAGES_OTHERS import LSL_MCL_Languages_others
                catalogue = LSL_MCL_Languages_others.synchroniser(
                    temp_data / 'JamFiles' / 'PC', code=langue_cible)
                LSL_MCL_Languages_others.appliquer(temp_data, catalogue)
        else:
            print('[4/8] Traduction et adaptations des textes JAM ignorées : textes de la source sélectionnée conservés.')

    @staticmethod
    def _traiter_textes_et_geometrie(temp_data, langue_cible):
        """Traduit les textes puis applique le profil géométrique."""
        ServiceConstruction._traduire_textes(temp_data, langue_cible)
        LSL_MCL_TEXTES.LSL_MCL_Textes.corriger_format_date_sauvegarde(temp_data, langue_cible)
        if V.ACTIVE_GEOMETRIE:
            print('[GEOMETRIE] Application du profil', langue_cible.upper())
            LSL_MCL_GEOMETRIES.LSL_MCL_Geometries.patch_geometrie_v3(temp_data, langue_cible)
        else:
            print('[GEOMETRIE] Désactivée : rectangles et polices PC conservés.')

    @staticmethod
    def _traiter_audio(temp_data, langue_cible):
        """Localise les pistes audio AFS, ADX et JAM2/ACX."""
        if V.ACTIVE_AUDIO_BUILD:
            print('[5/8] Audio gameplay...')
            try:
                if langue_cible.lower() == 'ru':
                    from LSL_MCL_AUDIOS_RU import LSL_MCL_Audios_RU
                    LSL_MCL_Audios_RU.localiser_afs_gameplay(temp_data, langue_cible)
                else:
                    LSL_MCL_AUDIOS.LSL_MCL_Audios.localiser_afs_gameplay(temp_data, langue_cible)
            except Exception as erreur:
                print('[AFS ERREUR]', erreur)
                raise
            print('[6/8] ADX global...')
            try:
                LSL_MCL_AUDIOS.LSL_MCL_Audios.localiser_adx_afs(temp_data, langue_cible)
            except Exception as erreur:
                print('[ADX ERREUR]', erreur)
                raise
            print('[6/8] Restauration des 32 voix absentes du PC...')
            LSL_MCL_AUDIOS.LSL_MCL_Audios.restaurer_32_voix(temp_data, langue_cible)
            print('[6/8] Audio JAM2/ACX ' + langue_cible.upper() + '...')
            try:
                LSL_MCL_ACX.LSL_MCL_Acx.localiser_audio_jam2_acx_multilangue(temp_data, langue_cible)
            except Exception as erreur:
                print('[JAM2/ACX ERREUR]', erreur)
                raise
            LSL_MCL_AUDIOS.LSL_MCL_Audios.synchroniser_durees_aos(temp_data, langue_cible)
        else:
            print('[5/8] Audio gameplay... IGNORE')
            print('[AUDIO] Désactivé pour accélérer les tests géométriques.')
            print('[6/8] ADX global... IGNORE')
            print('[ADX] Désactivé pour accélérer les tests géométriques.')

    @staticmethod
    def _traiter_video(temp_data, langue_cible):
        """Localise les cinématiques lorsque cette option est activée."""
        print('[7/8] Cinematiques...')
        if V.ACTIVE_VIDEO_ENCODAGE:
            try:
                LSL_MCL_VIDEOS.LSL_MCL_Videos.localiser_cinema(temp_data, langue_cible)
            except Exception as erreur:
                print('[CINEMA ERREUR]', erreur)
                raise
        else:
            print('[CINEMA] Traitement ignore pour accelerer les tests.')
            print('[CINEMA] Les videos PC originales sont conservees.')

    @staticmethod
    def _copier_et_publier(source, destination, etape, langue_cible=None):
        """Conserve le raccord des langues libres avec la copie directe de OLD GOOD."""
        source, destination = Path(source), Path(destination)
        if destination.exists():
            LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        LSL_MCL_OUTILS.LSL_MCL_Outils.copier_arbre_avec_progression(
            source, destination, etape)
        if langue_cible is not None:
            return LSL_MCL_ANALISES.LSL_MCL_Analises.ecrire_marqueur_localisation_pc(
                destination, langue_cible)
