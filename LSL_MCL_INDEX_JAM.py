"""Extraction Larry MCL : LSL_MCL_INDEX_JAM."""
from pathlib import Path
import LSL_MCL_VARIABLES as V
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES

class IndexJam:
    """Traitements hérités par LSL_MCL_Extractions."""

    @classmethod
    def source_ps2_index(cls):
        """Indexe les JAM PS2 par chemin relatif et nom de fichier."""
        jam_root = V.PS2_VERSION / 'Data' / 'JamFiles'
        resultat = {}
        if not jam_root.exists():
            return resultat
        for fichier in jam_root.rglob('*'):
            if not fichier.is_file() or fichier.suffix.lower() != '.jam':
                continue
            rel = str(fichier.relative_to(jam_root)).replace('\\', '/').lower()
            morceaux = rel.split('/')
            if morceaux[0] in ('pc', 'ps2'):
                rel = '/'.join(morceaux[1:])
            resultat.setdefault(rel, []).append(fichier)
            resultat.setdefault(fichier.name.lower(), []).append(fichier)
        return resultat

    @classmethod
    def trouver_ps2_jam(cls, pc_rel, index):
        """Résout un JAM PS2 uniquement lorsque sa correspondance est unique."""
        cle = str(pc_rel).replace('\\', '/').lower()
        candidats = index.get(cle, [])
        if len(candidats) == 1:
            return candidats[0]
        candidats = index.get(Path(pc_rel).name.lower(), [])
        uniques = list(dict.fromkeys(candidats))
        if len(uniques) == 1:
            return uniques[0]
        return None

    @classmethod
    def extraire_entrees_textes_jam(cls, fichier, racine, plateforme, data=None):
        """Extrait les chaînes JAM, leurs variables, adresses et informations linguistiques."""
        import LSL_MCL_ANALISES
        import LSL_MCL_DIAGNOSTICS
        import re
        if data is None:
            data = fichier.read_bytes()
        sha256_fichier = LSL_MCL_DIAGNOSTICS.LSL_MCL_Diagnostics.empreinte_sha256(fichier, data=data)
        chemin_relatif = str(fichier.relative_to(racine)).replace('\\', '/')
        chemin_normalise = LSL_MCL_OUTILS.LSL_MCL_Outils.normaliser_chemin_jam(chemin_relatif)
        resultat = []
        occurrences = {}
        for numero_bloc, bloc in enumerate(LSL_MCL_TEXTES.LSL_MCL_Textes.blocs_texte(data)):
            namespace = bloc['namespace']
            payload = bloc['payload']
            score_bloc = LSL_MCL_ANALISES.LSL_MCL_Analises.score_francais_bloc(payload)
            langue_bloc, scores_langues = LSL_MCL_ANALISES.LSL_MCL_Analises.identifier_langue_bloc_texte(payload)
            for numero_entree, match in enumerate(V.ENTRY.finditer(payload)):
                cle_brute = match.group(2)
                valeur_brute = match.group(4)
                cle = cle_brute.decode('latin1', errors='replace')
                valeur = valeur_brute.decode('cp1252', errors='replace')
                offset_entree = bloc['begin'] + match.start()
                offset_cle = bloc['begin'] + match.start(2)
                offset_valeur = bloc['begin'] + match.start(4)
                variables = re.findall('%[A-Za-z]', valeur)
                identifiant_occurrence = (namespace, cle, langue_bloc)
                numero_occurrence = occurrences.get(identifiant_occurrence, 0)
                occurrences[identifiant_occurrence] = numero_occurrence + 1
                resultat.append({'plateforme': plateforme, 'fichier': chemin_relatif, 'fichier_normalise': chemin_normalise, 'adresse_fichier': str(fichier.resolve()), 'taille_fichier': len(data), 'sha256_fichier': sha256_fichier, 'chunk_index': bloc.get('chunk_index'), 'offset_bloc_debut': bloc['begin'], 'offset_bloc_debut_hex': f"0x{bloc['begin']:X}", 'offset_bloc_fin': bloc['end'], 'offset_bloc_fin_hex': f"0x{bloc['end']:X}", 'taille_bloc': bloc['end'] - bloc['begin'], 'numero_bloc_texte': numero_bloc, 'score_francais_bloc': score_bloc, 'langue_bloc': langue_bloc, 'scores_langues': scores_langues, 'numero_entree': numero_entree, 'namespace': namespace, 'cle': cle, 'valeur': valeur, 'encodage': 'cp1252/latin1', 'longueur_octets': len(valeur_brute), 'numero_occurrence_cle_langue': numero_occurrence, 'offset_entree': offset_entree, 'offset_entree_hex': f'0x{offset_entree:X}', 'offset_cle': offset_cle, 'offset_cle_hex': f'0x{offset_cle:X}', 'offset_valeur': offset_valeur, 'offset_valeur_hex': f'0x{offset_valeur:X}', 'offset_valeur_fin': offset_valeur + len(valeur_brute), 'offset_valeur_fin_hex': f'0x{offset_valeur + len(valeur_brute):X}', 'variables': variables, 'nombre_variables': len(variables), 'identifiant': f'{chemin_normalise}::{namespace}::{cle}'})
        return resultat
