"""Service images : scan."""
import mmap
import struct
import LSL_MCL_VARIABLES as V
from LSL_MCL_IMAGE_DETECTION import (
    obtenir_detecteurs, SIGNATURES_IMAGES_RE, SIGNATURES_INCONNUES_RE,
)

class ScannerImages:
    """Opérations de scan des images du jeu."""

    @staticmethod
    def scanner_images_jam_mmap(jam, jam_root):
        """Détecte les images et signatures inconnues dans un JAM sans le charger intégralement."""
        detecteurs = obtenir_detecteurs()
        candidats = []
        inconnus = []
        if jam.stat().st_size == 0:
            return (candidats, inconnus)
        with jam.open('rb') as flux:
            with mmap.mmap(flux.fileno(), 0, access=mmap.ACCESS_READ) as data:
                for correspondance in SIGNATURES_IMAGES_RE.finditer(data):
                    signature = correspondance.group(0)
                    position = correspondance.start()
                    detecteur = detecteurs[signature]
                    try:
                        information = detecteur(data, position)
                    except (OSError, ValueError, TypeError, struct.error, OverflowError):
                        information = None
                    if information and information.get('taille', 0) > 0 and (position + information['taille'] <= len(data)):
                        candidats.append((position, information))
                for correspondance in SIGNATURES_INCONNUES_RE.finditer(data):
                    signature = correspondance.group(0)
                    position = correspondance.start()
                    inconnus.append({'jam': str(jam.relative_to(jam_root)), 'type': V.SIGNATURES_INCONNUES[signature], 'offset': position, 'offset_hex': f'0x{position:08X}'})
        return (candidats, inconnus)
