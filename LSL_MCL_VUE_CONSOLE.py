"""Interface console du moteur de localisation Larry MCL."""


class VueConsole:
    """Présente le menu et recueille les choix sans lancer de traitement."""

    @staticmethod
    def logo():
        """Affiche l'identité du programme."""
        print("")
        print("   ██████╗  █████╗ ██╗     ██╗  ██╗   ██╗")
        print("  ██╔════╝ ██╔══██╗██║     ██║  ╚██╗ ██╔╝")
        print("  ██║  ███╗███████║██║     ██║   ╚████╔╝")
        print("  ██║   ██║██╔══██║██║     ██║    ╚██╔╝")
        print("  ╚██████╔╝██║  ██║███████╗███████╗██║")
        print("   ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝")
        print("")

    @staticmethod
    def titre(texte):
        """Affiche le titre d'une étape encadré de séparateurs."""
        print()
        print("=" * 70)
        print(texte)
        print("=" * 70)

    @staticmethod
    def log(texte):
        """Affiche un message de traitement."""
        print(texte)

    @staticmethod
    def afficher_menu():
        """Présente les options disponibles dans la console."""
        VueConsole.titre("LARRY MCL — LOCALISATION MULTILINGUE")
        for ligne in (
            "[1] Construire la version localisée complète",
            "[2] Extraire toutes les images",
            "[3] Injecter toutes les images",
            "",
            "[4] Vérifier les outils et les sources PC/PS2",
            "[5] Préparer les textes et images localisés dans TEMP",
            "",
            "[6] Diagnostic complet",
            "[7] Diagnostic vidéo et audio",
            "[8] Diagnostic des textes",
            "[9] Diagnostic des menus",
            "",
            "[10] Restaurer les données PC depuis le backup",
            "[11] Installer la version finalisée dans le jeu PC",
            "[12] 📐 Afficher le chemin du guide de réglage géométrique",
            "",
            "[0] Quitter",
        ):
            print(ligne)

    @staticmethod
    def demander_choix():
        """Lit et nettoie le choix saisi par l'utilisateur."""
        return input("\nChoix : ").strip()

    @staticmethod
    def attendre_retour():
        """Suspend l'affichage jusqu'à la demande d'un nouveau menu."""
        input("\nAppuyez sur Entrée pour revenir au menu...")
