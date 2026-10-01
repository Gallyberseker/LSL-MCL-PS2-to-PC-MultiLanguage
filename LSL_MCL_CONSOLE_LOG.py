"""Duplication de stdout et stderr vers un journal numéroté par lancement."""

import atexit
import sys
from pathlib import Path
from threading import RLock


class LSL_MCL_Console_log:
    """Conserve l'affichage du terminal et enregistre les sorties Python.

    Les sorties des programmes externes doivent être récupérées par le moteur
    puis écrites dans stdout ou stderr pour apparaître dans le journal.
    """

    _session = None
    _verrou = RLock()

    def __init__(self, console, fichier):
        """Associe un flux console au fichier partagé par stdout et stderr."""
        self.console = console
        self.fichier = fichier

    @property
    def encoding(self):
        """Expose l'encodage du terminal d'origine."""
        return getattr(self.console, "encoding", None)

    @property
    def errors(self):
        """Expose la politique de traitement des erreurs du terminal."""
        return getattr(self.console, "errors", None)

    def fileno(self):
        """Renvoie le descripteur du terminal, si celui-ci en possède un."""
        return self.console.fileno()

    def write(self, texte):
        """Écrit dans les deux sorties et renvoie le nombre de caractères."""
        with self._verrou:
            self.fichier.write(texte)
            self.fichier.flush()
            self.console.write(texte)
        return len(texte)

    def flush(self):
        """Force l'écriture du journal et du terminal."""
        with self._verrou:
            self.fichier.flush()
            self.console.flush()

    def isatty(self):
        """Conserve le comportement du terminal pour les barres de progression."""
        return self.console.isatty()

    @staticmethod
    def activer_log_console():
        """Active le journal de stdout et stderr et renvoie son fichier.

        Une activation répétée réutilise le journal actif. La création exclusive
        évite d'écraser un journal lorsqu'un autre lancement choisit le même
        numéro. Chaque écriture est immédiatement transmise au fichier.
        """
        cls = LSL_MCL_Console_log
        with cls._verrou:
            if cls._session is not None:
                fichier, _, _ = cls._session
                if not fichier.closed:
                    return fichier
                cls.desactiver_log_console()

            dossier = Path(__file__).resolve().parent / "CONSOLE_LOGS"
            dossier.mkdir(parents=True, exist_ok=True)
            numero = 1
            while True:
                chemin = dossier / f"console_numero_{numero}.log"
                try:
                    fichier = chemin.open(
                        "x", encoding="utf-8", errors="backslashreplace", buffering=1)
                    break
                except FileExistsError:
                    numero += 1

            sortie = cls(sys.stdout, fichier)
            erreur = cls(sys.stderr, fichier)
            cls._session = (fichier, sortie, erreur)
            sys.stdout, sys.stderr = sortie, erreur
            print("=" * 70)
            print("JOURNAL CONSOLE")
            print("=" * 70)
            print(f"Numero  : {numero}")
            print(f"Fichier : {chemin}")
            print("=" * 70)
            print()
            return fichier

    @staticmethod
    def desactiver_log_console():
        """Restaure les flux remplacés par ce module, puis ferme le journal.

        Un flux remplacé depuis par un autre composant n'est pas réaffecté.
        L'appel est sans effet si aucune session n'est active.
        """
        cls = LSL_MCL_Console_log
        with cls._verrou:
            if cls._session is None:
                return
            fichier, sortie, erreur = cls._session
            if sys.stdout is sortie:
                sys.stdout = sortie.console
            if sys.stderr is erreur:
                sys.stderr = erreur.console
            cls._session = None
            fichier.close()


atexit.register(LSL_MCL_Console_log.desactiver_log_console)
