"""Coordination de la géométrie et publication des JAM préparés."""
from pathlib import Path
import os
import shutil
import tempfile

from LSL_MCL_GEOMETRIE_RECTANGLES import patch_geometrie_v3 as preparer_geometrie
from LSL_MCL_GEOMETRIE_POLICES import appliquer_polices_par_langue as preparer_polices


def _appliquer(operation, data_root, *arguments):
    """Prépare tous les JAM, puis remplace les fichiers avec retour arrière.

    Les erreurs de préparation ne modifient aucun original. Les remplacements
    sont atomiques par fichier. Une erreur de publication restaure les fichiers
    déjà remplacés ; une interruption du processus ne garantit pas ce retour.
    """
    racine = Path(data_root)
    dossier = racine / 'JamFiles' / 'PC'
    if not dossier.is_dir():
        return operation(racine, *arguments)
    with tempfile.TemporaryDirectory(prefix='.geometrie-', dir=racine) as temporaire:
        travail = Path(temporaire) / 'travail'
        sauvegarde = Path(temporaire) / 'sauvegarde'
        fichiers = sorted(p for p in dossier.rglob('*')
                          if p.is_file() and p.suffix.lower() == '.jam')
        for fichier in fichiers:
            relatif = fichier.relative_to(racine)
            for destination in (travail / relatif, sauvegarde / relatif):
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(fichier, destination)
        operation(travail, *arguments)
        modifications = []
        for fichier in fichiers:
            relatif = fichier.relative_to(racine)
            prepare = travail / relatif
            if prepare.read_bytes() != (sauvegarde / relatif).read_bytes():
                if fichier.read_bytes() != (sauvegarde / relatif).read_bytes():
                    raise RuntimeError(f'JAM modifié pendant la préparation : {fichier}')
                modifications.append((fichier, prepare, sauvegarde / relatif))
        publies = []
        try:
            for fichier, prepare, original in modifications:
                os.replace(prepare, fichier)
                publies.append((fichier, original))
        except BaseException:
            for fichier, original in reversed(publies):
                os.replace(original, fichier)
            raise


class LSL_MCL_Geometries:
    """Expose les opérations géométriques au moteur de localisation."""

    @staticmethod
    def patch_geometrie_v3(data_root, langue_cible=None):
        """Prépare les rectangles et les polices avant de publier les JAM."""
        return _appliquer(preparer_geometrie, data_root, langue_cible)

    @staticmethod
    def appliquer_polices_par_langue(data_root, profil, langue):
        """Prépare et publie uniquement les styles individuels de la langue."""
        return _appliquer(preparer_polices, data_root, profil, langue)

    @staticmethod
    def generer_guide_geometrie():
        """Retourne le guide statique livré avec les modules de géométrie."""
        fichier = Path(__file__).with_name('GUIDE_GEOMETRIE_LARRY_MCL.txt')
        print('[GUIDE GEOMETRIE] Tutoriel :', fichier)
        return fichier

    @staticmethod
    def aligner(valeur, alignement):
        """Arrondit un offset au multiple supérieur de l'alignement demandé."""
        return ((valeur + alignement - 1) // alignement) * alignement
