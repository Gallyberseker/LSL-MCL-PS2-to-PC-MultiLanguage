"""Façade compatible avec les appels historiques à LSL_MCL_Menu."""
from LSL_MCL_VUE_CONSOLE import VueConsole


class LSL_MCL_Menu:
    """Maintient les anciennes entrées du menu après séparation MVC."""

    @staticmethod
    def titre(texte):
        """Présente un titre sur la vue console."""
        VueConsole.titre(texte)

    @staticmethod
    def logo():
        """Présente le logo sur la vue console."""
        VueConsole.logo()

    @staticmethod
    def log(texte):
        """Présente un message sur la vue console."""
        VueConsole.log(texte)

    @staticmethod
    def executer_fonction_optionnelle(nom, *arguments):
        """Résout et lance une opération facultative par son ancien nom."""
        from LSL_MCL_ROUTAGE import LSL_MCL_Routages
        fonction = LSL_MCL_Routages.resoudre_option(nom)
        if not callable(fonction):
            VueConsole.log(f"\n[EN PREPARATION] {nom}\nLa place est reservee dans le menu.")
            return False
        resultat = fonction(*arguments)
        return resultat is not False

    @staticmethod
    def menu(game_root, ps2_ok):
        """Délègue la boucle interactive au contrôleur du programme."""
        from LSL_MCL_CONTROLEUR import ControleurMenu
        ControleurMenu(VueConsole()).executer(game_root, ps2_ok)
