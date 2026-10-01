"""Lecture, reconstruction et correspondance des entrées AFS."""
from pathlib import Path
import struct
import LSL_MCL_VARIABLES as V
import LSL_MCL_LANGUAGES
import LSL_MCL_TEXTES

def _aligner(position, alignement):
    """Arrondit une position au prochain multiple d’alignement."""
    return (position + alignement - 1) // alignement * alignement

class LSL_MCL_Afs:
    """Traitements AFS hérités par LSL_MCL_Audios."""

    @classmethod
    def lire_afs(cls, data):
        """Lit les entrées, les noms et les données AFS ; rejette les en-têtes tronqués et les entrées hors fichier."""
        if len(data) < 8:
            raise ValueError('En-tête AFS tronqué')
        if data[:4] != b'AFS\x00':
            raise ValueError('AFS invalide')
        nombre = struct.unpack_from('<I', data, 4)[0]
        if nombre <= 0 or nombre > 100000:
            raise ValueError('Nombre AFS invalide')
        if 8 + nombre * 8 > len(data):
            raise ValueError('Table des entrées AFS tronquée')
        entrees = []
        p = 8
        for _ in range(nombre):
            offset, taille = struct.unpack_from('<II', data, p)
            entrees.append((offset, taille))
            p += 8
        table_offset = 0
        table_size = 0
        if p + 8 <= len(data):
            table_offset, table_size = struct.unpack_from('<II', data, p)
        noms = ['' for _ in range(nombre)]
        table = b''
        if table_offset > 0 and table_size > 0 and (table_offset + table_size <= len(data)):
            table = data[table_offset:table_offset + table_size]
            if len(table) >= nombre * 48:
                for i in range(nombre):
                    rec = table[i * 48:i * 48 + 32]
                    noms[i] = rec.split(b'\x00', 1)[0].decode('latin1', errors='ignore')
        payloads = []
        for offset, taille in entrees:
            if offset + taille > len(data):
                raise ValueError('Entree AFS hors fichier')
            payloads.append(data[offset:offset + taille])
        alignement = 2048
        offsets_valides = [offset for offset, taille in entrees if offset > 0]
        for candidat in (2048, 1024, 256, 128, 32):
            if offsets_valides and sum((1 for offset in offsets_valides if offset % candidat == 0)) / len(offsets_valides) >= 0.9:
                alignement = candidat
                break
        return {'count': nombre, 'entries': entrees, 'payloads': payloads, 'names': noms, 'table': table, 'table_offset': table_offset, 'table_size': table_size, 'alignment': alignement}

    @classmethod
    def construire_afs(cls, template, nouveaux_payloads):
        """Reconstruit une banque AFS en conservant les noms et l’alignement du modèle."""
        info = cls.lire_afs(template)
        if len(nouveaux_payloads) != info['count']:
            raise ValueError('Nombre de fichiers AFS incorrect')
        nombre = info['count']
        header_fin = 8 + nombre * 8 + 8
        premier_offset = min((offset for offset, taille in info['entries'] if offset > 0), default=_aligner(header_fin, info['alignment']))
        premier_offset = max(premier_offset, _aligner(header_fin, info['alignment']))
        sortie = bytearray(template[:min(premier_offset, len(template))])
        if len(sortie) < premier_offset:
            sortie.extend(b'\x00' * (premier_offset - len(sortie)))
        nouvelles_entrees = []
        position = premier_offset
        for payload in nouveaux_payloads:
            position = _aligner(position, info['alignment'])
            if len(sortie) < position:
                sortie.extend(b'\x00' * (position - len(sortie)))
            offset = position
            sortie.extend(payload)
            position += len(payload)
            nouvelles_entrees.append((offset, len(payload)))
        table_offset = 0
        table_size = 0
        if info['table']:
            position = _aligner(len(sortie), info['alignment'])
            if len(sortie) < position:
                sortie.extend(b'\x00' * (position - len(sortie)))
            table_offset = position
            table = bytearray(info['table'])
            if len(table) >= nombre * 48:
                for i, payload in enumerate(nouveaux_payloads):
                    struct.pack_into('<I', table, i * 48 + 44, len(payload))
            sortie.extend(table)
            table_size = len(table)
        sortie[0:4] = b'AFS\x00'
        struct.pack_into('<I', sortie, 4, nombre)
        p = 8
        for offset, taille in nouvelles_entrees:
            struct.pack_into('<II', sortie, p, offset, taille)
            p += 8
        struct.pack_into('<II', sortie, p, table_offset, table_size)
        return bytes(sortie)

    @classmethod
    def nom_afs(cls, nom):
        """Normalise un nom d’entrée AFS pour comparer les ressources PC et PS2."""
        return nom.replace('\\', '/').strip().lower()

    @classmethod
    def marqueurs_audio_langue(cls, langue_cible):
        """Retourne ou construit les marqueurs audio langue."""
        langue = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible)
        return V.ALIASES_AUDIO_LANGUE.get(langue, (langue,))

    @classmethod
    def choisir_entree_audio_langue(cls, noms, nom_pc, langue_cible):
        """Sélectionne entree audio langue."""
        nom_pc_normalise = cls.nom_afs(nom_pc)
        candidats_langue = [index for index, nom in enumerate(noms) if nom and LSL_MCL_LANGUAGES.LSL_MCL_Languages.texte_contient_marqueur_langue(nom, langue_cible) and (Path(cls.nom_afs(nom)).suffix == Path(nom_pc_normalise).suffix) and (Path(nom_pc_normalise).stem in Path(cls.nom_afs(nom)).stem or Path(cls.nom_afs(nom)).stem in Path(nom_pc_normalise).stem)]
        if len(candidats_langue) == 1:
            return candidats_langue[0]
        exacts = [index for index, nom in enumerate(noms) if cls.nom_afs(nom) == nom_pc_normalise]
        if len(exacts) == 1:
            return exacts[0]
        base_pc = Path(nom_pc_normalise).stem
        memes_noms = [index for index, nom in enumerate(noms) if nom and Path(cls.nom_afs(nom)).stem == base_pc]
        if len(memes_noms) == 1:
            return memes_noms[0]
        return None
