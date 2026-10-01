"""Lecture des blocs JAM et normalisation des noms pour l'extraction."""
from pathlib import Path
import struct

import LSL_MCL_VARIABLES as V


class LSL_MCL_jams:
    """Expose les informations binaires utilisées par les traitements JAM."""

    @staticmethod
    def nom_jam(jam, jam_root):
        """Encode le chemin relatif du JAM avec des séparateurs doubles underscores."""
        return str(Path(jam).relative_to(Path(jam_root))).replace('\\', '__').replace('/', '__')

    @staticmethod
    def jam_chunks(data):
        """Repère les blocs dont l'en-tête et le payload tiennent dans les données.

        Retourne (offset en-tête, taille 1, taille 2, début payload, fin payload).
        Les deux tailles sont conservées pour les contrôles des appelants.
        Une signature incomplète est ignorée sans arrêter la recherche.
        """
        resultat = []
        position = 0
        longueur = len(data)
        while True:
            signature = data.find(V.SIG_JAM, position)
            if signature < 0:
                break
            position = signature + 1
            entete = signature - 8
            debut = entete + 32
            if entete < 0 or debut > longueur:
                continue
            taille1, taille2 = struct.unpack_from('<II', data, entete)
            fin = debut + taille1
            if fin <= longueur:
                resultat.append((entete, taille1, taille2, debut, fin))
        return resultat
