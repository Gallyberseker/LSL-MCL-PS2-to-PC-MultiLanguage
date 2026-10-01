"""Détecteurs partagés des images intégrées aux JAM."""
from functools import lru_cache
import re
from LSL_MCL_FORMATS import SIGNATURES_INCONNUES

_SIGNATURES = (
    (b"BM", "bmp_valide"), (b"DDS ", "dds_valide"),
    (b"\xff\xd8\xff", "jpg_valide"), (b"\x89PNG\r\n\x1a\n", "png_valide"),
    (b"GIF87a", "gif_valide"), (b"GIF89a", "gif_valide"),
    (b"RIFF", "webp_valide"), (b"\x00\x00\x01\x00", "ico_valide"),
)
SIGNATURES_IMAGES_RE = re.compile(b"|".join(re.escape(s) for s, _ in _SIGNATURES))
SIGNATURES_INCONNUES_RE = re.compile(b"|".join(re.escape(s) for s in SIGNATURES_INCONNUES))


@lru_cache(maxsize=1)
def obtenir_detecteurs():
    """Charge les validateurs au premier usage, sans initialisation du programme."""
    from LSL_MCL_IMAGE_VALIDATION import ValidationImages
    return {signature: getattr(ValidationImages, nom) for signature, nom in _SIGNATURES}
