"""Reconstruction des JAM russes en conservant la structure et les commandes PC."""
from collections import defaultdict
from pathlib import Path
import re
import struct
import LSL_MCL_VARIABLES as V
from LSL_MCL_JAMS import LSL_MCL_jams
from LSL_MCL_TEXTES import LSL_MCL_Textes
from LSL_MCL_ECRITURE_JAM import publier_jam

class ConstructeurAppInitRusse:
    """Transfère les chaînes et les polices RU en préservant la structure PC."""

    @staticmethod
    def _chunks(data):
        """Valide des blocs JAM contigus et ordonnés."""
        chunks = LSL_MCL_jams.jam_chunks(data)
        if not chunks or data[:4] != b'JAM2':
            raise ValueError('Conteneur JAM2 invalide.')
        for i, (header, size, size2, start, end) in enumerate(chunks):
            limite = chunks[i + 1][0] if i + 1 < len(chunks) else len(data)
            if size != size2 or start != header + 32 or (not end <= limite < end + 4):
                raise ValueError(f'Bloc JAM {i} non conforme.')
        return chunks

    @staticmethod
    def _polices(data):
        """Repère la définition et les deux images TGA de la police russe."""
        candidats = {}
        for _, _, _, debut, fin in LSL_MCL_jams.jam_chunks(data):
            payload = data[debut:fin]
            if payload.startswith(b'Font[2]'):
                candidats['definition'] = payload
            elif len(payload) > 18 and payload[:3] == b'\x00\x01\x01':
                largeur, hauteur = struct.unpack_from('<HH', payload, 12)
                if (largeur, hauteur) == (3788, 76):
                    candidats['titre'] = payload
                elif largeur > 2000 and hauteur in (37, 38):
                    candidats['principale'] = payload
        if set(candidats) != {'definition', 'titre', 'principale'}:
            raise ValueError('Police GUFMAIN/GUFTITLE incomplète dans APPINIT.')
        return candidats

    @staticmethod
    def _textes(data):
        """Indexe les traductions RU par espace de noms et clé unique."""
        valeurs = defaultdict(set)
        for bloc in LSL_MCL_Textes.blocs_texte(data):
            for entree in V.ENTRY.finditer(bloc['payload']):
                valeurs[bloc['namespace'], entree.group(2)].add(entree.group(4))
        return {cle: next(iter(textes)) for cle, textes in valeurs.items() if len(textes) == 1}

    @staticmethod
    def _contient_guillemet_non_echappe(texte):
        """Détecte un guillemet réel sans rejeter les séquences \\" des textes JAM."""
        for index, octet in enumerate(texte):
            if octet != 34:
                continue
            antislashs = 0
            position = index - 1
            while position >= 0 and texte[position] == 92:
                antislashs += 1
                position -= 1
            if antislashs % 2 == 0:
                return True
        return False

    @staticmethod
    def _adapter_placeholders_pc(original, candidat):
        """Adapte une phrase PS2 aux variables réellement utilisées sur PC.

        La PS2 ajoute parfois des variables propres à la console (par exemple
        %M pour la carte mémoire) qui n'existent pas dans la phrase PC. Si les
        variables PC sont présentes dans le même ordre au début de la phrase RU,
        on conserve la traduction RU jusqu'à la dernière variable PC puis on
        reprend la ponctuation/suffixe PC. Cela transforme par exemple
        ``Load %G?`` + ``... %G ... %M?`` en ``... %G?`` sans texte anglais.
        """
        motif = re.compile(b'%[a-zA-Z]')
        pc = list(motif.finditer(original))
        ru = list(motif.finditer(candidat))
        if [m.group(0) for m in pc] == [m.group(0) for m in ru]:
            return candidat
        if not pc:
            if ru and all((m.group(0) in (b'%M', b'%P') for m in ru)):
                base = candidat[:ru[0].start()].rstrip()
                morceaux = base.rsplit(None, 1)
                if len(morceaux) == 2 and len(morceaux[1]) <= 3:
                    base = morceaux[0].rstrip()
                base = base.rstrip(b' .!?;:')
                ponctuation = re.search(b'([.!?]+)\\s*$', original)
                return base + (ponctuation.group(1) if ponctuation else b'')
            return None
        if len(ru) < len(pc):
            return None
        if [m.group(0) for m in ru[:len(pc)]] != [m.group(0) for m in pc]:
            return None
        dernier_pc = pc[-1]
        dernier_ru = ru[len(pc) - 1]
        suffixe_pc = original[dernier_pc.end():]
        return candidat[:dernier_ru.end()] + suffixe_pc

    @staticmethod
    def _remplacer_textes(payload, namespace, traductions):
        """Remplace les valeurs PC par le russe en gardant les commandes PC."""
        compteur = 0

        def substituer(entree):
            """Conserve les clés, espaces et fins de ligne du bloc PC."""
            nonlocal compteur
            original = entree.group(4)
            cle = entree.group(2)
            candidat = traductions.get((namespace, cle))
            if cle == b'MIGSerch' and candidat is not None:
                candidat = b'ZONCK COXPAHEHHSX NFP...'
            if candidat is None or len(candidat) > V.MAX_TEXTE_AIS or ConstructeurAppInitRusse._contient_guillemet_non_echappe(candidat) or (b'\n' in candidat):
                return entree.group(0)
            candidat = ConstructeurAppInitRusse._adapter_placeholders_pc(original, candidat)
            if candidat is None:
                return entree.group(0)
            candidat = LSL_MCL_Textes.conserver_commandes_pc(original, candidat)
            if len(candidat) > V.MAX_TEXTE_AIS or ConstructeurAppInitRusse._contient_guillemet_non_echappe(candidat) or b'\n' in candidat or (b'\r' in candidat):
                return entree.group(0)
            compteur += candidat != original
            return entree.group(1) + b'"' + entree.group(2) + b'"' + entree.group(3) + b'"' + candidat + b'"' + entree.group(5) + (b'\r' if entree.group(0).endswith(b'\r') else b'')
        sortie = V.ENTRY.sub(substituer, payload)
        valeurs = LSL_MCL_Textes.parse_chaines(sortie)
        if valeurs and re.search(b'ASCIIChar\\s*\\[\\s*\\d+\\s*\\]', sortie):
            nombre = LSL_MCL_Textes._compter_caracteres(sortie)
            sortie = re.sub(b'ASCIIChar\\s*\\[\\s*\\d+\\s*\\]', f'ASCIIChar   [  {nombre}  ]'.encode(), sortie, count=1)
        return (sortie, compteur)

    @staticmethod
    def construire(pc, ru, inclure_polices=False):
        """Reconstruit les textes d'un JAM et, pour APPINIT, ses polices."""
        chunks = ConstructeurAppInitRusse._chunks(pc)
        atlas_pc = ConstructeurAppInitRusse._polices(pc) if inclure_polices else {}
        atlas_ru = ConstructeurAppInitRusse._polices(ru) if inclure_polices else {}
        if inclure_polices:
            from LSL_MCL_POLICES_RU import PolicesRusses
            atlas_ru = PolicesRusses.fusionner(atlas_pc, atlas_ru)
        traductions = ConstructeurAppInitRusse._textes(ru)
        blocs = {b['chunk_index']: b['namespace'] for b in LSL_MCL_Textes.blocs_texte(pc)}
        premier = chunks[0][0]
        sortie = bytearray(pc[:premier])
        positions = {}
        changements = 0
        polices = 0
        for index, (ancien, _, _, debut, fin) in enumerate(chunks):
            contenu = pc[debut:fin]
            if contenu in atlas_pc.values():
                nom = next((k for k, v in atlas_pc.items() if v == contenu))
                contenu = atlas_ru[nom]
                polices += 1
            if index in blocs:
                contenu, nombre = ConstructeurAppInitRusse._remplacer_textes(contenu, blocs[index], traductions)
                changements += nombre
            positions[ancien] = len(sortie)
            sortie += struct.pack('<II', len(contenu), len(contenu))
            sortie += V.SIG_JAM + contenu
            if index < len(chunks) - 1:
                manque = -len(sortie) % 4
                sortie += b'\xff' + b'\x00' * (manque - 1) if manque else b''
        if inclure_polices and polices != 3:
            raise ValueError("Les trois ressources de police n'ont pas été transférées.")
        index_positions = [i for i in range(0, premier - 3, 2) if struct.unpack_from('<I', pc, i)[0] in positions]
        if inclure_polices and len(index_positions) != len(chunks) + 1:
            raise ValueError('Index APPINIT incomplet : reconstruction refusée.')
        if not index_positions and len(sortie) != len(pc):
            raise ValueError('Index JAM absent : déplacement des blocs impossible.')
        for offset in index_positions:
            ancienne = struct.unpack_from('<I', pc, offset)[0]
            struct.pack_into('<I', sortie, offset, positions[ancienne])
        construit = bytes(sortie)
        verifie = ConstructeurAppInitRusse._chunks(construit)
        if len(verifie) != len(chunks) or [c[0] for c in verifie] != list(positions.values()):
            raise ValueError('Contrôle des blocs reconstruits échoué.')
        return (construit, changements)

    @staticmethod
    def ecrire(pc_source, ru_source, destination):
        """Reconstruit un JAM russe et remplace la destination uniquement après écriture complète."""
        resultat, textes = ConstructeurAppInitRusse.construire(Path(pc_source).read_bytes(), Path(ru_source).read_bytes(), inclure_polices=Path(pc_source).name.casefold() == 'appinit.jam')
        destination = Path(destination)
        publier_jam(destination, resultat)
        return (destination, textes)
