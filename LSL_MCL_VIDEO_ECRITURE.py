"""Publication des cinématiques SFD après leurs contrôles de reconstruction."""
from pathlib import Path
import os
import shutil
import tempfile


def publier_sfd(destination, *, source=None, donnees=None):
    """Prépare une copie ou des octets dans un fichier voisin avant remplacement atomique."""
    if (source is None) == (donnees is None):
        raise ValueError('Fournir une source ou des données SFD.')
    destination = Path(destination)
    temporaire = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=destination.name + '.', suffix='.tmp', delete=False) as flux:
            temporaire = Path(flux.name)
            if source is not None:
                with Path(source).open('rb') as entree:
                    shutil.copyfileobj(entree, flux, length=1024 * 1024)
            else:
                flux.write(donnees)
        if not temporaire.stat().st_size:
            raise ValueError('Publication SFD vide refusée.')
        shutil.copymode(destination, temporaire)
        os.replace(temporaire, destination)
    finally:
        if temporaire is not None:
            temporaire.unlink(missing_ok=True)
