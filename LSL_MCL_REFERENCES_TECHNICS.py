"""Contrôle les références de ressources dans les JAM après localisation."""
from pathlib import Path
import re


class LSL_MCL_References_technics:
    """Bloque la construction si de nouvelles références techniques apparaissent."""

    _CHAINES_ASCII = re.compile(rb'[\x20-\x7E]{4,260}')
    _MOTIFS = (
        b'.AOS', b'.AFS', b'.ADX', b'.AHX', b'.SFD',
        b'.JAM', b'.DDS', b'.BMP', b'.AGI', b'.AGM',
        b'$FX', b'SFX\\', b'SFX/',
    )

    @classmethod
    def _extraire_references(cls, data):
        """Recense les chaînes ASCII contenant un nom ou un marqueur de ressource."""
        resultat = set()
        for match in cls._CHAINES_ASCII.finditer(data):
            chaine = match.group(0)
            upper = chaine.upper()
            if any(motif in upper for motif in cls._MOTIFS):
                resultat.add(chaine)
        return resultat

    @classmethod
    def verifier_references_techniques(cls, backup_data, final_data):
        """Compare les JAM communs et lève RuntimeError si une référence est nouvelle.

        Les chaînes originales restent comparées octet par octet. La recherche
        des marqueurs ignore la casse, comme celle de l'extension des fichiers.
        Ce contrôle ne vérifie pas l'existence des ressources référencées ni
        les JAM absents de l'une des deux versions.
        """
        from LSL_MCL_MENU import LSL_MCL_Menu

        LSL_MCL_Menu.titre('VERIFICATION DES REFERENCES TECHNIQUES')
        backup_jam = Path(backup_data) / 'JamFiles' / 'PC'
        final_jam = Path(final_data) / 'JamFiles' / 'PC'
        problemes = 0
        compares = 0
        for original in backup_jam.rglob('*'):
            if not original.is_file() or original.suffix.lower() != '.jam':
                continue
            relatif = original.relative_to(backup_jam)
            modifie = final_jam / relatif
            if not modifie.is_file():
                continue
            originales = cls._extraire_references(original.read_bytes())
            modifiees = cls._extraire_references(modifie.read_bytes())
            compares += 1
            nouvelles = modifiees - originales
            if nouvelles and problemes == 0:
                print('ATTENTION : nouvelles références techniques détectées.')
            for chaine in sorted(nouvelles):
                print('[TECHNIQUE]', relatif, '=>', repr(chaine))
                problemes += 1
        print(f'[TECHNIQUE] {compares} JAM comparé(s).')
        if problemes:
            raise RuntimeError(
                f'Compilation arrêtée : {problemes} référence(s) technique(s) '
                'ajoutée(s) ou modifiée(s).'
            )
        if compares:
            print('Aucune nouvelle référence technique suspecte.')
        else:
            print('[TECHNIQUE] Aucun JAM commun : contrôle non effectué.')
