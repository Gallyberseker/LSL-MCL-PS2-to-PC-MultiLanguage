"""Options, chemins et état partagé du moteur Larry MCL."""
from pathlib import Path
import re
import struct

from LSL_MCL_FORMATS import (
    SFD_NON_VOCAUX,
    FORMATS_IMAGES,
    SIGNATURES_INCONNUES,
    EXT_IMAGES,
    SIG_JAM,
    ENTRY,
    GLYPH,
    ACCENT,
    PC_KEYS,
    MAX_TEXTE_AIS,
    JETON_COMMANDE_JAM,
    MARQUEURS_CONSOLE_PC,
    RACCORDS_CONSOLE_PC,
    MOTS_LIAISON_FIN_PC,
    SECTOR_SIZE,
)

import LSL_MCL_PROFIL_LANGUE_RU as _langue_ru
import LSL_MCL_PROFIL_LANGUE_FR as _langue_fr
import LSL_MCL_PROFIL_LANGUE_EN as _langue_en
import LSL_MCL_PROFIL_LANGUE_DE as _langue_de
import LSL_MCL_PROFIL_LANGUE_ES as _langue_es
import LSL_MCL_PROFIL_LANGUE_IT as _langue_it

ACTIVE_VIDEO_ENCODAGE = True

ACTIVE_AUDIO_BUILD = True

ACTIVE_IMAGE_EXTRACTION = True

ACTIVE_REFERENCES_TECHNIQUES = True

ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD = True

ACTIVE_TRADUCTION_TEXTE_JAM = True

ACTIVE_TELECHARGEMENT_OUTILS = True

ACTIVE_GEOMETRIE = True

# Débloque initialement le mode nu ; le joueur choisit son activation.
ACTIVATE_NUDE_MODE = False
ACTIVATE_NAUGHTY_MODE = False

# État modifiable par le menu et le parcours de construction.
LANGUE_CIBLE = "fr"

EDITIONS_PS2 = {
    identifiant: edition
    for module in (_langue_ru, _langue_en, _langue_fr, _langue_de, _langue_es, _langue_it)
    for identifiant, edition in module.EDITIONS_PS2.items()
}

_PROFILS = {
    'ru': _langue_ru,
    'fr': _langue_fr,
    'en': _langue_en,
    'de': _langue_de,
    'es': _langue_es,
    'it': _langue_it
}
PROFILS_LANGUES = {code: module.PROFIL_DETECTION for code, module in _PROFILS.items()}

MARQUEURS_BACKUP_DISABLE = {
    code: _PROFILS[code].MARQUEUR_BACKUP_DISABLE
    for code in ('fr', 'en', 'de', 'it', 'es')
}

GAME_NAME = ("Leisure Suit Larry - Magna Cum Laude "
             "Uncut and Uncensored")

# La racine reste celle de ce fichier, quel que soit le répertoire courant.
ROOT = Path(__file__).resolve().parent

VENDOR = ROOT / "_vendor"

PC_VERSION_BACKUP = ROOT / "PC_VERSION_BACKUP"

PC_VERSION = ROOT / "PC_VERSION"

PS2_VERSION = ROOT / "PS2_VERSION"

EDIT = ROOT / "EDITION_IMAGE"

IMAGE_EXTRACT = (EDIT / "All_Image_extract")

IMAGE_INJECT = (EDIT / "All_Image_Inject")

MANIFEST = (EDIT / "emplacement_image.json")

UNKNOWN_IMAGES = (EDIT / "signatures_images_non_prises_en_charge.json")

PC_VERSION_EDIT_TEMPS = (ROOT / "PC_VERSION_EDIT_TEMPS")

PC_VERSION_EDIT_FINI = (ROOT / "PC_VERSION_EDIT_FINI")

OUTILS = ROOT / "OUTILS"

RAPPORTS = ROOT / "RAPPORTS"

CONFIG = ROOT / "Locate_Game_Folder.json"

AFSPACKER_DIR = OUTILS

SFD_MUXER_C_DIR = OUTILS

SFD_TEMP = ROOT / "_TEMP_SFD"

MARQUEUR_LOCALISATION_PC = "Larry_MCL_Localisation.txt"

ALIASES_AUDIO_LANGUE = {
    code: _PROFILS[code].ALIASES_AUDIO
    for code in ('fr', 'en', 'de', 'es', 'it')
}

_CACHE_SHA256_FICHIERS = {}

_IMAGES_SIERRA = {
    'BASE64_IMG_RU_ALLRIGHT_SIERRA': 'SIERRA_RU.b64',
    'BASE64_IMG_FR_ALLRIGHT_SIERRA': 'SIERRA_FR.b64',
    'BASE64_IMG_ES_ALLRIGHT_SIERRA': 'SIERRA_ES.b64',
    'BASE64_IMG_DE_ALLRIGHT_SIERRA': 'SIERRA_DE.b64',
    'BASE64_IMG_IT_ALLRIGHT_SIERRA': 'SIERRA_IT.b64',
    'BASE64_IMG_EN_ALLRIGHT_SIERRA': 'SIERRA_EN.b64',
}

def __getattr__(nom):
    """Charge une image Sierra à son premier accès en conservant son ancien nom."""
    if nom not in _IMAGES_SIERRA:
        raise AttributeError(f"Le module {__name__!r} ne contient pas {nom!r}.")
    fichier = Path(__file__).resolve().parent / "RESSOURCES_SIERRA" / _IMAGES_SIERRA[nom]
    valeur = fichier.read_text(encoding="ascii")
    globals()[nom] = valeur
    return valeur

