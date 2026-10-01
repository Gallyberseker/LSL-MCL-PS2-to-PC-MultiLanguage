"""Adaptation des clauses matérielles PS2 aux textes de l’interface PC."""
import re
import unicodedata
import LSL_MCL_VARIABLES as V

class LSL_MCL_Console_ps2:
    """Retire les clauses mémoire PS2 uniquement si le contrat des variables PC est conservé."""

    @staticmethod
    def _texte_console_normalise(texte):
        """Normalise la casse, les accents et les espaces pour comparer les textes."""
        texte = unicodedata.normalize('NFKC', texte).casefold()
        texte = unicodedata.normalize('NFKD', texte)
        texte = ''.join((caractere for caractere in texte if not unicodedata.combining(caractere)))
        return ' '.join(texte.split())

    @staticmethod
    def _phrase_pc_complete(texte):
        """Refuse les phrases manifestement incomplètes après retrait d’une clause PS2."""
        sans_fin = re.sub('[.!?…\\s]+$', '', texte or '')
        if not sans_fin:
            return False
        if re.match("^(?:la|le|les)\\s+n[’']|^(?:the)\\s+(?:is|was|has)|^(?:der|die|das)\\s+(?:ist|wurde)|^(?:el|la|los|las)\\s+(?:es|está|se)|^(?:il|lo|la|gli|le)\\s+(?:è|e|non)", sans_fin.casefold()):
            return False
        derniere_variable = re.search('%[A-Za-z]$', sans_fin)
        if derniere_variable:
            avant = sans_fin[:derniere_variable.start()]
            return bool(re.findall('[^\\W\\d_]+', avant, flags=re.UNICODE))
        sans_variables = re.sub('%[A-Za-z]', ' ', sans_fin)
        mots = re.findall('[^\\W\\d_]+', sans_variables, flags=re.UNICODE)
        return len(mots) >= 2 and mots[-1].casefold() not in V.MOTS_LIAISON_FIN_PC

    @staticmethod
    def _retirer_clause_console_texte(ancien, candidat):
        """Retire une clause mémoire PS2 en conservant les variables, leur ordre, leur casse et la ponctuation PC ; renvoie None si le résultat est incertain."""
        try:
            texte_pc = ancien.decode('cp1252')
            texte_ps2 = candidat.decode('cp1252')
        except UnicodeDecodeError:
            return None
        variables_pc = re.findall('%[A-Za-z]', texte_pc)
        variables_ps2 = re.findall('%[A-Za-z]', texte_ps2)
        pc_norm = sorted((variable.casefold() for variable in variables_pc))
        ps2_norm = sorted((variable.casefold() for variable in variables_ps2))
        surplus = list(ps2_norm)
        for variable in pc_norm:
            if variable not in surplus:
                return None
            surplus.remove(variable)
        if not surplus or any((variable != '%m' for variable in surplus)):
            return None
        normaliser = LSL_MCL_Console_ps2._texte_console_normalise
        marqueurs = tuple(sorted({normaliser(m) for m in V.MARQUEURS_CONSOLE_PC if normaliser(m)}))
        normalise, positions_originales = LSL_MCL_Console_ps2._normaliser_avec_positions(texte_ps2)
        positions = [normalise.find(m) for m in marqueurs if m in normalise]
        if not positions:
            return None
        position_normalisee = min(positions)
        position = positions_originales[position_normalisee]
        variable_memoire = re.search('%[mM](?=\\W|$)', texte_ps2[position:])
        if variable_memoire is None:
            return None
        fin_retrait = position + variable_memoire.end()
        if re.search('[.!?…]', texte_ps2[position:position + variable_memoire.start()]):
            return None
        prefixe_normalise = normalise[:position_normalisee].rstrip()
        debut_retrait = position
        raccords = sorted({normaliser(r) for r in V.RACCORDS_CONSOLE_PC if normaliser(r)}, key=len, reverse=True)
        for raccord in raccords:
            if prefixe_normalise.endswith(raccord):
                debut_normalise = len(prefixe_normalise) - len(raccord)
                if debut_normalise == 0 or prefixe_normalise[debut_normalise - 1].isspace():
                    debut_retrait = positions_originales[debut_normalise]
                    break
        proposition = (texte_ps2[:debut_retrait].rstrip() + ' ' + texte_ps2[fin_retrait:].lstrip()).strip()
        phrases = re.split('(?<=[.!?])\\s+', proposition)
        utiles = []
        for phrase in phrases:
            normalisee = LSL_MCL_Console_ps2._texte_console_normalise(phrase)
            if any((marqueur in normalisee for marqueur in marqueurs)):
                continue
            utiles.append(phrase)
        proposition = ' '.join(utiles).strip()
        proposition = re.sub('\\s+([,.;:!?])', '\\1', proposition)
        proposition = re.sub('[ \\t]{2,}', ' ', proposition).strip()
        trouvees = list(re.finditer('%[A-Za-z]', proposition))
        if len(trouvees) != len(variables_pc):
            return None
        morceaux = []
        position = 0
        for match, variable_pc in zip(trouvees, variables_pc):
            if match.group(0).casefold() != variable_pc.casefold():
                return None
            morceaux.extend((proposition[position:match.start()], variable_pc))
            position = match.end()
        morceaux.append(proposition[position:])
        proposition = ''.join(morceaux)
        ponctuation = re.search('([.!?]+)\\s*$', texte_pc)
        if ponctuation:
            proposition = re.sub('[.!?…]+\\s*$', '', proposition).rstrip()
            proposition += ponctuation.group(1)
        if not LSL_MCL_Console_ps2._phrase_pc_complete(proposition):
            return None
        if sorted((variable.casefold() for variable in re.findall('%[A-Za-z]', proposition))) != pc_norm:
            return None
        normalisee = LSL_MCL_Console_ps2._texte_console_normalise(proposition)
        ancien_normalise = LSL_MCL_Console_ps2._texte_console_normalise(texte_pc)
        if any((marqueur in normalisee and marqueur not in ancien_normalise for marqueur in marqueurs)):
            return None
        try:
            return proposition.encode('cp1252')
        except UnicodeEncodeError:
            return None

    @staticmethod
    def _normaliser_avec_positions(texte):
        """Associe chaque caractère normalisé à son indice dans le texte original.

    Les expansions Unicode et les groupes d'espaces conservent leur origine,
    afin de découper le texte original sans utiliser les indices normalisés.
    """
        caracteres, positions = ([], [])
        espace = None
        for index, caractere in enumerate(texte):
            normalise = unicodedata.normalize('NFKC', caractere).casefold()
            normalise = unicodedata.normalize('NFKD', normalise)
            for lettre in normalise:
                if unicodedata.combining(lettre):
                    continue
                if lettre.isspace():
                    if caracteres and espace is None:
                        espace = index
                    continue
                if espace is not None:
                    caracteres.append(' ')
                    positions.append(espace)
                    espace = None
                caracteres.append(lettre)
                positions.append(index)
        return (''.join(caracteres), positions)
