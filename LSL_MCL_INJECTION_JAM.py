"""Traitements d'injection : jam."""
import struct
import re
import LSL_MCL_JAMS

class InjectionJam:
    """Services d'injection jam."""

    @staticmethod
    def compacter_reserve_jam(payload):
        """Retire les espaces de réserve hors des chaînes avant la fermeture AIS."""
        fermeture = payload.rfind(b'}')
        if fermeture < 0:
            raise RuntimeError("Structure de bloc texte JAM invalide : accolade '}' manquante.")
        reserve = re.search(b'[ \t]+$', payload[:fermeture])
        if reserve:
            return payload[:reserve.start()] + payload[fermeture:]
        return payload

    @staticmethod
    def appliquer_padding_espaces_jam(payload, taille_attendue):
        """Ajuste la réserve extérieure aux chaînes à la capacité exacte du bloc."""
        if len(payload) == taille_attendue:
            return payload
        payload = InjectionJam.compacter_reserve_jam(payload)
        taille_actuelle = len(payload)
        if taille_actuelle > taille_attendue:
            return None
        fermeture = payload.rfind(b'}')
        reserve = taille_attendue - taille_actuelle
        return payload[:fermeture] + b' ' * reserve + payload[fermeture:]

    @staticmethod
    def remplacer_chunk_variable(data, bloc, nouveau_payload):
        """Remplace le payload d'un chunk et ajuste les offsets suivants dans l'index JAM."""
        anciens_chunks = LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(data)
        premiere_entete = anciens_chunks[0][0]
        header = bloc['header']
        debut = bloc['begin']
        fin = bloc['end']
        ancien_size = bloc['size']
        nouveau_size = len(nouveau_payload)
        delta = nouveau_size - ancien_size
        sortie = bytearray()
        sortie += data[:header]
        sortie += struct.pack('<II', nouveau_size, nouveau_size)
        sortie += data[header + 8:debut]
        sortie += nouveau_payload
        sortie += data[fin:]
        if delta:
            for ancien_header, _, _, _, _ in anciens_chunks:
                if ancien_header <= header:
                    continue
                ancien = struct.pack('<I', ancien_header)
                nouveau = struct.pack('<I', ancien_header + delta)
                pos = 0
                while True:
                    pos = sortie.find(ancien, pos, premiere_entete)
                    if pos < 0:
                        break
                    sortie[pos:pos + 4] = nouveau
                    pos += 4
        return bytes(sortie)
