"""Contrôleur des actions de la console et du mode automatique."""
from pathlib import Path
import LSL_MCL_VARIABLES as V

class ControleurMenu:
    """Interprète un choix de menu et coordonne les services métier."""

    def __init__(self, vue):
        """Associe la vue console au contrôleur."""
        self.vue = vue
        self.game_root = None
        self.ps2_ok = False

    def executer(self, game_root, ps2_ok):
        """Conserve la boucle du menu et la sortie après un build automatique."""
        self.game_root = game_root
        self.ps2_ok = ps2_ok
        automatique = not V.ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD
        actions = self.actions()
        while True:
            if automatique:
                self.vue.titre('BUILD AUTOMATIQUE')
                self.vue.log('[AUTO] Menu utilisateur désactivé.')
                self.vue.log('[AUTO] Choix automatique : [1]')
                choix = '1'
            else:
                self.vue.afficher_menu()
                choix = self.vue.demander_choix()
            choix = choix.strip()
            resultat = False
            if choix == '0':
                self.vue.log("Fermeture de l'utilitaire.")
                break
            if choix not in actions:
                self.vue.log('Choix invalide.')
            else:
                resultat = actions[choix]()
            if automatique:
                self.vue.titre('BUILD AUTOMATIQUE TERMINE' if resultat is True else 'BUILD AUTOMATIQUE INTERROMPU')
                break
            self.vue.attendre_retour()

    def actions(self):
        """Associe chaque numéro visible à une action du contrôleur."""
        return {'1': self.construire, '2': self.extraire_images, '3': self.injecter_images, '4': self.verifier_sources, '5': self.injecter_langue, '6': self.diagnostic_complet, '7': self.diagnostic_audio_video, '8': self.diagnostic_texte, '9': self.diagnostic_menu, '10': self.restaurer, '11': self.injecter_version_finale, '12': self.guide_geometrie}

    def assurer_ps2(self):
        """Prépare la source PS2 à la demande et mémorise son état."""
        if not self.ps2_ok:
            from LSL_MCL_EXTRACTIONS import LSL_MCL_Extractions
            self.ps2_ok = LSL_MCL_Extractions.preparer_ps2()
        return self.ps2_ok

    def construire(self):
        """Sélectionne la langue et construit la version ; renvoie False si une source manque ou si le choix est annulé."""
        from LSL_MCL_LANGUAGES import LSL_MCL_Languages
        from LSL_MCL_INJECTIONS import LSL_MCL_Injection
        from LSL_MCL_LANGUAGES_OTHERS import LSL_MCL_Languages_others
        if not self.assurer_pc():
            return False
        automatique = not V.ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD
        besoin_ps2 = any((V.ACTIVE_TRADUCTION_TEXTE_JAM, V.ACTIVE_IMAGE_EXTRACTION, V.ACTIVE_AUDIO_BUILD, V.ACTIVE_VIDEO_ENCODAGE))
        if besoin_ps2 and (not self.assurer_ps2()):
            self.vue.log('Source PS2_VERSION requise.')
            if automatique:
                self.vue.log('[AUTO] Build interrompu : source PS2_VERSION absente.')
            return False
        langue = LSL_MCL_Languages.demander_langue_localisation() if besoin_ps2 else LSL_MCL_Languages._menu_langues_complet({})
        if langue is None:
            if automatique:
                self.vue.log('[AUTO] Build interrompu : aucune langue sélectionnée.')
            return False
        if langue in ('fr', 'en', 'de', 'es', 'it', 'ru'):
            LSL_MCL_Injection.construire_version_fr(self.game_root, langue)
        else:
            self.vue.log('[CONSTRUCTION] Constructeur AUTRE LANGUE : ' + langue.upper())
            LSL_MCL_Languages_others.construire_version(self.game_root, langue)
        return True

    def extraire_images(self):
        """Lance l'extraction des images PC."""
        from LSL_MCL_EXTRACTIONS import LSL_MCL_Extractions
        LSL_MCL_Extractions.extraire_images()

    def injecter_images(self):
        """Lance l'injection d'images demandée dans le menu."""
        from LSL_MCL_INJECTIONS import LSL_MCL_Injection
        LSL_MCL_Injection.injecter_images_depuis_menu()

    def verifier_sources(self):
        """Contrôle les outils et les installations PC et PS2."""
        from LSL_MCL_OUTILS import LSL_MCL_Outils
        from LSL_MCL_COMPUTER import LSL_MCL_Computer
        LSL_MCL_Outils.verifier_outils()
        self.vue.log('\nVerification des sources...')
        jeu = LSL_MCL_Computer.detecter_jeu()
        self.game_root = jeu
        self.vue.log(f'[PC] Jeu PC : {jeu}' if jeu else '[PC] Jeu PC introuvable.')
        backup = V.PC_VERSION_BACKUP / 'Data'
        self.vue.log('[PC] Backup : ' + ('OK' if backup.exists() else 'ABSENT'))
        self.ps2_ok = False
        self.assurer_ps2()
        self.vue.log('[SCAN JEU PS2_VERSION] Source : ' + ('OK' if self.ps2_ok else 'ABSENTE'))

    def injecter_langue(self):
        """Exécute l'injection PS2 optionnelle si la source existe."""
        from LSL_MCL_MENU import LSL_MCL_Menu
        if not self.assurer_pc():
            return False
        if not self.assurer_ps2():
            self.vue.log('Source PS2_VERSION requise.')
            return
        if not LSL_MCL_Menu.executer_fonction_optionnelle('injecter_langue_ps2', self.game_root):
            self.vue.log("Utilisez temporairement l'option 1 pour construire la version francaise.")

    def diagnostic_complet(self):
        """Diagnostique les sources disponibles, même si une seule existe."""
        from LSL_MCL_COMPUTER import LSL_MCL_Computer
        from LSL_MCL_DIAGNOSTICS import LSL_MCL_Diagnostics
        if self.game_root is None or not Path(self.game_root).exists():
            self.game_root = LSL_MCL_Computer.detecter_jeu()
        pc = self.game_root and (Path(self.game_root) / 'Data').exists()
        ps2 = (V.PS2_VERSION / 'Data').exists()
        self.vue.log('[DIAGNOSTIC] Jeu PC : ' + ('DETECTE' if pc else 'ABSENT'))
        self.vue.log('[DIAGNOSTIC] Source PS2_VERSION : ' + ('DETECTEE' if ps2 else 'ABSENTE'))
        if not pc and (not ps2):
            self.vue.log('[DIAGNOSTIC] Impossible de continuer : aucune source PC ou PS2_VERSION disponible.')
            return
        LSL_MCL_Diagnostics.diagnostiquer_jeu_complet(self.game_root)

    def _diagnostic_depuis_data(self, nom):
        """Résout la source Data et lance le diagnostic choisi."""
        from LSL_MCL_OUTILS import LSL_MCL_Outils
        from LSL_MCL_MENU import LSL_MCL_Menu
        racine = LSL_MCL_Outils.obtenir_data_de_travail()
        if racine is None:
            self.vue.log('[DIAGNOSTIC] Aucune source Data.')
            return
        LSL_MCL_Menu.executer_fonction_optionnelle(nom, racine)

    def diagnostic_audio_video(self):
        """Lance le diagnostic audio et vidéo."""
        self._diagnostic_depuis_data('diagnostiquer_videos_audio')

    def diagnostic_texte(self):
        """Contrôle les deux sources requises avant le diagnostic texte."""
        from LSL_MCL_MENU import LSL_MCL_Menu
        racine = V.PC_VERSION_BACKUP / 'Data'
        if not racine.exists():
            self.vue.log('[DIAGNOSTIC TEXTES] Backup PC original absent.')
            return
        if not (V.PS2_VERSION / 'Data').exists():
            self.vue.log('[DIAGNOSTIC TEXTES] Source PS2_VERSION absente.')
            return
        LSL_MCL_Menu.executer_fonction_optionnelle('diagnostiquer_textes_jam', racine)

    def diagnostic_menu(self):
        """Lance le diagnostic des menus et des interfaces."""
        self._diagnostic_depuis_data('diagnostiquer_menus_interfaces')

    def restaurer(self):
        """Restaure la sauvegarde PC originale."""
        from LSL_MCL_BACKUP import LSL_MCL_Backup
        if not self.assurer_pc():
            return False
        LSL_MCL_Backup.restaurer_data_version_backup(self.game_root)

    def injecter_version_finale(self):
        """Copie la version éditée et terminée dans le jeu PC."""
        from LSL_MCL_INJECTIONS import LSL_MCL_Injection
        if not self.assurer_pc():
            return False
        self.vue.log('[11] Injection Version Edit')
        LSL_MCL_Injection.injecter_data_version_edit_fini(self.game_root)

    def guide_geometrie(self):
        """Produit le guide des réglages géométriques."""
        from LSL_MCL_GEOMETRIES import LSL_MCL_Geometries
        LSL_MCL_Geometries.generer_guide_geometrie()

    def assurer_pc(self):
        """Détecte et mémorise une installation PC valide avant une action sur le jeu."""
        from LSL_MCL_COMPUTER import LSL_MCL_Computer
        if self.game_root is None or not LSL_MCL_Computer._installation_pc_valide(self.game_root):
            self.game_root = LSL_MCL_Computer.detecter_jeu()
        if self.game_root is None or not LSL_MCL_Computer._installation_pc_valide(self.game_root):
            self.vue.log('[PC] Installation valide requise ; action interrompue.')
            return False
        return True
