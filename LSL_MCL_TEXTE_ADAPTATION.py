"""Traitement AdaptationTextes des textes Larry MCL."""
import re
import LSL_MCL_VARIABLES as V

_TRAITEMENTS_PC_PS2 = {
    cle: "traiter_" + cle
    for cle in ("MEMCRDL1", "MLLoadQ", "MLLoadng", "MSSave",
                "MDDelete", "MSSaveQ", "MDDeletQ", "MIGSerch")
}


class AdaptationTextes:
    """Services textuels exposés par LSL_MCL_Textes."""

    @staticmethod
    def adapter_glyph(raw):
        """
        Adapte les glyphes spéciaux du jeu.
        """
        sortie = bytearray()
        for valeur in raw:
            sortie.append(V.GLYPH.get(valeur, valeur))
        return bytes(sortie)

    @staticmethod
    def adapter_accent(raw):
        """
        Supprime/remplace les caractères accentués non compatibles
        avec la police du jeu.

        Exemples :
            ï -> i
            é -> e
            ç -> c
            ñ -> n
            ü -> u
            ß -> ss
        """
        sortie = bytearray()
        for valeur in raw:
            if valeur in V.ACCENT:
                sortie.extend(V.ACCENT[valeur])
            else:
                sortie.append(valeur)
        return bytes(sortie)

    @classmethod
    def adapter_glyph_accent(cls, raw):
        """
        Adapte les glyphes spéciaux du jeu.
        Supprime/remplace les caractères accentués non compatibles
                avec la police du jeu.

            1. glyphes spéciaux PS2 -> PC
            2. accents -> caractères compatibles

        """
        raw = cls.adapter_glyph(raw)
        raw = cls.adapter_accent(raw)
        return raw

    @staticmethod
    def adapter_variables_ps2_vers_pc(ancien, candidat):
        """Rétablit la casse des variables PC ou retire une clause console incompatible."""
        import LSL_MCL_CONSOLE_PS2
        pc = list(re.finditer(b'%[A-Za-z]', ancien))
        ps2 = list(re.finditer(b'%[A-Za-z]', candidat))
        noms_pc = [m.group(0).lower() for m in pc]
        noms_ps2 = [m.group(0).lower() for m in ps2]
        if sorted(noms_pc) == sorted(noms_ps2):
            resultat = bytearray(candidat)
            for attendu, trouve in zip(pc, ps2):
                if attendu.group(0).lower() == trouve.group(0).lower():
                    resultat[trouve.start():trouve.end()] = attendu.group(0)
            return bytes(resultat)
        return LSL_MCL_CONSOLE_PS2.LSL_MCL_Console_ps2._retirer_clause_console_texte(ancien, candidat)

    @staticmethod
    def _separer_commandes_jam(valeur):
        """Sépare les libellés et jetons de commandes d’une valeur AIS."""
        morceaux = V.JETON_COMMANDE_JAM.split(valeur)
        libelles = [m.strip() for m in morceaux if m.strip()]
        commandes = V.JETON_COMMANDE_JAM.findall(valeur)
        return (libelles, commandes)

    @classmethod
    def traiter_MLLoadQ(cls, langue, texte_ps2):
        """Adapte le message MLLoadQ selon le profil de langue PC."""
        return cls._message_pc('MLLoadQ', langue, texte_ps2)

    @classmethod
    def traiter_MLLoadng(cls, langue, texte_ps2):
        """Adapte le message MLLoadng selon le profil de langue PC."""
        return cls._message_pc('MLLoadng', langue, texte_ps2)

    @classmethod
    def traiter_MSSave(cls, langue, texte_ps2):
        """Adapte le message MSSave selon le profil de langue PC."""
        return cls._message_pc('MSSave', langue, texte_ps2)

    @classmethod
    def traiter_MDDelete(cls, langue, texte_ps2):
        """Adapte le message MDDelete selon le profil de langue PC."""
        return cls._message_pc('MDDelete', langue, texte_ps2)

    @classmethod
    def traiter_MSSaveQ(cls, langue, texte_ps2):
        """Adapte le message MSSaveQ selon le profil de langue PC."""
        return cls._message_pc('MSSaveQ', langue, texte_ps2)

    @classmethod
    def traiter_MDDeletQ(cls, langue, texte_ps2):
        """Adapte le message MDDeletQ selon le profil de langue PC."""
        return cls._message_pc('MDDeletQ', langue, texte_ps2)

    @classmethod
    def traiter_MEMCRDL1(cls, langue, texte_ps2):
        """Adapte le message MEMCRDL1 selon le profil de langue PC."""
        return cls._message_pc('MEMCRDL1', langue, texte_ps2)

    @classmethod
    def traiter_MIGSerch(cls, langue, texte_ps2):
        """Adapte le message MIGSerch selon le profil de langue PC."""
        return cls._message_pc('MIGSerch', langue, texte_ps2)

    @classmethod
    def adapter_cle_ps2_vers_pc(cls, cle, candidat):
        """Adapte une valeur PS2_VERSION réellement récupérée par clé pour l'interface PC."""
        nom_traitement = _TRAITEMENTS_PC_PS2.get(cle)
        traitement = getattr(cls, nom_traitement) if nom_traitement else None
        if traitement is None or candidat is None:
            return candidat
        langue = cls.normaliser_code_langue(V.LANGUE_CIBLE).upper()
        texte_ps2 = candidat.decode('cp1252', errors='replace')
        rendu = traitement(langue, texte_ps2)
        resultat = rendu.encode('cp1252', errors='replace')
        print('[ADAPTATION PS2_VERSION->PC]', cle, '|', langue, '|', texte_ps2, '->', rendu)
        return resultat

    @classmethod
    def adapter_texte_ps2_vers_pc(cls, ancien, candidat):
        """Adapte variables et commandes ; refuse une structure incompatible avec le PC."""
        candidat = cls.adapter_variables_ps2_vers_pc(ancien, candidat)
        if candidat is None:
            return None
        candidat = cls.conserver_commandes_pc(ancien, candidat)
        if cls.variables_texte_jam(candidat) != cls.variables_texte_jam(ancien):
            return None
        return candidat.strip()

    @classmethod
    def conserver_commandes_pc(cls, ancien, candidat):
        """Conserve les commandes PC et les libellés traduits lorsque leur structure concorde."""
        libelles_pc, commandes_pc = cls._separer_commandes_jam(ancien)
        libelles_ps2, commandes_ps2 = cls._separer_commandes_jam(candidat)
        if not commandes_pc and commandes_ps2 and (len(libelles_ps2) == 1):
            return libelles_ps2[0]
        if commandes_pc and len(libelles_pc) == len(libelles_ps2):
            commence_par_commande = bool(V.JETON_COMMANDE_JAM.match(ancien.lstrip()))
            elements = []
            if commence_par_commande:
                for index, libelle in enumerate(libelles_ps2):
                    if index < len(commandes_pc):
                        elements.extend((commandes_pc[index], libelle))
                    else:
                        elements.append(libelle)
            else:
                elements.append(libelles_ps2[0])
                for index, libelle in enumerate(libelles_ps2[1:]):
                    if index < len(commandes_pc):
                        elements.extend((commandes_pc[index], libelle))
                    else:
                        elements.append(libelle)
            return b' '.join((element for element in elements if element))
        return candidat

    @staticmethod
    def _message_pc(cle, langue, texte_ps2):
        """Charge le profil demandé ; conserve la valeur PS2 si aucune adaptation existe."""
        from importlib import import_module
        if langue not in ('EN', 'FR', 'DE', 'ES', 'IT', 'RU'):
            return texte_ps2
        profil = import_module('LSL_MCL_TEXTE_LANGUE_' + langue)
        return profil.MESSAGES_PC.get(cle, texte_ps2)
