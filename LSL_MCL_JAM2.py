"""Lecture et reconstruction du format JAM2, indépendantes de l’audio."""
from pathlib import Path
import struct

class LSL_MCL_Jam2:
    """Lit et reconstruit les conteneurs JAM2 utilisés par les services du moteur."""

    @staticmethod
    def _jam2_acx_u16(donnees, position):
        """Lit un entier non signé de 16 bits dans une ressource ACX."""
        return struct.unpack_from('<H', donnees, position)[0]

    @staticmethod
    def _jam2_acx_u32(donnees, position):
        """Lit un entier non signé de 32 bits dans une ressource ACX."""
        return struct.unpack_from('<I', donnees, position)[0]

    @staticmethod
    def _jam2_acx_p32(valeur):
        """Écrit un entier non signé de 32 bits dans une ressource ACX."""
        return struct.pack('<I', valeur)

    @staticmethod
    def _jam2_acx_lire(path):
        """Lit un JAM2 et retourne ses octets, sa table et ses blocs modifiables.

Refuse les en-têtes tronqués, tables hors fichier et blocs chevauchants.
Les références sentinelles restent traitées comme dans le lecteur original."""
        path = Path(path)
        donnees = path.read_bytes()
        if len(donnees) < 32:
            raise ValueError(f'{path.name}: en-tête JAM2 tronqué')
        if donnees[:4] != b'JAM2':
            raise ValueError(f'{path.name}: signature JAM2 absente')
        first = LSL_MCL_Jam2._jam2_acx_u32(donnees, 8)
        nb_noms = LSL_MCL_Jam2._jam2_acx_u16(donnees, 28)
        nb_ext = LSL_MCL_Jam2._jam2_acx_u16(donnees, 30)
        noms = [donnees[32 + i * 8:32 + (i + 1) * 8].rstrip(b'\x00 ').decode('latin-1') for i in range(nb_noms)]
        base_ext = 32 + nb_noms * 8
        extensions = [donnees[base_ext + i * 4:base_ext + (i + 1) * 4].rstrip(b'\x00 ').decode('latin-1') for i in range(nb_ext)]
        meta = 32 + nb_noms * 8 + nb_ext * 4
        if meta + 4 > len(donnees) or first > len(donnees) or first < meta + 4 or (first - (meta + 4)) % 8:
            raise ValueError('Table JAM2 incoherente.')
        count = (first - (meta + 4)) // 8
        table = []
        noms_par_offset = {}
        for i in range(count):
            q = meta + 4 + i * 8
            fid = LSL_MCL_Jam2._jam2_acx_u16(donnees, q)
            eid = LSL_MCL_Jam2._jam2_acx_u16(donnees, q + 2)
            off = LSL_MCL_Jam2._jam2_acx_u32(donnees, q + 4)
            table.append([fid, eid, off, q + 4])
            if fid < len(noms) and eid < len(extensions):
                cle = (noms[fid].upper(), extensions[eid].upper())
                noms_par_offset.setdefault(off, []).append(cle)
        offsets = sorted({x[2] for x in table if first <= x[2] < len(donnees)})
        blocs = []
        for i, off in enumerate(offsets):
            if off + 32 > len(donnees):
                raise ValueError('Bloc JAM2 tronque.')
            cs = LSL_MCL_Jam2._jam2_acx_u32(donnees, off)
            ds = LSL_MCL_Jam2._jam2_acx_u32(donnees, off + 4)
            suivant = offsets[i + 1] if i + 1 < len(offsets) else len(donnees)
            fin_data = off + 32 + cs
            if fin_data > suivant:
                raise ValueError(f'Bloc chevauche a 0x{off:X}')
            blocs.append({'old': off, 'header': bytearray(donnees[off:off + 32]), 'data': bytearray(donnees[off + 32:fin_data]), 'tail': bytes(donnees[fin_data:suivant]), 'cs': cs, 'ds': ds, 'cles': noms_par_offset.get(off, [])})
        return {'raw': donnees, 'first': first, 'meta': meta, 'table': table, 'blocs': blocs}

    @staticmethod
    def _jam2_acx_reconstruire(jam):
        """Reconstruit les blocs JAM2 et actualise leurs offsets dans la table.

Conserve l’alignement historique ; refuse le redimensionnement des blocs
compressés. Le service appelant contrôle l’identité avant modification."""
        prefix = bytearray(jam['raw'][:jam['first']])
        anciens_vers_nouveaux = {}
        body = bytearray()
        for i, bloc in enumerate(jam['blocs']):
            nouvel_offset = jam['first'] + len(body)
            anciens_vers_nouveaux[bloc['old']] = nouvel_offset
            header = bytearray(bloc['header'])
            header[0:4] = LSL_MCL_Jam2._jam2_acx_p32(len(bloc['data']))
            if bloc['cs'] == bloc['ds']:
                header[4:8] = LSL_MCL_Jam2._jam2_acx_p32(len(bloc['data']))
            elif len(bloc['data']) != bloc['cs']:
                raise ValueError(f"Bloc compresse modifie a 0x{bloc['old']:X}: abandon securite.")
            body += header + bloc['data']
            if i + 1 < len(jam['blocs']):
                pad = (4 - len(bloc['data']) % 4) % 4
                if pad:
                    body += b'\xff' + b'\x00' * (pad - 1)
        for _, _, ancien, champ in jam['table']:
            if ancien in anciens_vers_nouveaux:
                prefix[champ:champ + 4] = LSL_MCL_Jam2._jam2_acx_p32(anciens_vers_nouveaux[ancien])
        return bytes(prefix + body)
