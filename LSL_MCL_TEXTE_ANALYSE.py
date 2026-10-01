"""Traitement AnalyseTextes des textes Larry MCL."""
from pathlib import Path
import re
import LSL_MCL_VARIABLES as V

class AnalyseTextes:
    """Services textuels exposés par LSL_MCL_Textes."""

    @staticmethod
    def blocs_texte(data):
        """Repère les chunks textuels JAM et leurs offsets sans modifier les données."""
        import LSL_MCL_JAMS
        resultat = []
        for index, (header, taille1, taille2, debut, fin) in enumerate(LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(data)):
            payload = data[debut:fin]
            namespace = re.search(b'Namespace "([^"]+)"', payload[:500])
            count = re.search(b'ASCIIString\\s*\\[\\s*(\\d+)\\s*\\]', payload[:1000])
            if not (namespace and count):
                continue
            resultat.append({'chunk_index': index, 'header': header, 'size': taille1, 'begin': debut, 'end': fin, 'namespace': namespace.group(1).decode('latin1'), 'count': int(count.group(1)), 'payload': payload})
        return resultat

    @staticmethod
    def parse_chaines(payload):
        """Lit les couples clé/valeur AIS ; la dernière occurrence d’une clé est retenue."""
        return {match.group(2).decode('latin1'): match.group(4) for match in V.ENTRY.finditer(payload)}

    @staticmethod
    def score_langue(valeurs, langue=None):
        """Évalue les marqueurs lexicaux et accents du profil de la langue demandée."""
        langue = (langue or V.LANGUE_CIBLE).lower()
        profil = V.PROFILS_LANGUES.get(langue, V.PROFILS_LANGUES['fr'])
        score = 0
        for raw in valeurs.values():
            texte = raw.decode('cp1252', errors='ignore').lower()
            score += sum((texte.count(mot) * 3 for mot in profil['mots']))
            score += sum((texte.count(accent) * 2 for accent in profil['accents']))
        return score

    @classmethod
    def score_francais(cls, valeurs):
        """Évalue les marqueurs du profil français."""
        return cls.score_langue(valeurs, 'fr')

    @staticmethod
    def normaliser_texte_jam(valeur):
        """Décode une valeur CP1252 et normalise sa casse et ses espaces."""
        texte = valeur.decode('cp1252', errors='ignore').strip().lower()
        texte = re.sub('\\s+', ' ', texte)
        return texte

    @classmethod
    def normaliser_source_anglaise_jam(cls, valeur):
        """Produit la clé de recherche utilisée pour les phrases anglaises de secours."""
        texte = cls.normaliser_texte_jam(valeur)
        texte = re.sub('[^a-z0-9%]+', ' ', texte)
        mots = []
        for mot in texte.split():
            if len(mot) > 3 and mot.endswith('s') and (not mot.endswith('ss')):
                mot = mot[:-1]
            mots.append(mot)
        return ' '.join(mots)

    @staticmethod
    def variables_texte_jam(valeur):
        """Renvoie les variables %lettre triées, sans distinction de casse."""
        return tuple(sorted((variable.lower() for variable in re.findall(b'%[A-Za-z]', valeur))))

    @staticmethod
    def parse_chaines_multiples(payload):
        """Lit toutes les occurrences de chaque clé AIS dans leur ordre d’origine."""
        resultat = {}
        for match in V.ENTRY.finditer(payload):
            cle = match.group(2).decode('latin1')
            resultat.setdefault(cle, []).append(match.group(4))
        return resultat

    @staticmethod
    def normaliser_code_langue(langue):
        """Résout les alias de langue définis dans les paramètres du projet."""
        code = str(langue or 'fr').strip().lower()
        correspondances = {alias: langue_canonique for langue_canonique, aliases in V.ALIASES_AUDIO_LANGUE.items() for alias in aliases}
        return correspondances.get(code, code)

    @staticmethod
    def _fichiers_jam(dossier):
        """Parcourt les fichiers JAM sans distinguer la casse de leur extension."""
        return (f for f in Path(dossier).rglob('*') if f.is_file() and f.suffix.lower() == '.jam')

    @staticmethod
    def _compter_caracteres(payload):
        """Compte les octets de chaque valeur AIS et son terminateur, doublons inclus."""
        return sum((len(m.group(4)) + 1 for m in V.ENTRY.finditer(payload)))
