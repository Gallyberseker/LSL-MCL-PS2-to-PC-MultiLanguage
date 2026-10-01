"""Gestion des langues : ProtectionTraduction."""
from collections import Counter
import re
import LSL_MCL_TEXTES

class ProtectionTraduction:
    """Services de ProtectionTraduction."""

    @classmethod
    def variables_valides(cls, original, traduit):
        """Vérifie la conservation des variables de format dans la traduction."""
        return Counter(cls.VARIABLES.findall(original)) == Counter(cls.VARIABLES.findall(traduit))

    @classmethod
    def marqueurs_proteges(cls, texte):
        """Recense les marqueurs du texte à préserver."""
        return (Counter(cls.VARIABLES.findall(texte)), Counter(cls.FORMATS_DATE.findall(texte)), Counter(cls.BOUTONS.findall(texte)))

    @classmethod
    def marqueurs_valides(cls, original, traduit):
        """Vérifie la conservation des marqueurs du texte original."""
        return cls.marqueurs_proteges(original) == cls.marqueurs_proteges(traduit)

    @classmethod
    def proteger_texte(cls, texte):
        """Protège variables, formats de date et glyphes boutons avant traduction automatique."""
        jetons = []
        motif = re.compile(cls.VARIABLES.pattern + '|' + cls.FORMATS_DATE.pattern + '|' + cls.BOUTONS.pattern)

        def proteger(match):
            """Remplace temporairement un marqueur par un jeton protégé."""
            marqueur = f'ZXQVAR{len(jetons):04d}ZXQ'
            jetons.append((marqueur, match.group()))
            return marqueur
        return (motif.sub(proteger, texte), jetons)

    @staticmethod
    def restaurer_jetons(texte, jetons):
        """Réinsère les marqueurs protégés après traduction."""
        for marqueur, valeur in jetons:
            texte = texte.replace(marqueur, valeur)
        return texte

    @staticmethod
    def securiser_delimiteurs(texte):
        """
        Sécurise une valeur destinée à une chaîne AIS.

        Règles :
        - supprime les vrais retours ligne ;
        - conserve les guillemets AIS déjà échappés : "
        - transforme un guillemet ASCII interne non échappé en : "
        - ne produit JAMAIS de guillemets typographiques “ ”.
        """
        if texte is None:
            return ''
        texte = str(texte)
        texte = texte.replace('\r', ' ')
        texte = texte.replace('\n', ' ')
        texte = re.sub('\\s{2,}', ' ', texte).strip()
        sortie = []
        i = 0
        while i < len(texte):
            caractere = texte[i]
            if caractere == '\\' and i + 1 < len(texte) and (texte[i + 1] == '"'):
                sortie.append('\\"')
                i += 2
                continue
            if caractere == '"':
                sortie.append('\\"')
                i += 1
                continue
            sortie.append(caractere)
            i += 1
        return ''.join(sortie)

    @staticmethod
    def normaliser_texte_ais(texte):
        """
        Sécurise une traduction avant son injection dans un fichier AIS/JAM.

        Le moteur du jeu utilise des chaînes entourées par des guillemets ASCII.

        À l'intérieur d'une chaîne, un guillemet doit être représenté par :

            "

        Certains traducteurs transforment malheureusement :

            "BUTTON"

        en :

            \\“BUTTON\\”

        ou :

            “BUTTON”

        Ces formes provoquent ensuite :

            invalid string

        dans le moteur du jeu.

        Cette fonction restaure donc la syntaxe AIS correcte.
        """
        if texte is None:
            return ''
        texte = str(texte)
        texte = texte.replace('\\“', '\\"')
        texte = texte.replace('\\”', '\\"')
        texte = texte.replace('“', '\\"')
        texte = texte.replace('”', '\\"')
        texte = texte.replace('‘', "'")
        texte = texte.replace('’', "'")
        return texte

    @staticmethod
    def normaliser_glyphes_jeu(texte):
        """
        Adapte uniquement les caractères incompatibles pour les langues OTHER.

        La traduction JSON reste intacte.
        Cette fonction est destinée uniquement au texte envoyé au jeu.

        Exemples :
            geruïneerd -> geruineerd
            Dostępny   -> Dostepny

        IMPORTANT :
            On utilise adapter_accent() uniquement.
            On n'applique PAS adapter_glyph() ici afin de ne pas
            modifier les glyphes spéciaux/boutons du jeu.
        """
        if texte is None:
            return ''
        texte = str(texte)
        caracteres_hors_cp1252 = {'ą': 'a', 'Ą': 'A', 'ć': 'c', 'Ć': 'C', 'ę': 'e', 'Ę': 'E', 'ł': 'l', 'Ł': 'L', 'ń': 'n', 'Ń': 'N', 'ś': 's', 'Ś': 'S', 'ź': 'z', 'Ź': 'Z', 'ż': 'z', 'Ż': 'Z'}
        texte = ''.join((caracteres_hors_cp1252.get(caractere, caractere) for caractere in texte))
        brut = texte.encode('cp1252', errors='replace')
        brut = LSL_MCL_TEXTES.LSL_MCL_Textes.adapter_accent(brut)
        return brut.decode('cp1252', errors='replace')
