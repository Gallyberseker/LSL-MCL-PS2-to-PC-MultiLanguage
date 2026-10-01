"""Profil de langue IT et géométrie fixe pour Larry MCL."""
import LSL_MCL_VARIABLES as V


PROFIL_GEOMETRIE = {
    # IT [PROFIL IT] [ÉDITION SOURCE PS2] identifiant de la version utilisée pour les valeurs de ce profil
    'edition': 'SLES_526.42',

    # IT ===== MENU DÉMARRER =====
    # IT [MENU DÉMARRER] [liste complète des trois choix NOUVELLE PARTIE, CHARGER et QUITTER ; déplace ou redimensionne leur zone commune] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : IntrFram.JAM] > Intro > MenuLst
    'menu_principal_rectangle': (161.0, 250.0, 461.0, 355.0),
    # IT [MENU DÉMARRER] [bouton NOUVELLE PARTIE uniquement ; déplace ou redimensionne sa zone] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : IntrFram.JAM] > Intro > MenuNew
    'menu_principal_nouvelle_partie_rectangle': (0.0, 0.0, 300.0, 35.0),
    # IT [MENU DÉMARRER] [texte d’invite de démarrage (TitleTxt) ; déplace ou redimensionne sa zone indépendante de la liste] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : IntrFram.JAM] > Intro > MenuStrt
    'menu_principal_texte_demarrer_rectangle': (84.0, 285.0, 576.0, 320.0),
    # IT [MENU DÉMARRER] [bouton CHARGER uniquement ; déplace ou redimensionne sa zone] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : IntrFram.JAM] > Intro > MenuLoad
    'menu_principal_charger_rectangle': (0.0, 0.0, 300.0, 35.0),
    # IT [MENU DÉMARRER] [bouton QUITTER uniquement ; déplace ou redimensionne sa zone] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : IntrFram.JAM] > Intro > MenuExit
    'menu_principal_quitter_rectangle': (0.0, 0.0, 300.0, 35.0),

    # IT [MENU DÉMARRER] [NOUVELLE PARTIE seul] [TAILLE HORIZONTALE DU TEXTE BLANC NORMAL] ; IntrFram.JAM / Intro / MenuNew
    'mn_new_actif_x': 0.40,
    # IT [MENU DÉMARRER] [NOUVELLE PARTIE seul] [TAILLE HORIZONTALE DU TEXTE GRIS DÉSACTIVÉ, état prévu mais déclenchement non confirmé] ; IntrFram.JAM / Intro / MenuNew
    'mn_new_gris_x': 0.40,
    # IT [MENU DÉMARRER] [NOUVELLE PARTIE seul] [TAILLE HORIZONTALE DU TEXTE JAUNE SURVOL] ; IntrFram.JAM / Intro / MenuNew
    'mn_new_jaune_x': 0.42,

    # IT [MENU DÉMARRER] [CHARGER seul] [TAILLE HORIZONTALE DU TEXTE BLANC NORMAL] ; IntrFram.JAM / Intro / MenuLoad
    'mn_load_actif_x': 0.40,
    # IT [MENU DÉMARRER] [CHARGER seul] [TAILLE HORIZONTALE DU TEXTE GRIS DÉSACTIVÉ, état prévu mais déclenchement non confirmé] ; IntrFram.JAM / Intro / MenuLoad
    'mn_load_gris_x': 0.40,
    # IT [MENU DÉMARRER] [CHARGER seul] [TAILLE HORIZONTALE DU TEXTE JAUNE SURVOL] ; IntrFram.JAM / Intro / MenuLoad
    'mn_load_jaune_x': 0.42,

    # IT [MENU DÉMARRER] [QUITTER seul] [TAILLE HORIZONTALE DU TEXTE BLANC NORMAL] ; IntrFram.JAM / Intro / MenuExit
    'mn_exit_actif_x': 0.40,
    # IT [MENU DÉMARRER] [QUITTER seul] [TAILLE HORIZONTALE DU TEXTE GRIS DÉSACTIVÉ, état prévu mais déclenchement non confirmé] ; IntrFram.JAM / Intro / MenuExit
    'mn_exit_gris_x': 0.40,
    # IT [MENU DÉMARRER] [QUITTER seul] [TAILLE HORIZONTALE DU TEXTE JAUNE SURVOL] ; IntrFram.JAM / Intro / MenuExit
    'mn_exit_jaune_x': 0.42,

    # IT ===== MENU PAUSE =====
    # IT [MENU PAUSE] [cadre qui contient les choix du menu pause ; déplace ou redimensionne le cadre complet] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PausMenu > PauseSc
    'menu_pause_ecran_rectangle': (160.0, 101.0, 480.0, 379.0),
    # IT [MENU PAUSE] [liste qui contient les six choix du menu pause ; déplace ou redimensionne leur zone commune] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PausMenu > PauseLst
    'menu_pause_liste_rectangle': (10.0, 32.0, 310.0, 243.0),
    # IT [MENU PAUSE] [bouton LIVRE NOIR uniquement ; déplace ou redimensionne sa zone] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PausMenu > PauItm01
    'menu_pause_bouton_1_rectangle': (0.0, 0.0, 300.0, 35.0),
    # IT [MENU PAUSE] [bouton SAUVEGARDER uniquement ; déplace ou redimensionne sa zone] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PausMenu > PauItm02
    'menu_pause_bouton_2_rectangle': (0.0, 0.0, 300.0, 35.0),
    # IT [MENU PAUSE] [bouton OPTIONS uniquement ; déplace ou redimensionne sa zone] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PausMenu > PauItm03
    'menu_pause_bouton_3_rectangle': (0.0, 0.0, 300.0, 35.0),
    # IT [MENU PAUSE] [bouton PHOTOS uniquement ; déplace ou redimensionne sa zone] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PausMenu > PauItm04
    'menu_pause_bouton_4_rectangle': (0.0, 0.0, 300.0, 35.0),
    # IT [MENU PAUSE] [bouton EXTRAS uniquement ; déplace ou redimensionne sa zone] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PausMenu > PauItm05
    'menu_pause_bouton_5_rectangle': (0.0, 0.0, 300.0, 35.0),
    # IT [MENU PAUSE] [bouton QUITTER uniquement ; déplace ou redimensionne sa zone] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PausMenu > PauItm06
    'menu_pause_bouton_6_rectangle': (0.0, 0.0, 300.0, 35.0),
    # IT [MENU PAUSE] [indication en bas de l’écran haut bas ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PausMenu
    'menu_pause_aide_haut_bas_rectangle': (-80.0, 288.0, 86.0, 318.0),
    # IT [MENU PAUSE] [indication en bas de l’écran retour ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PausMenu
    'menu_pause_aide_retour_rectangle': (87.0, 288.0, 233.0, 318.0),
    # IT [MENU PAUSE] [indication en bas de l’écran sélection ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PausMenu
    'menu_pause_aide_selection_rectangle': (234.0, 288.0, 400.0, 318.0),

    # IT [MENU PAUSE] [LIVRE NOIR seul] [TAILLE HORIZONTALE DU TEXTE BLANC NORMAL] ; AppInit.JAM / PausMenu / PauItm01
    'pause_1_actif_x': 0.30,
    # IT [MENU PAUSE] [LIVRE NOIR seul] [TAILLE HORIZONTALE DU TEXTE GRIS DÉSACTIVÉ, état prévu mais déclenchement non confirmé] ; AppInit.JAM / PausMenu / PauItm01
    'pause_1_gris_x': 0.30,
    # IT [MENU PAUSE] [LIVRE NOIR seul] [TAILLE HORIZONTALE DU TEXTE JAUNE SURVOL] ; AppInit.JAM / PausMenu / PauItm01
    'pause_1_jaune_x': 0.40,

    # IT [MENU PAUSE] [SAUVEGARDER seul] [TAILLE HORIZONTALE DU TEXTE BLANC NORMAL] ; AppInit.JAM / PausMenu / PauItm02
    'pause_2_actif_x': 0.25,
    # IT [MENU PAUSE] [SAUVEGARDER seul] [TAILLE HORIZONTALE DU TEXTE GRIS DÉSACTIVÉ, état prévu mais déclenchement non confirmé] ; AppInit.JAM / PausMenu / PauItm02
    'pause_2_gris_x': 0.25,
    # IT [MENU PAUSE] [SAUVEGARDER seul] [TAILLE HORIZONTALE DU TEXTE JAUNE SURVOL] ; AppInit.JAM / PausMenu / PauItm02
    'pause_2_jaune_x': 0.35,

    # IT [MENU PAUSE] [OPTIONS seul] [TAILLE HORIZONTALE DU TEXTE BLANC NORMAL] ; AppInit.JAM / PausMenu / PauItm03
    'pause_3_actif_x': 0.30,
    # IT [MENU PAUSE] [OPTIONS seul] [TAILLE HORIZONTALE DU TEXTE GRIS DÉSACTIVÉ, état prévu mais déclenchement non confirmé] ; AppInit.JAM / PausMenu / PauItm03
    'pause_3_gris_x': 0.30,
    # IT [MENU PAUSE] [OPTIONS seul] [TAILLE HORIZONTALE DU TEXTE JAUNE SURVOL] ; AppInit.JAM / PausMenu / PauItm03
    'pause_3_jaune_x': 0.40,

    # IT [MENU PAUSE] [PHOTOS seul] [TAILLE HORIZONTALE DU TEXTE BLANC NORMAL] ; AppInit.JAM / PausMenu / PauItm04
    'pause_4_actif_x': 0.30,
    # IT [MENU PAUSE] [PHOTOS seul] [TAILLE HORIZONTALE DU TEXTE GRIS DÉSACTIVÉ, état prévu mais déclenchement non confirmé] ; AppInit.JAM / PausMenu / PauItm04
    'pause_4_gris_x': 0.30,
    # IT [MENU PAUSE] [PHOTOS seul] [TAILLE HORIZONTALE DU TEXTE JAUNE SURVOL] ; AppInit.JAM / PausMenu / PauItm04
    'pause_4_jaune_x': 0.40,

    # IT [MENU PAUSE] [EXTRAS seul] [TAILLE HORIZONTALE DU TEXTE BLANC NORMAL] ; AppInit.JAM / PausMenu / PauItm05
    'pause_5_actif_x': 0.30,
    # IT [MENU PAUSE] [EXTRAS seul] [TAILLE HORIZONTALE DU TEXTE GRIS DÉSACTIVÉ, état prévu mais déclenchement non confirmé] ; AppInit.JAM / PausMenu / PauItm05
    'pause_5_gris_x': 0.30,
    # IT [MENU PAUSE] [EXTRAS seul] [TAILLE HORIZONTALE DU TEXTE JAUNE SURVOL] ; AppInit.JAM / PausMenu / PauItm05
    'pause_5_jaune_x': 0.40,

    # IT [MENU PAUSE] [QUITTER seul] [TAILLE HORIZONTALE DU TEXTE BLANC NORMAL] ; AppInit.JAM / PausMenu / PauItm06
    'pause_6_actif_x': 0.30,
    # IT [MENU PAUSE] [QUITTER seul] [TAILLE HORIZONTALE DU TEXTE GRIS DÉSACTIVÉ, état prévu mais déclenchement non confirmé] ; AppInit.JAM / PausMenu / PauItm06
    'pause_6_gris_x': 0.30,
    # IT [MENU PAUSE] [QUITTER seul] [TAILLE HORIZONTALE DU TEXTE JAUNE SURVOL] ; AppInit.JAM / PausMenu / PauItm06
    'pause_6_jaune_x': 0.40,

    # IT ===== LIVRE NOIR > NAVIGATION =====
    # IT [LIVRE NOIR > NAVIGATION] [fond ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > BBook
    'livre_noir_fond_rectangle': (64.0, 63.0, 576.0, 407.0),
    # IT [LIVRE NOIR > NAVIGATION] [ligne ; 160 éléments possèdent ce rectangle d’origine ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > BBook
    'livre_noir_item_rectangle': (0.0, 0.0, 234.0, 28.0),
    # IT [LIVRE NOIR > NAVIGATION] [ligne icône ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > BBook
    'livre_noir_item_icone_rectangle': (0.0, 4.0, 20.0, 24.0),
    # IT [LIVRE NOIR > NAVIGATION] [ligne texte marge ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > BBook
    'livre_noir_item_texte_marge_rectangle': (25.0, 0.0, 25.0, 0.0),
    # IT [LIVRE NOIR > NAVIGATION] [quete inactif ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > BBook
    'onglet_quete_inactif_rectangle': (55.0, -29.0, 83.0, 2.0),
    # IT [LIVRE NOIR > NAVIGATION] [filles inactif ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > BBook
    'onglet_filles_inactif_rectangle': (87.0, -29.0, 115.0, 2.0),
    # IT [LIVRE NOIR > NAVIGATION] [tenue inactif ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > BBook
    'onglet_tenue_inactif_rectangle': (118.0, -29.0, 146.0, 2.0),
    # IT [LIVRE NOIR > NAVIGATION] [objet inactif ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > BBook
    'onglet_objet_inactif_rectangle': (148.0, -29.0, 176.0, 2.0),
    # IT [LIVRE NOIR > NAVIGATION] [stats inactif ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > BBook
    'onglet_stats_inactif_rectangle': (180.0, -29.0, 208.0, 2.0),

    # IT ===== LIVRE NOIR > QUÊTES =====
    # IT [LIVRE NOIR > QUÊTES] [onglet actif ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Quests
    'quete_onglet_actif_rectangle': (38.0, -29.0, 101.0, 2.0),
    # IT [LIVRE NOIR > QUÊTES] [titre ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Quests
    'quete_titre_rectangle': (280.0, -40.0, 460.0, 10.0),
    # IT [LIVRE NOIR > QUÊTES] [titre icône ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Quests
    'quete_titre_icone_rectangle': (470.0, -31.0, 502.0, 1.0),
    # IT [LIVRE NOIR > QUÊTES] [flèche de défilement haut ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Quests
    'quete_scroll_haut_rectangle': (16.0, 52.0, 36.0, 72.0),
    # IT [LIVRE NOIR > QUÊTES] [flèche de défilement bas ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Quests
    'quete_scroll_bas_rectangle': (16.0, 250.0, 36.0, 271.0),
    # IT [LIVRE NOIR > QUÊTES] [liste ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Quests
    'quete_liste_rectangle': (38.0, 32.0, 272.0, 286.0),
    # IT [LIVRE NOIR > QUÊTES] [sous titre ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Quests
    'quete_sous_titre_rectangle': (280.0, 25.0, 460.0, 65.0),
    # IT [LIVRE NOIR > QUÊTES] [description ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Quests
    'quete_description_rectangle': (280.0, 75.0, 482.0, 350.0),
    # IT [LIVRE NOIR > QUÊTES] [indication en bas de l’écran page ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Quests
    'quete_aide_page_rectangle': (0.0, 353.0, 170.0, 385.0),
    # IT [LIVRE NOIR > QUÊTES] [indication en bas de l’écran haut bas ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Quests
    'quete_aide_haut_bas_rectangle': (171.0, 353.0, 340.0, 385.0),
    # IT [LIVRE NOIR > QUÊTES] [indication en bas de l’écran retour ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Quests
    'quete_aide_retour_rectangle': (341.0, 353.0, 512.0, 385.0),

    # IT [LIVRE NOIR] [grand titre LIVRE NOIR / QUÊTES seul] [TAILLE HORIZONTALE DU TEXTE BLANC] ; Levels/*.JAM / Quests / ScrTitle
    'quete_titre_actif_x': 0.26,

    # IT ===== LIVRE NOIR > FILLES =====
    # IT [LIVRE NOIR > FILLES] [onglet actif ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlDetl
    'fille_onglet_actif_rectangle': (70.0, -29.0, 133.0, 2.0),
    # IT [LIVRE NOIR > FILLES] [titre ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlDetl
    'fille_titre_rectangle': (280.0, -40.0, 460.0, 10.0),
    # IT [LIVRE NOIR > FILLES] [titre icône ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlDetl
    'fille_titre_icone_rectangle': (470.0, -31.0, 502.0, 1.0),
    # IT [LIVRE NOIR > FILLES] [liste ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlDetl
    'fille_liste_rectangle': (38.0, 32.0, 272.0, 286.0),
    # IT [LIVRE NOIR > FILLES] [image principale ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlDetl
    'fille_image_principale_rectangle': (311.0, 22.0, 439.0, 150.0),
    # IT [LIVRE NOIR > FILLES] [icône ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlDetl
    'fille_icone_rectangle': (343.0, 210.0, 407.0, 274.0),
    # IT [LIVRE NOIR > FILLES] [jeton texte ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlDetl
    'fille_token_texte_rectangle': (311.0, 285.0, 439.0, 315.0),
    # IT [LIVRE NOIR > FILLES] [flèche de défilement haut ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlDetl
    'fille_scroll_haut_rectangle': (16.0, 52.0, 36.0, 72.0),
    # IT [LIVRE NOIR > FILLES] [flèche de défilement bas ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlDetl
    'fille_scroll_bas_rectangle': (16.0, 250.0, 36.0, 271.0),
    # IT [LIVRE NOIR > FILLES] [texte milieu ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlDetl
    'fille_texte_milieu_rectangle': (311.0, 175.0, 439.0, 205.0),
    # IT [LIVRE NOIR > FILLES] [indication en bas de l’écran page ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlDetl
    'fille_aide_page_rectangle': (0.0, 353.0, 123.0, 385.0),
    # IT [LIVRE NOIR > FILLES] [indication en bas de l’écran haut bas ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlDetl
    'fille_aide_haut_bas_rectangle': (124.0, 353.0, 251.0, 385.0),
    # IT [LIVRE NOIR > FILLES] [indication en bas de l’écran sélection ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlDetl
    'fille_aide_selection_rectangle': (252.0, 353.0, 390.0, 385.0),
    # IT [LIVRE NOIR > FILLES] [indication en bas de l’écran retour ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlDetl
    'fille_aide_retour_rectangle': (391.0, 353.0, 507.0, 385.0),

    # IT [LIVRE NOIR] [grand titre LIVRE NOIR / FILLES seul] [TAILLE HORIZONTALE DU TEXTE BLANC] ; Levels/*.JAM / GirlDetl / ScrTitle
    'fille_titre_actif_x': 0.3,

    # IT [LIVRE NOIR > FILLES] [liste gauche ; texte normal] [TAILLE HORIZONTALE ITITLE] ; Style FGLIST cloné depuis ListItem/BBook
    'fille_liste_actif_x': 0.25,
    # IT [LIVRE NOIR > FILLES] [liste gauche ; texte désactivé] [TAILLE HORIZONTALE ITITLE_G]
    'fille_liste_gris_x': 0.25,
    # IT [LIVRE NOIR > FILLES] [liste gauche ; texte sélectionné] [TAILLE HORIZONTALE ITITLE_S]
    'fille_liste_jaune_x': 0.25,

    # IT [LIVRE NOIR > FILLES] [droite ; libellé milieu] [GDEF_W dédié]
    'fille_texte_milieu_gdef_x': 0.65,
    # IT [LIVRE NOIR > FILLES] [droite ; libellé milieu] [ITITLE dédié]
    'fille_texte_milieu_ititle_x': 0.25,
    # IT [LIVRE NOIR > FILLES] [droite basse ; nom du cadeau/objet] [GDEF_W dédié]
    'fille_token_texte_gdef_x': 0.65,
    # IT [LIVRE NOIR > FILLES] [droite basse ; nom du cadeau/objet] [ITITLE dédié]
    'fille_token_texte_ititle_x': 0.25,

    # IT ===== LIVRE NOIR > TENUES =====
    # IT [LIVRE NOIR > TENUES] [onglet actif ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Costume
    'tenue_onglet_actif_rectangle': (101.0, -29.0, 164.0, 2.0),
    # IT [LIVRE NOIR > TENUES] [titre ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Costume
    'tenue_titre_rectangle': (280.0, -40.0, 460.0, 10.0),
    # IT [LIVRE NOIR > TENUES] [titre icône ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Costume
    'tenue_titre_icone_rectangle': (470.0, -31.0, 502.0, 1.0),
    # IT [LIVRE NOIR > TENUES] [liste ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Costume
    'tenue_liste_rectangle': (38.0, 32.0, 272.0, 286.0),
    # IT [LIVRE NOIR > TENUES] [flèche de défilement haut ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Costume
    'tenue_scroll_haut_rectangle': (16.0, 52.0, 36.0, 72.0),
    # IT [LIVRE NOIR > TENUES] [flèche de défilement bas ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Costume
    'tenue_scroll_bas_rectangle': (16.0, 250.0, 36.0, 271.0),
    # IT [LIVRE NOIR > TENUES] [sous titre ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Costume
    'tenue_sous_titre_rectangle': (291.0, 247.0, 495.0, 262.0),
    # IT [LIVRE NOIR > TENUES] [accessoire 1 ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Costume
    'tenue_accessoire_1_rectangle': (291.0, 262.0, 336.0, 314.0),
    # IT [LIVRE NOIR > TENUES] [accessoire 2 ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Costume
    'tenue_accessoire_2_rectangle': (344.0, 262.0, 389.0, 314.0),
    # IT [LIVRE NOIR > TENUES] [accessoire 3 ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Costume
    'tenue_accessoire_3_rectangle': (397.0, 262.0, 442.0, 314.0),
    # IT [LIVRE NOIR > TENUES] [accessoire 4 ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Costume
    'tenue_accessoire_4_rectangle': (450.0, 262.0, 495.0, 314.0),

    # IT [LIVRE NOIR] [grand titre LIVRE NOIR / TENUES seul] [TAILLE HORIZONTALE DU TEXTE BLANC] ; Levels/*.JAM / Costume / ScrTitle
    'tenue_titre_actif_x': 0.3,

    # IT [LIVRE NOIR] [TENUES] [indication en bas de l’écran page ; position et dimensions de cet élément] page, haut/bas et retour.
    
    'tenue_aide_page_rectangle': (0.0, 353.0, 170.0, 385.0),
    
    # IT [LIVRE NOIR] [TENUES] [indication en bas de l’écran page ; position et dimensions de cet élément] page, haut/bas et retour.
    
    'tenue_aide_haut_bas_rectangle': (171.0, 353.0, 340.0, 385.0),
    
    # IT [LIVRE NOIR] [TENUES] [indication en bas de l’écran page ; position et dimensions de cet élément] page, haut/bas et retour.
    
    'tenue_aide_retour_rectangle': (341.0, 353.0, 512.0, 385.0),




    # IT ===== LIVRE NOIR > OBJETS =====
    # IT [LIVRE NOIR > OBJETS] [onglet actif ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Invntory
    'objet_onglet_actif_rectangle': (131.0, -29.0, 194.0, 2.0),
    # IT [LIVRE NOIR > OBJETS] [titre ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Invntory
    'objet_titre_rectangle': (280.0, -40.0, 460.0, 10.0),
    # IT [LIVRE NOIR > OBJETS] [titre icône ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Invntory
    'objet_titre_icone_rectangle': (470.0, -31.0, 502.0, 1.0),
    # IT [LIVRE NOIR > OBJETS] [liste ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Invntory
    'objet_liste_rectangle': (38.0, 32.0, 272.0, 286.0),
    # IT [LIVRE NOIR > OBJETS] [flèche de défilement haut ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Invntory
    'objet_scroll_haut_rectangle': (16.0, 52.0, 36.0, 72.0),
    # IT [LIVRE NOIR > OBJETS] [flèche de défilement bas ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Invntory
    'objet_scroll_bas_rectangle': (16.0, 250.0, 36.0, 271.0),
    # IT [LIVRE NOIR > OBJETS] [image ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Invntory
    'objet_image_rectangle': (343.0, 54.0, 407.0, 118.0),
    # IT [LIVRE NOIR > OBJETS] [description ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Invntory
    'objet_description_rectangle': (280.0, 130.0, 460.0, 400.0),
    # IT [LIVRE NOIR > OBJETS] [indication en bas de l’écran page ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Invntory
    'objet_aide_page_rectangle': (0.0, 353.0, 123.0, 385.0),
    # IT [LIVRE NOIR > OBJETS] [indication en bas de l’écran haut bas ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Invntory
    'objet_aide_haut_bas_rectangle': (124.0, 353.0, 251.0, 385.0),
    # IT [LIVRE NOIR > OBJETS] [indication en bas de l’écran détail ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Invntory
    'objet_aide_detail_rectangle': (252.0, 353.0, 390.0, 385.0),
    # IT [LIVRE NOIR > OBJETS] [indication en bas de l’écran retour ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Invntory
    'objet_aide_retour_rectangle': (391.0, 353.0, 507.0, 385.0),

    # IT [LIVRE NOIR] [grand titre LIVRE NOIR / OBJETS seul] [TAILLE HORIZONTALE DU TEXTE BLANC] ; Levels/*.JAM / Invntory / ScrTitle
    'objet_titre_actif_x': 0.3,

    # IT ===== LIVRE NOIR > STATISTIQUES =====
    # IT [LIVRE NOIR > STATISTIQUES] [onglet actif ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Stats
    'stats_onglet_actif_rectangle': (163.0, -29.0, 226.0, 2.0),
    # IT [LIVRE NOIR > STATISTIQUES] [titre ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Stats
    'stats_titre_rectangle': (280.0, -40.0, 460.0, 10.0),
    # IT [LIVRE NOIR > STATISTIQUES] [titre icône ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Stats
    'stats_titre_icone_rectangle': (470.0, -31.0, 502.0, 1.0),
    # IT [LIVRE NOIR > STATISTIQUES] [liste gauche ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Stats
    'stats_liste_gauche_rectangle': (38.0, 32.0, 272.0, 285.0),
    # IT [LIVRE NOIR > STATISTIQUES] [ligne gauche ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Stats
    'stats_item_gauche_rectangle': (0.0, 0.0, 234.0, 28.0),
    # IT [LIVRE NOIR > STATISTIQUES] [flèche de défilement haut ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Stats
    'stats_scroll_haut_rectangle': (16.0, 52.0, 36.0, 72.0),
    # IT [LIVRE NOIR > STATISTIQUES] [flèche de défilement bas ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Stats
    'stats_scroll_bas_rectangle': (16.0, 250.0, 36.0, 271.0),
    # IT [LIVRE NOIR > STATISTIQUES] [liste droite ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Stats
    'stats_liste_droite_rectangle': (270.0, 32.0, 490.0, 286.0),
    # IT [LIVRE NOIR > STATISTIQUES] [ligne droite ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Stats
    'stats_item_droite_rectangle': (0.0, 0.0, 220.0, 24.0),
    # IT [LIVRE NOIR > STATISTIQUES] [indication en bas de l’écran page ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Stats
    'stats_aide_page_rectangle': (0.0, 353.0, 170.0, 385.0),
    # IT [LIVRE NOIR > STATISTIQUES] [indication en bas de l’écran haut bas ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Stats
    'stats_aide_haut_bas_rectangle': (171.0, 353.0, 340.0, 385.0),
    # IT [LIVRE NOIR > STATISTIQUES] [indication en bas de l’écran retour ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > Stats
    'stats_aide_retour_rectangle': (341.0, 353.0, 512.0, 385.0),

    # IT [LIVRE NOIR] [grand titre LIVRE NOIR / STATISTIQUES seul] [TAILLE HORIZONTALE DU TEXTE BLANC] ; Levels/*.JAM / Stats / ScrTitle
    'stats_titre_actif_x': 0.3,

    # IT ===== LIVRE NOIR > HISTORIQUE DES FILLES =====
    # IT [LIVRE NOIR > HISTORIQUE DES FILLES] [historique fond ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlHist
    'fille_historique_fond_rectangle': (48.0, 36.0, 592.0, 377.0),
    # IT [LIVRE NOIR > HISTORIQUE DES FILLES] [historique titre ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlHist
    'fille_historique_titre_rectangle': (335.0, 90.0, 463.0, 110.0),
    # IT [LIVRE NOIR > HISTORIQUE DES FILLES] [historique image ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlHist
    'fille_historique_image_rectangle': (335.0, 120.0, 463.0, 248.0),
    # IT [LIVRE NOIR > HISTORIQUE DES FILLES] [historique liste titre ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlHist
    'fille_historique_liste_titre_rectangle': (38.0, 30.0, 272.0, 55.0),
    # IT [LIVRE NOIR > HISTORIQUE DES FILLES] [historique liste ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlHist
    'fille_historique_liste_rectangle': (38.0, 70.0, 272.0, 295.0),
    # IT [LIVRE NOIR > HISTORIQUE DES FILLES] [historique flèche de défilement haut ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlHist
    'fille_historique_scroll_haut_rectangle': (16.0, 90.0, 36.0, 110.0),
    # IT [LIVRE NOIR > HISTORIQUE DES FILLES] [historique flèche de défilement bas ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : Levels/*.JAM] > GirlHist
    'fille_historique_scroll_bas_rectangle': (16.0, 260.0, 36.0, 280.0),

    # IT ===== OPTIONS > MENU =====
    # IT [OPTIONS > MENU] [cadre de l’écran ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Options
    'option_ecran_rectangle': (128.0, 92.0, 512.0, 316.0),
    # IT [OPTIONS > MENU] [liste ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Options
    'option_liste_rectangle': (-32.0, 32.0, 416.0, 206.0),
    # IT [OPTIONS > MENU] [ligne ; 4 éléments possèdent ce rectangle d’origine ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Options
    'option_item_rectangle': (0.0, 0.0, 448.0, 40.0),
    # IT [OPTIONS > MENU] [indication en bas de l’écran haut bas ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Options
    'option_aide_haut_bas_rectangle': (-30.0, 234.0, 118.0, 264.0),
    # IT [OPTIONS > MENU] [indication en bas de l’écran retour ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Options
    'option_aide_retour_rectangle': (119.0, 234.0, 266.0, 264.0),
    # IT [OPTIONS > MENU] [indication en bas de l’écran sélection ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Options
    'option_aide_selection_rectangle': (267.0, 234.0, 414.0, 264.0),

    # IT ===== OPTIONS > AUDIO =====
    # IT [OPTIONS > AUDIO] [cadre de l’écran ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Audio
    'audio_ecran_rectangle': (130.0, 92.0, 510.0, 313.0),
    # IT [OPTIONS > AUDIO] [liste ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Audio
    'audio_liste_rectangle': (30.0, 50.0, 150.0, 171.0),
    # IT [OPTIONS > AUDIO] [ligne ; 3 éléments possèdent ce rectangle d’origine ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Audio
    'audio_item_rectangle': (0.0, 0.0, 120.0, 40.0),
    # IT [OPTIONS > AUDIO] [flèche gauche 1 ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Audio
    'audio_fleche_gauche_1_rectangle': (165.0, 63.0, 181.0, 79.0),
    # IT [OPTIONS > AUDIO] [flèche gauche 2 ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Audio
    'audio_fleche_gauche_2_rectangle': (165.0, 103.0, 181.0, 119.0),
    # IT [OPTIONS > AUDIO] [flèche gauche 3 ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Audio
    'audio_fleche_gauche_3_rectangle': (165.0, 143.0, 181.0, 159.0),
    # IT [OPTIONS > AUDIO] [flèche droite 1 ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Audio
    'audio_fleche_droite_1_rectangle': (329.0, 63.0, 345.0, 79.0),
    # IT [OPTIONS > AUDIO] [flèche droite 2 ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Audio
    'audio_fleche_droite_2_rectangle': (329.0, 103.0, 345.0, 119.0),
    # IT [OPTIONS > AUDIO] [flèche droite 3 ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Audio
    'audio_fleche_droite_3_rectangle': (329.0, 143.0, 345.0, 159.0),
    # IT [OPTIONS > AUDIO] [indication en bas de l’écran gauche droite ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Audio
    'audio_aide_gauche_droite_rectangle': (-86.0, 231.0, 190.0, 261.0),
    # IT [OPTIONS > AUDIO] [indication en bas de l’écran retour ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Audio
    'audio_aide_retour_rectangle': (191.0, 231.0, 319.0, 261.0),
    # IT [OPTIONS > AUDIO] [indication en bas de l’écran sélection ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Audio
    'audio_aide_selection_rectangle': (320.0, 231.0, 468.0, 261.0),

    # IT ===== OPTIONS > COMMANDES =====
    # IT [OPTIONS > COMMANDES] [cadre de l’écran ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Cntrller
    'controleur_ecran_rectangle': (48.0, 132.0, 592.0, 328.0),
    # IT [OPTIONS > COMMANDES] [liste ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Cntrller
    'controleur_liste_rectangle': (105.0, 70.0, 245.0, 154.0),
    # IT [OPTIONS > COMMANDES] [ligne ; 3 éléments possèdent ce rectangle d’origine ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Cntrller
    'controleur_item_rectangle': (0.0, 0.0, 140.0, 28.0),
    # IT [OPTIONS > COMMANDES] [indication en bas de l’écran haut bas ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Cntrller
    'controleur_aide_haut_bas_rectangle': (0.0, 206.0, 136.0, 236.0),
    # IT [OPTIONS > COMMANDES] [indication en bas de l’écran cycle ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Cntrller
    'controleur_aide_cycle_rectangle': (137.0, 206.0, 273.0, 236.0),
    # IT [OPTIONS > COMMANDES] [indication en bas de l’écran retour ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Cntrller
    'controleur_aide_retour_rectangle': (274.0, 206.0, 409.0, 236.0),
    # IT [OPTIONS > COMMANDES] [indication en bas de l’écran sélection ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Cntrller
    'controleur_aide_selection_rectangle': (410.0, 206.0, 545.0, 236.0),

    # IT ===== OPTIONS > VIBRATION =====
    # IT [OPTIONS > VIBRATION] [cadre de l’écran ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Rumble
    'vibration_ecran_rectangle': (130.0, 92.0, 510.0, 233.0),
    # IT [OPTIONS > VIBRATION] [liste ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Rumble
    'vibration_liste_rectangle': (30.0, 60.0, 150.0, 101.0),
    # IT [OPTIONS > VIBRATION] [ligne ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Rumble
    'vibration_item_rectangle': (0.0, 0.0, 120.0, 40.0),
    # IT [OPTIONS > VIBRATION] [flèche gauche ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Rumble
    'vibration_fleche_gauche_rectangle': (165.0, 73.0, 181.0, 89.0),
    # IT [OPTIONS > VIBRATION] [flèche droite ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Rumble
    'vibration_fleche_droite_rectangle': (329.0, 73.0, 345.0, 89.0),
    # IT [OPTIONS > VIBRATION] [indication en bas de l’écran gauche droite ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Rumble
    'vibration_aide_gauche_droite_rectangle': (-30.0, 151.0, 116.0, 181.0),
    # IT [OPTIONS > VIBRATION] [indication en bas de l’écran retour ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Rumble
    'vibration_aide_retour_rectangle': (117.0, 151.0, 264.0, 181.0),
    # IT [OPTIONS > VIBRATION] [indication en bas de l’écran sélection ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Rumble
    'vibration_aide_selection_rectangle': (265.0, 151.0, 410.0, 181.0),

    # IT ===== OPTIONS > DIFFICULTÉ =====
    # IT [OPTIONS > DIFFICULTÉ] [cadre de l’écran ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Diffclty
    'difficulte_ecran_rectangle': (130.0, 92.0, 510.0, 233.0),
    # IT [OPTIONS > DIFFICULTÉ] [liste ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Diffclty
    'difficulte_liste_rectangle': (30.0, 60.0, 150.0, 101.0),
    # IT [OPTIONS > DIFFICULTÉ] [ligne ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Diffclty
    'difficulte_item_rectangle': (0.0, 0.0, 120.0, 40.0),
    # IT [OPTIONS > DIFFICULTÉ] [flèche gauche ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Diffclty
    'difficulte_fleche_gauche_rectangle': (165.0, 73.0, 181.0, 89.0),
    # IT [OPTIONS > DIFFICULTÉ] [flèche droite ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Diffclty
    'difficulte_fleche_droite_rectangle': (329.0, 73.0, 345.0, 89.0),
    # IT [OPTIONS > DIFFICULTÉ] [indication en bas de l’écran gauche droite ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Diffclty
    'difficulte_aide_gauche_droite_rectangle': (-30.0, 151.0, 116.0, 181.0),
    # IT [OPTIONS > DIFFICULTÉ] [indication en bas de l’écran retour ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Diffclty
    'difficulte_aide_retour_rectangle': (117.0, 151.0, 264.0, 181.0),
    # IT [OPTIONS > DIFFICULTÉ] [indication en bas de l’écran sélection ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Diffclty
    'difficulte_aide_selection_rectangle': (265.0, 151.0, 410.0, 181.0),

    # IT ===== PHOTOS > MENU =====
    # IT [PHOTOS > MENU] [cadre de l’écran ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoOpt
    'photo_menu_ecran_rectangle': (128.0, 128.0, 512.0, 272.0),
    # IT [PHOTOS > MENU] [liste ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoOpt
    'photo_menu_liste_rectangle': (-32.0, 32.0, 416.0, 128.0),
    # IT [PHOTOS > MENU] [ligne ; 2 éléments possèdent ce rectangle d’origine ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoOpt
    'photo_menu_item_rectangle': (0.0, 0.0, 448.0, 40.0),
    # IT [PHOTOS > MENU] [indication en bas de l’écran haut bas ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoOpt
    'photo_menu_aide_haut_bas_rectangle': (-20.0, 154.0, 128.0, 184.0),
    # IT [PHOTOS > MENU] [indication en bas de l’écran retour ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoOpt
    'photo_menu_aide_retour_rectangle': (129.0, 154.0, 256.0, 184.0),
    # IT [PHOTOS > MENU] [indication en bas de l’écran sélection ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoOpt
    'photo_menu_aide_selection_rectangle': (257.0, 154.0, 404.0, 184.0),

    # IT ===== PHOTOS > ALBUM =====
    # IT [PHOTOS > ALBUM] [cadre de l’écran ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoAlb
    'photo_album_ecran_rectangle': (64.0, 64.0, 576.0, 384.0),
    # IT [PHOTOS > ALBUM] [titre ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoAlb
    'photo_album_titre_rectangle': (52.0, 43.0, 466.0, 73.0),
    # IT [PHOTOS > ALBUM] [flèche de défilement gauche ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoAlb
    'photo_album_scroll_gauche_rectangle': (22.0, 30.0, 38.0, 46.0),
    # IT [PHOTOS > ALBUM] [flèche de défilement droite ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoAlb
    'photo_album_scroll_droite_rectangle': (475.0, 30.0, 491.0, 46.0),
    # IT [PHOTOS > ALBUM] [flèche de défilement haut ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoAlb
    'photo_album_scroll_haut_rectangle': (30.0, 78.0, 46.0, 94.0),
    # IT [PHOTOS > ALBUM] [flèche de défilement bas ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoAlb
    'photo_album_scroll_bas_rectangle': (30.0, 232.0, 46.0, 248.0),
    # IT [PHOTOS > ALBUM] [photo 1 ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoAlb
    'photo_album_photo_1_rectangle': (72.0, 68.0, 190.0, 158.0),
    # IT [PHOTOS > ALBUM] [photo 2 ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoAlb
    'photo_album_photo_2_rectangle': (200.0, 68.0, 318.0, 158.0),
    # IT [PHOTOS > ALBUM] [photo 3 ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoAlb
    'photo_album_photo_3_rectangle': (328.0, 68.0, 446.0, 158.0),
    # IT [PHOTOS > ALBUM] [photo 4 ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoAlb
    'photo_album_photo_4_rectangle': (72.0, 168.0, 190.0, 258.0),
    # IT [PHOTOS > ALBUM] [photo 5 ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoAlb
    'photo_album_photo_5_rectangle': (200.0, 168.0, 318.0, 258.0),
    # IT [PHOTOS > ALBUM] [photo 6 ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoAlb
    'photo_album_photo_6_rectangle': (328.0, 168.0, 446.0, 258.0),
    # IT [PHOTOS > ALBUM] [indication en bas de l’écran navigation ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoAlb
    'photo_album_aide_navigation_rectangle': (32.0, 330.0, 190.0, 360.0),
    # IT [PHOTOS > ALBUM] [indication en bas de l’écran zoom ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoAlb
    'photo_album_aide_zoom_rectangle': (201.0, 330.0, 318.0, 360.0),
    # IT [PHOTOS > ALBUM] [indication en bas de l’écran retour ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > PhotoAlb
    'photo_album_aide_retour_rectangle': (318.0, 330.0, 447.0, 360.0),

    # IT ===== EXTRAS > MENU =====
    # IT [EXTRAS > MENU] [cadre de l’écran ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Extras
    'extra_ecran_rectangle': (64.0, 128.0, 576.0, 352.0),
    # IT [EXTRAS > MENU] [liste ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Extras
    'extra_liste_rectangle': (32.0, 32.0, 480.0, 195.0),
    # IT [EXTRAS > MENU] [ligne ; 4 éléments possèdent ce rectangle d’origine ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Extras
    'extra_item_rectangle': (0.0, 0.0, 448.0, 40.0),
    # IT [EXTRAS > MENU] [indication en bas de l’écran haut bas ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Extras
    'extra_aide_haut_bas_rectangle': (0.0, 236.0, 170.0, 264.0),
    # IT [EXTRAS > MENU] [indication en bas de l’écran retour ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Extras
    'extra_aide_retour_rectangle': (171.0, 236.0, 340.0, 264.0),
    # IT [EXTRAS > MENU] [indication en bas de l’écran sélection ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > Extras
    'extra_aide_selection_rectangle': (341.0, 236.0, 512.0, 264.0),

    # IT ===== EXTRAS > BONUS =====
    # IT [EXTRAS > BONUS] [cadre de l’écran ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > BonusOpt
    'bonus_ecran_rectangle': (110.0, 72.0, 530.0, 253.0),
    # IT [EXTRAS > BONUS] [liste ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > BonusOpt
    'bonus_liste_rectangle': (30.0, 60.0, 190.0, 141.0),
    # IT [EXTRAS > BONUS] [ligne ; 2 éléments possèdent ce rectangle d’origine ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > BonusOpt
    'bonus_item_rectangle': (0.0, 0.0, 160.0, 40.0),
    # IT [EXTRAS > BONUS] [indication en bas de l’écran gauche droite ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > BonusOpt
    'bonus_aide_gauche_droite_rectangle': (0.0, 191.0, 140.0, 221.0),
    # IT [EXTRAS > BONUS] [indication en bas de l’écran retour ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > BonusOpt
    'bonus_aide_retour_rectangle': (141.0, 191.0, 280.0, 221.0),
    # IT [EXTRAS > BONUS] [indication en bas de l’écran sélection ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > BonusOpt
    'bonus_aide_selection_rectangle': (281.0, 191.0, 420.0, 221.0),

    # IT ===== CHARGER / SAUVEGARDER > ÉCRAN DES FICHIERS =====
    # IT [CHARGER / SAUVEGARDER > ÉCRAN DES FICHIERS] [cadre de l’écran ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > LoadGame
    'sauvegarde_ecran_rectangle': (64.0, 79.0, 576.0, 401.0),
    # IT [CHARGER / SAUVEGARDER > ÉCRAN DES FICHIERS] [liste ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > LoadGame
    'sauvegarde_liste_rectangle': (55.0, 113.0, 457.0, 281.0),
    # IT [CHARGER / SAUVEGARDER > ÉCRAN DES FICHIERS] [flèche gauche ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > LoadGame
    'sauvegarde_fleche_gauche_rectangle': (23.0, 30.0, 55.0, 62.0),
    # IT [CHARGER / SAUVEGARDER > ÉCRAN DES FICHIERS] [flèche droite ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > LoadGame
    'sauvegarde_fleche_droite_rectangle': (457.0, 30.0, 489.0, 62.0),
    # IT [CHARGER / SAUVEGARDER > ÉCRAN DES FICHIERS] [flèche haut ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > LoadGame
    'sauvegarde_fleche_haut_rectangle': (31.0, 121.0, 46.0, 137.0),
    # IT [CHARGER / SAUVEGARDER > ÉCRAN DES FICHIERS] [flèche bas ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > LoadGame
    'sauvegarde_fleche_bas_rectangle': (31.0, 257.0, 46.0, 273.0),
    # IT [CHARGER / SAUVEGARDER > ÉCRAN DES FICHIERS] [informations ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > LoadGame
    'sauvegarde_info_rectangle': (-42.0, 50.0, 554.0, 70.0),
    # IT [CHARGER / SAUVEGARDER > ÉCRAN DES FICHIERS] [espace libre ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > LoadGame
    'sauvegarde_espace_libre_rectangle': (50.0, 281.0, 346.0, 309.0),
    # IT [CHARGER / SAUVEGARDER > ÉCRAN DES FICHIERS] [boutons SAUVEGARDER et CHARGER partageant les mêmes coordonnées ; modification potentiellement commune aux deux écrans] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > LoadGame
    'sauvegarde_bouton_sauver_rectangle': (0.0, 332.0, 170.0, 362.0),
    # IT [CHARGER / SAUVEGARDER > ÉCRAN DES FICHIERS] [bouton supprimer ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > LoadGame
    'sauvegarde_bouton_supprimer_rectangle': (171.0, 332.0, 384.0, 362.0),
    # IT [CHARGER / SAUVEGARDER > ÉCRAN DES FICHIERS] [bouton annuler ; position et dimensions de cet élément] [OFFSET X1,Y1 ; TAILLE X2-X1,Y2-Y1] ; [DU FICHIER : AppInit.JAM] > LoadGame
    'sauvegarde_bouton_annuler_rectangle': (385.0, 332.0, 512.0, 362.0),



    # IT [CHARGER / SAUVEGARDER > FICHIERS] [lignes non survolées de la liste de fichiers CHARGER/SAUVEGARDER] [TAILLE HORIZONTALE DU TEXTE BLANC NORMAL] ; AppInit.JAM / Global / LoadItem / GDEF_WS ; actif partagé, toute autre utilisation du même actif change aussi
    'gdef_ws_x': 0.55,
    # IT [CHARGER / SAUVEGARDER > FICHIERS] [liste des fichiers CHARGER/SAUVEGARDER et boutons de navigation (styles LoadItem/MouseBx)] [TAILLE HORIZONTALE DU TEXTE JAUNE SURVOL] ; AppInit.JAM / Global / GDEF_S ; actif partagé, toute autre utilisation du même actif change aussi
    'gdef_s_x': 0.65,

    # IT ===== TRANSITION > CHARGEMENT =====
    'gdef_w_x': 0.55,  # IT [TRANSITION > CHARGEMENT ; CHARGER / SAUVEGARDER > INFORMATIONS] [« Chargement »/pourcentage pendant la transition, informations au-dessus des sauvegardes et textes des commandes] [TAILLE HORIZONTALE DU TEXTE BLANC] ; AppInit.JAM / Global / GDEF_W ; actif partagé, toute autre utilisation du même actif change aussi

    # IT ===== MINI-JEU > POSE =====
    # IT [MINI-JEU > POSE] [message de départ « prêt / partez / pose » (clé historique « classement »)] [TAILLE HORIZONTALE DU TEXTE MINI-JEU POSE] ; Levels/*.JAM / WndrPose / LeadFont ; appliqué aux niveaux contenant WndrPose
    'pose_classement_x': 0.4,
    # IT [MINI-JEU > POSE] [décompte / chronomètre] [TAILLE HORIZONTALE DU TEXTE MINI-JEU POSE] ; Levels/*.JAM / WndrPose / TimeFont ; appliqué aux niveaux contenant WndrPose
    'pose_chronometre_x': 0.4,

    # IT ===== MINI-JEU > QUARTERS =====
    # IT [MINI-JEU > QUARTERS] [petit message de résultat] [TAILLE HORIZONTALE DU TEXTE MINI-JEU QUARTERS] ; Levels/*.JAM / Quarters / FDBKSMAL ; appliqué aux cinq niveaux contenant Quarters
    'quarters_indice_petit_x': 0.4,
    # IT [MINI-JEU > QUARTERS] [grand message de résultat] [TAILLE HORIZONTALE DU TEXTE MINI-JEU QUARTERS] ; Levels/*.JAM / Quarters / FDBKBIG ; appliqué aux cinq niveaux contenant Quarters
    'quarters_indice_grand_x': 0.9,

    # IT ===== ASSETS PARTAGÉS > OPTIONS ET MINI-JEUX =====
    # IT [OPTIONS > VIBRATION / DIFFICULTÉ / JEU ; MINI-JEUX > RÉSULTATS] [valeurs des OPTIONS vibration/difficulté/jeu (style OnOffCC) et lignes de résultats des mini-jeux] [TAILLE HORIZONTALE DU TEXTE GRIS] ; AppInit.JAM / Global / GDEF_GY ; actif partagé, toute autre utilisation du même actif change aussi
    'gdef_gy_x': 0.48,
    # IT [MINI-JEUX > RÉSULTATS] [valeurs désactivées des résultats de mini-jeux] [TAILLE HORIZONTALE DU TEXTE ROUGE] ; AppInit.JAM / Global / GDEF_RD
    'gdef_rd_x': 0.65,
    # IT [MINI-JEUX > RÉSULTATS] [valeurs ciblées des résultats de mini-jeux] [TAILLE HORIZONTALE DU TEXTE VERT] ; AppInit.JAM / Global / GDEF_GN
    'gdef_gn_x': 0.85,

    # IT ===== ASSETS PARTAGÉS > MENUS ET DESCRIPTIONS =====
    # IT [MENUS UTILISANT PItem] [lignes de menus avec style PItem (plusieurs écrans)] [TAILLE HORIZONTALE DU TEXTE BLANC] ; AppInit.JAM / Global / TITLE (style partagé) ; actif partagé, toute autre utilisation du même actif change aussi
    'title_x': 0.2,
    # IT [MENUS UTILISANT PItem] [lignes de menus avec style PItem quand désactivées] [TAILLE HORIZONTALE DU TEXTE GRIS DÉSACTIVÉ] ; AppInit.JAM / Global / TITLE_GR (style partagé) ; actif partagé, toute autre utilisation du même actif change aussi
    'title_gr_x': 0.2,
    # IT [MENUS UTILISANT PItem] [lignes de menus avec style PItem au survol] [TAILLE HORIZONTALE DU TEXTE JAUNE SURVOL] ; AppInit.JAM / Global / TITLE_S (style partagé) ; actif partagé, toute autre utilisation du même actif change aussi
    'title_s_x': 0.3,
    # IT [MINI-JEUX > RÉSULTATS] [texte de résultats de mini-jeux] [TAILLE HORIZONTALE DU TEXTE ROUGE] ; AppInit.JAM / Global / TITLE_RD (style partagé)
    'title_rd_x': 0.3,
    # IT [MINI-JEUX > RÉSULTATS] [texte de résultats de mini-jeux] [TAILLE HORIZONTALE DU TEXTE VERT] ; AppInit.JAM / Global / TITLE_GN (style partagé)
    'title_gn_x': 0.3,
    # IT [MINI-JEUX > RÉSULTATS] [texte de résultats de mini-jeux] [TAILLE HORIZONTALE DU TEXTE GRIS] ; AppInit.JAM / Global / TITLE_GY (style partagé)
    'title_gy_x': 0.3,
    # IT [INTERFACE DU JEU > DESCRIPTIONS] [descriptions de l’interface du jeu] [TAILLE HORIZONTALE DU TEXTE DESCRIPTION BLANCHE] ; AppInit.JAM / Global / DESC_WHT
    'desc_wht_x': 0.38,
    # IT [INTERFACE DU JEU > DESCRIPTIONS] [descriptions de l’interface du jeu] [TAILLE HORIZONTALE DU TEXTE DESCRIPTION GRISE] ; AppInit.JAM / Global / DESC_GRY
    'desc_gry_x': 0.38,
    # IT [ÉCRANS UTILISANT CET ACTIF GLOBAL] [lignes d’information utilisant ITITLE] [TAILLE HORIZONTALE DU TEXTE BLANC] ; AppInit.JAM / Global / ITITLE (style partagé)
    'ititle_x': 0.12,
    # IT [CHARGER / LIVRE NOIR] [titre « Choisir un fichier » de CHARGER et certaines lignes du Livre noir] [TAILLE HORIZONTALE DU TEXTE JAUNE] ; AppInit.JAM / Global / ITITLE_S (style partagé) ; actif partagé, toute autre utilisation du même actif change aussi
    'ititle_s_x': 0.12,
    # IT [ÉCRAN NON IDENTIFIÉ DANS LES WIDGETS EXTRAITS] [éléments utilisant ITITLE_G, écran précis non confirmé] [TAILLE HORIZONTALE DU TEXTE GRIS] ; AppInit.JAM / Global / ITITLE_G (style partagé)
    'ititle_g_x': 0.12,

    # IT ===== ASSETS SANS ÉCRAN CONFIRMÉ =====
    # IT [ÉCRAN NON IDENTIFIÉ DANS LES WIDGETS EXTRAITS] [actif présent dans AppInit.JAM / Global / ASSETS.AUA] [TAILLE HORIZONTALE DU TEXTE BLANC GDEF_WSB] ; aucune référence UI directe trouvée : écran non confirmé
    'gdef_wsb_x': 0.65,
    # IT [ÉCRAN NON IDENTIFIÉ DANS LES WIDGETS EXTRAITS] [actif présent dans AppInit.JAM / Global / ASSETS.AUA] [TAILLE HORIZONTALE DU TEXTE BLANC GDEF_WSC] ; aucune référence UI directe trouvée : écran non confirmé
    'gdef_wsc_x': 0.65,
    # IT [ÉCRAN NON IDENTIFIÉ DANS LES WIDGETS EXTRAITS] [actif présent dans AppInit.JAM / Global / ASSETS.AUA] [TAILLE HORIZONTALE DU TEXTE BLANC GDEF_WSM] ; aucune référence UI directe trouvée : écran non confirmé
    'gdef_wsm_x': 0.45,
    'stitle_x': 0.22,  # IT [ÉCRAN NON IDENTIFIÉ DANS LES WIDGETS EXTRAITS] [actif STITLE ; usage précis non repéré dans les widgets] [TAILLE HORIZONTALE DU TEXTE ACTIF STITLE] ; aucune référence UI directe trouvée : écran non confirmé
    # IT [ÉCRAN NON IDENTIFIÉ DANS LES WIDGETS EXTRAITS] [actif STITLE_S ; usage précis non repéré dans les widgets] [TAILLE HORIZONTALE DU TEXTE ACTIF STITLE_S] ; aucune référence UI directe trouvée : écran non confirmé
    'stitle_s_x': 0.22,
    # IT [ÉCRAN NON IDENTIFIÉ DANS LES WIDGETS EXTRAITS] [actif STITLE_G ; usage précis non repéré dans les widgets] [TAILLE HORIZONTALE DU TEXTE ACTIF STITLE_G] ; aucune référence UI directe trouvée : écran non confirmé
    'stitle_g_x': 0.22,
    # IT [ÉCRAN NON IDENTIFIÉ DANS LES WIDGETS EXTRAITS] [actif STITLESM ; usage précis non repéré dans les widgets] [TAILLE HORIZONTALE DU TEXTE ACTIF STITLESM] ; aucune référence UI directe trouvée : écran non confirmé
    'stitlesm_x': 0.16,

    # Largeur du texte ; hauteur conservée. Augmenter pour élargir les lettres.
    'chargement_message_dore_x': 0.18,
}


class LSL_MCL_Language_it:
    """Opérations et profil de la langue IT."""

    @staticmethod
    def profil():
        """Retourne les informations générales de cette langue."""
        return V.PROFILS_LANGUES['it']

    @staticmethod
    def geometrie():
        """Retourne une copie du profil géométrique pour éviter toute mutation globale."""
        return PROFIL_GEOMETRIE.copy()
