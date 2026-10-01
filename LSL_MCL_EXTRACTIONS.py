"""Interface des extractions PC et PS2 ; conserve les appels existants."""
from LSL_MCL_SOURCE_PS2 import SourcePs2
from LSL_MCL_EXTRACTION_IMAGES import ExtractionImages
from LSL_MCL_INDEX_JAM import IndexJam

class LSL_MCL_Extractions(SourcePs2, ExtractionImages, IndexJam):
    """Compose la préparation PS2, les extractions d’images et les index JAM."""
