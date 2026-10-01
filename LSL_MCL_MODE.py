"""Déblocage initial des options bonus dans les ressources PC."""

from pathlib import Path
import re

import LSL_MCL_VARIABLES as V
from LSL_MCL_ECRITURE_JAM import publier_jam


class LSL_MCL_Mode:
    """Débloque les options indépendamment du choix du joueur."""

    @staticmethod
    def debloquer_option(data_root):
        """Applique les déblocages initiaux activés, sans modifier les toggles.

        Les sauvegardes existantes conservent leurs propres valeurs.
        Une variable False conserve le réglage de la source utilisée.
        """
        options = (
            ('NudeActive', V.ACTIVATE_NUDE_MODE, 'NUDE MODE'),
            ('NaughtyActive', V.ACTIVATE_NAUGHTY_MODE, 'NAUGHTY MODE'),
        )
        if not any(actif for _, actif, _ in options):
            print('[MODES BONUS] Déblocages automatiques désactivés.')
            return False
        jam = Path(data_root) / 'JamFiles' / 'PC' / 'AppInit.JAM'
        original = jam.read_bytes()
        donnees = bytearray(original)
        messages = []
        for nom, actif, etiquette in options:
            if not actif:
                messages.append(f'[{etiquette}] Déblocage automatique désactivé.')
                continue
            motif = re.compile(
                rb'DataLink\s*\{\s*Name\s+"' + nom.encode('ascii') + rb'"\s+'
                rb'Type\s+Boolean\s+Parent\s+"SaveData\\"\s+'
                rb'Data\s+(?P<valeur>[01])\s*\}'
            )
            correspondances = list(motif.finditer(original))
            if len(correspondances) != 1:
                raise RuntimeError(
                    f'{etiquette} : déclaration {nom} absente ou ambiguë ; '
                    'AppInit.JAM conservé intact.'
                )
            cible = correspondances[0]
            donnees[cible.start('valeur')] = ord('1')
            messages.append(f'[{etiquette}] Option débloquée dans les valeurs initiales.')
        if donnees != original:
            publier_jam(jam, bytes(donnees))
        for message in messages:
            print(message)
        return True
