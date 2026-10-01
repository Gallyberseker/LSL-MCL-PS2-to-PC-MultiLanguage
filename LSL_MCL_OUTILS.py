"""Façade des outils : installation, fichiers, sources PC et exécution."""
from LSL_MCL_OUTILS_INSTALLATION import InstallationOutils
from LSL_MCL_OUTILS_FICHIERS import OperationsFichiers
from LSL_MCL_OUTILS_SOURCES import SourcesPC
from LSL_MCL_OUTILS_EXECUTION import ExecutionOutils

class LSL_MCL_Outils(InstallationOutils, OperationsFichiers, SourcesPC, ExecutionOutils):
    """Expose les services communs avec l’interface historique du projet."""
