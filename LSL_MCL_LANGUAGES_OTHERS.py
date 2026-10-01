"""Interface des services de langues de Larry MCL."""
import re
import LSL_MCL_VARIABLES as V
from LSL_MCL_LANGUE_CATALOGUE import CatalogueLangue
from LSL_MCL_LANGUE_PROTECTION import ProtectionTraduction
from LSL_MCL_LANGUE_TRADUCTION import TraductionLangue
from LSL_MCL_LANGUE_APPLICATION import ApplicationLangue

class LSL_MCL_Languages_others(CatalogueLangue, ProtectionTraduction, TraductionLangue, ApplicationLangue):
    """Interface commune des services de langues du projet."""
    CATALOGUE_LEGACY = V.ROOT / 'LSL_MCL_others_language.json'
    CATALOGUE = CATALOGUE_LEGACY
    VARIABLES = re.compile('%(?:\\d+\\$)?[-+#0 ]?\\d*(?:\\.\\d+)?[A-Za-z%]|\\\\[nr]|\\{[A-Za-z_]\\w*\\}')
    FORMATS_DATE = re.compile('(?<![A-Za-z])(?:YYYY|YY|MM|DD|hh|mm|ss|N)(?![A-Za-z])')
    BOUTONS = re.compile('[ÀÁÂÃÄ¿±°²³¹»¸º´µ¶·]')
    LANGUE_RE = re.compile('[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*')
