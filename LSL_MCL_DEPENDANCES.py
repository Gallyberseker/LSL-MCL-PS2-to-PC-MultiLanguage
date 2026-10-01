"""Vérification et installation des bibliothèques Python requises par le moteur."""

import importlib
from importlib import metadata
import subprocess
import sys

import LSL_MCL_VARIABLES as V


class LSL_MCL_Dependances:
    """Installe les dépendances dans l'interpréteur qui lance le projet."""

    GOOGLETRANS_VERSION = "4.0.2"

    @staticmethod
    def _installer(paquet, mise_a_jour=False):
        """Installe un paquet si le téléchargement est autorisé ; renvoie un booléen."""
        if getattr(sys, "frozen", False):
            print("[DEPENDANCE] Paquet absent du programme :", paquet)
            print("[DEPENDANCE] Recompilez le programme avec COMPILER_WINDOWS.bat.")
            return False
        if not V.ACTIVE_TELECHARGEMENT_OUTILS:
            print("[DEPENDANCE] Installation automatique désactivée.")
            return False
        commande = [sys.executable, "-m", "pip", "install"]
        if mise_a_jour:
            commande.append("--upgrade")
        commande.append(paquet)
        print("[DEPENDANCE] Installation automatique de", paquet, "...")
        try:
            subprocess.check_call(commande)
        except (OSError, subprocess.CalledProcessError) as erreur:
            print("[DEPENDANCE] ERREUR installation", paquet, ":", erreur)
            print(f'Installation manuelle : "{sys.executable}" -m pip install {paquet}')
            return False
        importlib.invalidate_caches()
        return True

    @classmethod
    def verifier_pillow(cls):
        """Vérifie ou installe Pillow pour le traitement des images."""
        try:
            importlib.import_module("PIL")
        except ImportError:
            print("[DEPENDANCE] Pillow : INTROUVABLE OU IMPORT IMPOSSIBLE")
        else:
            print("[DEPENDANCE] Pillow : OK")
            return True
        if not cls._installer("Pillow"):
            return False
        try:
            importlib.import_module("PIL")
        except (ImportError, OSError) as erreur:
            print("[DEPENDANCE] ERREUR chargement Pillow :", erreur)
            return False
        print("[DEPENDANCE] Pillow : INSTALLE")
        return True

    @classmethod
    def verifier_googletrans(cls):
        """Vérifie la version imposée et l'import de Translator.

        Une installation alors que googletrans était déjà chargé exige un
        redémarrage ; False empêche de valider l'ancien code resté en mémoire.
        """
        deja_charge = any(nom == "googletrans" or nom.startswith("googletrans.")
                          for nom in sys.modules)
        try:
            version = metadata.version("googletrans")
            if version == cls.GOOGLETRANS_VERSION:
                from googletrans import Translator  # noqa: F401
                print("[DEPENDANCE] googletrans", version, ": OK")
                return True
            print("[DEPENDANCE] googletrans", version, ": version incompatible")
        except (ImportError, OSError) as erreur:
            print("[DEPENDANCE] googletrans : indisponible :", erreur)
        paquet = f"googletrans=={cls.GOOGLETRANS_VERSION}"
        # Un import échoué peut avoir chargé certains sous-modules.
        deja_charge = deja_charge or any(
            nom == "googletrans" or nom.startswith("googletrans.")
            for nom in sys.modules)
        if not cls._installer(paquet, mise_a_jour=True):
            return False
        try:
            if metadata.version("googletrans") != cls.GOOGLETRANS_VERSION:
                raise RuntimeError("Version installée différente de " + cls.GOOGLETRANS_VERSION)
            if deja_charge:
                print("[DEPENDANCE] googletrans installé ; redémarrez l'utilitaire "
                      "pour charger la version installée.")
                return False
            from googletrans import Translator  # noqa: F401
        except (ImportError, OSError, RuntimeError) as erreur:
            print("[DEPENDANCE] ERREUR vérification googletrans :", erreur)
            return False
        print("[DEPENDANCE] googletrans : INSTALLE")
        return True

    @classmethod
    def verifier_dependances(cls):
        """Vérifie les dépendances nécessaires aux options actives."""
        print()
        print("=" * 70)
        print("VERIFICATION DES DEPENDANCES")
        print("=" * 70)
        pillow_ok = cls.verifier_pillow() if V.ACTIVE_IMAGE_EXTRACTION else True
        googletrans_ok = cls.verifier_googletrans() if V.ACTIVE_TRADUCTION_TEXTE_JAM else True
        print("=" * 70)
        if pillow_ok and googletrans_ok:
            print("[DEPENDANCES] Toutes les dépendances requises sont disponibles.")
        else:
            manquantes = []
            if not pillow_ok:
                manquantes.append("Pillow")
            if not googletrans_ok:
                manquantes.append("googletrans")
            print("[DEPENDANCES] Dépendances indisponibles dans cette session :",
                  ", ".join(manquantes))
            if not googletrans_ok:
                print("[DEPENDANCES] Traduction manuelle du catalogue toujours possible.")
        print("=" * 70)
        print()
        return pillow_ok and googletrans_ok
