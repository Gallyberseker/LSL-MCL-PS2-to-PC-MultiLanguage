"""Traitement PayloadTextes des textes Larry MCL."""
import re
import LSL_MCL_VARIABLES as V

class PayloadTextes:
    """Services textuels exposés par LSL_MCL_Textes."""

    @classmethod
    def construire_payload_compact_fixe(cls, pc_payload, source_payload, traductions_globales=None, traductions_textes=None):
        """Reconstruit un bloc AIS à taille fixe en préservant les variables et commandes PC."""
        import LSL_MCL_INJECTIONS
        source = cls.parse_chaines_multiples(source_payload)
        matches = list(V.ENTRY.finditer(pc_payload))
        if not matches:
            return (pc_payload, 0, 0)
        morceaux = []
        position = 0
        changes = 0
        occurrences = {}
        for match in matches:
            morceaux.append(pc_payload[position:match.start()])
            cle_bytes = match.group(2)
            cle = cle_bytes.decode('latin1')
            ancien = match.group(4)
            numero_occurrence = occurrences.get(cle, 0)
            occurrences[cle] = numero_occurrence + 1
            valeurs_source = source.get(cle, ())
            candidat = valeurs_source[numero_occurrence] if numero_occurrence < len(valeurs_source) else None
            candidat_local_invalide = candidat is None
            if candidat is not None:
                candidat_cle = cls.adapter_cle_ps2_vers_pc(cle, candidat)
                candidat_adapte = cls.adapter_texte_ps2_vers_pc(ancien, cls.adapter_glyph_accent(candidat_cle))
                candidat_local_invalide = candidat_adapte is None or candidat_adapte == ancien or any((m in candidat_adapte.lower() and m not in ancien.lower() for m in (b'memory card', b'carte memoire', b'playstation')))
            if candidat_local_invalide:
                candidat_texte = None
                if traductions_textes:
                    candidat_texte = traductions_textes.get(cls.normaliser_source_anglaise_jam(ancien))
                if candidat_texte is not None:
                    candidat = candidat_texte
                elif traductions_globales:
                    candidat = cls.choisir_traduction_globale(cle, ancien, traductions_globales)
            if cle in V.PC_KEYS or candidat is None:
                nouveau = ancien
            else:
                candidat = cls.adapter_cle_ps2_vers_pc(cle, candidat)
                candidat = cls.adapter_texte_ps2_vers_pc(ancien, cls.adapter_glyph_accent(candidat))
                if candidat is None:
                    nouveau = ancien
                else:
                    nouveau = candidat
            longueur_avant = len(nouveau)
            nouveau_limite = cls.limiter_texte_ais(nouveau)
            if nouveau_limite is None:
                print('[JAM TEXTE REFUSE - LONGUEUR]', cle, ':', longueur_avant, 'octets et variables impossibles a conserver')
                nouveau = ancien
            else:
                nouveau = nouveau_limite
                if len(nouveau) != longueur_avant:
                    print('[JAM TEXTE COMPACTE]', cle, ':', longueur_avant, '->', len(nouveau), 'octets')
            if nouveau != ancien:
                changes += 1
            fin_cr = b'\r' if match.group(0).endswith(b'\r') else b''
            morceaux.append(b'"' + cle_bytes + b'" "' + nouveau + b'"' + fin_cr)
            position = match.end()
        morceaux.append(pc_payload[position:])
        resultat = b''.join(morceaux)
        if not cls.payload_ais_est_valide(resultat, len(matches)):
            print('[JAM BLOC REFUSE - SYNTAXE AIS]', 'une chaine reconstruite est invalide')
            return (None, changes, 0)
        ascii_char = cls._compter_caracteres(resultat)
        resultat = re.sub(b'ASCIIChar\\s+\\[\\s*\\d+\\s*\\]', f'ASCIIChar   [  {ascii_char}  ]'.encode('ascii'), resultat, count=1)
        resultat = LSL_MCL_INJECTIONS.LSL_MCL_Injection.compacter_reserve_jam(resultat)
        taille_pc = len(pc_payload)
        taille_compacte = len(resultat)
        depassement = max(0, taille_compacte - taille_pc)
        if depassement:
            return (None, changes, depassement)
        resultat_padded = LSL_MCL_INJECTIONS.LSL_MCL_Injection.appliquer_padding_espaces_jam(resultat, taille_pc)
        if resultat_padded is None:
            return (None, changes, depassement)
        return (resultat_padded, changes, -(taille_pc - taille_compacte))

    @classmethod
    def traduire_jam_sans_deplacement(cls, pc_data, source_data, nom, traductions_globales=None, traductions_textes=None):
        """Traduit les blocs textuels et vérifie que taille, offsets et table JAM restent identiques."""
        import LSL_MCL_JAMS
        pc_blocs = cls.blocs_texte(pc_data)
        source_blocs = cls.blocs_texte(source_data)
        sortie = bytearray(pc_data)
        total = 0
        blocs_modifies = 0
        for bloc in pc_blocs:
            candidats = [candidat for candidat in source_blocs if candidat['namespace'] == bloc['namespace']]
            source = cls.choisir_bloc_structurel(bloc['payload'], candidats) if candidats else None
            if source is None:
                source = {'payload': b''}
            else:
                print('[JAM SOURCE PS2_VERSION]', nom, f"{bloc['namespace']}[{bloc['count']}]", '<-', f"chunk {source['chunk_index']}", f"[{source['count']}]", 'score langue', cls.score_langue(cls.parse_chaines(source['payload'])))
            nouveau, changes, espace = cls.construire_payload_compact_fixe(bloc['payload'], source['payload'], traductions_globales, traductions_textes)
            if nouveau is None:
                print('[JAM BLOC IGNORE - CAPACITE]', nom, f"{bloc['namespace']}[{bloc['count']}]", ':', espace, 'octets manquants')
                continue
            if not changes:
                continue
            sortie[bloc['begin']:bloc['end']] = nouveau
            total += changes
            blocs_modifies += 1
            reserve = -espace
            print('[JAM TEXTE]', f"{bloc['namespace']}[{bloc['count']}]", ':', changes, 'chaines | reserve', reserve, 'octets')
        sortie = bytes(sortie)
        if len(sortie) != len(pc_data):
            raise RuntimeError(f'{nom} : taille du fichier modifiee.')
        avant = LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(pc_data)
        apres = LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(sortie)
        if avant != apres:
            raise RuntimeError(f'{nom} : table des chunks modifiee.')
        print('[JAM STRUCTURE OK]', nom, ':', len(apres), 'chunks inchanges')
        return (sortie, blocs_modifies, total)

    @classmethod
    def limiter_texte_ais(cls, valeur, maximum=V.MAX_TEXTE_AIS):
        """Compacte ou coupe à une frontière de mot ; refuse la perte d’une variable."""
        if len(valeur) <= maximum:
            return valeur
        variables_originales = cls.variables_texte_jam(valeur)
        compacte = re.sub(b'[ \\t]+([,.;:!?])', b'\\1', valeur)
        compacte = re.sub(b'[ \\t]{2,}', b' ', compacte).strip()
        if len(compacte) <= maximum:
            return compacte
        ponctuation = b''
        match_fin = re.search(b'([.!?]+)$', compacte)
        if match_fin:
            ponctuation = match_fin.group(1)[:1]
        limite = maximum - len(ponctuation)
        coupure = compacte.rfind(b' ', 0, limite + 1)
        if coupure < max(1, limite - 32):
            coupure = limite
        compacte = compacte[:coupure].rstrip()
        if compacte.endswith(b'\\'):
            compacte = compacte[:-1].rstrip()
        compacte += ponctuation
        if len(compacte) > maximum or cls.variables_texte_jam(compacte) != variables_originales:
            return None
        return compacte

    @staticmethod
    def payload_ais_est_valide(payload, nombre_attendu):
        """Vérifie le nombre d’entrées AIS, leurs clés et la longueur des valeurs."""
        matches = list(V.ENTRY.finditer(payload))
        if len(matches) != nombre_attendu:
            return False
        return all((b'\n' not in match.group(2) and b'\r' not in match.group(2) and (len(match.group(4)) <= V.MAX_TEXTE_AIS) for match in matches))
