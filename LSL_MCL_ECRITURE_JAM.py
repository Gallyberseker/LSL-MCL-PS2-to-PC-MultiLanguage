"""Remplacement d'un emplacement binaire dans un JAM."""
from pathlib import Path
import os
import shutil
import tempfile


def remplacer_emplacement(jam, offset, taille, payload):
    """Prépare et vérifie une copie avant de remplacer atomiquement le JAM.

    Le fichier original reste intact si la préparation échoue.
    """
    jam = Path(jam)
    if offset < 0 or taille <= 0 or len(payload) != taille:
        raise ValueError('Emplacement ou taille du payload incorrect.')
    if offset + taille > jam.stat().st_size:
        raise ValueError('Emplacement hors du fichier JAM.')
    descripteur, nom = tempfile.mkstemp(prefix='.injection_', suffix='.jam', dir=jam.parent)
    os.close(descripteur)
    temporaire = Path(nom)
    try:
        shutil.copy2(jam, temporaire)
        with temporaire.open('r+b') as flux:
            flux.seek(offset)
            flux.write(payload)
            flux.flush()
            flux.seek(offset)
            if flux.read(taille) != payload:
                raise OSError('Vérification de la copie JAM échouée.')
        os.replace(temporaire, jam)
    finally:
        temporaire.unlink(missing_ok=True)


def publier_jam(destination, donnees):
    """Vérifie une écriture complète avant de publier un JAM reconstruit.

    Accepte une taille différente pour les conteneurs dont les index ont
    déjà été recalculés et validés par le constructeur.
    """
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    descripteur, nom = tempfile.mkstemp(
        prefix=".jam_", suffix=".tmp", dir=destination.parent)
    temporaire = Path(nom)
    try:
        with os.fdopen(descripteur, "w+b") as flux:
            flux.write(donnees)
            flux.flush()
            flux.seek(0)
            if flux.read() != donnees:
                raise OSError("Vérification du JAM reconstruit échouée.")
        if destination.exists():
            shutil.copymode(destination, temporaire)
        os.replace(temporaire, destination)
    finally:
        temporaire.unlink(missing_ok=True)
