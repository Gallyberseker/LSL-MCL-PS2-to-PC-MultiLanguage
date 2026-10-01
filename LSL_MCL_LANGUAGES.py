"""Interface des services de langues de Larry MCL."""
from LSL_MCL_LANGUE_DETECTION import DetectionLangues
from LSL_MCL_LANGUE_MENU import MenuLangues

class LSL_MCL_Languages(DetectionLangues, MenuLangues):
    """Interface commune des services de langues du projet."""
