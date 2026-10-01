"""Point d’entrée du projet MVC Larry MCL."""
from LSL_MCL_CONSOLE_LOG import LSL_MCL_Console_log
from LSL_MCL_DEPENDANCES import LSL_MCL_Dependances


def main():
    """Vérifie Pillow avant de charger le moteur et renvoie le code de sortie."""
    LSL_MCL_Console_log.activer_log_console()
    # Les modules image chargent Pillow même si l’extraction est désactivée.
    if not LSL_MCL_Dependances.verifier_pillow():
        return 1
    from LSL_MCL_MAIN import LSL_MCL_Main
    LSL_MCL_Main.demarrer()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
