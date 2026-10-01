"""Façade de traduction des textes JAM PS2 vers PC, sans déplacement des chunks."""
from LSL_MCL_TEXTE_ANALYSE import AnalyseTextes
from LSL_MCL_TEXTE_ADAPTATION import AdaptationTextes
from LSL_MCL_TEXTE_MEMOIRE import MemoireTextes
from LSL_MCL_TEXTE_PAYLOAD import PayloadTextes
from LSL_MCL_TEXTE_APPLICATION import ApplicationTextes

class LSL_MCL_Textes(AnalyseTextes, AdaptationTextes, MemoireTextes, PayloadTextes, ApplicationTextes):
    """Expose les traitements textuels et leurs contrôles avec l’interface du projet."""
