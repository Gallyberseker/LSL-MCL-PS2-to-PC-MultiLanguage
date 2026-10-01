"""Traitement MemoireTextes des textes Larry MCL."""
import LSL_MCL_VARIABLES as V

class MemoireTextes:
    """Services textuels exposés par LSL_MCL_Textes."""

    @classmethod
    def choisir_traduction_globale(cls, cle, ancien, traductions_globales):
        """Retient une traduction par clé seulement si les adaptations PC ne sont pas ambiguës."""
        valeurs = traductions_globales.get(cle, ())
        marqueurs_console = (b'memory card', b'carte memoire', b'tarjeta de memoria', b'scheda di memoria', b'speicherkarte', b'playstation')
        candidats = {}
        for valeur in valeurs:
            valeur_cle = cls.adapter_cle_ps2_vers_pc(cle, valeur)
            adaptee = cls.adapter_texte_ps2_vers_pc(ancien, cls.adapter_glyph_accent(valeur_cle))
            if adaptee is None or adaptee == ancien:
                continue
            if any((marqueur in adaptee.lower() and marqueur not in ancien.lower() for marqueur in marqueurs_console)):
                continue
            candidats.setdefault(adaptee, set()).add(valeur)
        if not candidats:
            return None
        if len(candidats) != 1:
            return None
        valeurs_originales = next(iter(candidats.values()))
        return sorted(valeurs_originales)[0]

    @classmethod
    def construire_memoire_jam_globale(cls, jam_root_pc, ps2_index):
        """Indexe les clés PS2 et les phrases parallèles reconnues dans la langue cible."""
        import LSL_MCL_EXTRACTIONS
        from functools import lru_cache
        import LSL_MCL_ANALISES
        identifier = lru_cache(maxsize=128)(LSL_MCL_ANALISES.LSL_MCL_Analises.identifier_langue_bloc_texte)
        parser = lru_cache(maxsize=128)(cls.parse_chaines_multiples)
        candidats_cles = {}
        candidats_textes = {}
        fichiers_paires = 0
        blocs_cible = 0
        blocs_autres_refuses = 0
        blocs_inconnus_ignores = 0
        fichiers_ps2 = sorted({fichier for liste in ps2_index.values() for fichier in liste})
        for fichier in fichiers_ps2:
            blocs_fichier_ps2 = cls.blocs_texte(fichier.read_bytes())
            for bloc in blocs_fichier_ps2:
                langue_bloc, _ = identifier(bloc['payload'])
                if langue_bloc != V.LANGUE_CIBLE:
                    if langue_bloc == 'inconnue':
                        blocs_inconnus_ignores += 1
                    else:
                        blocs_autres_refuses += 1
                    continue
                blocs_cible += 1
                for cle, valeurs in parser(bloc['payload']).items():
                    candidats_cles.setdefault(cle, set()).update(valeurs)
            for bloc_cible in blocs_fichier_ps2:
                langue_bloc_cible, _ = identifier(bloc_cible['payload'])
                if langue_bloc_cible != V.LANGUE_CIBLE:
                    continue
                valeurs_cible = parser(bloc_cible['payload'])
                if not valeurs_cible:
                    continue
                candidats_anglais = []
                cles_cible = set(valeurs_cible)
                for bloc_anglais in blocs_fichier_ps2:
                    if bloc_anglais['namespace'] != bloc_cible['namespace']:
                        continue
                    valeurs_anglais = parser(bloc_anglais['payload'])
                    if not valeurs_anglais:
                        continue
                    langue_bloc_anglais, _ = identifier(bloc_anglais['payload'])
                    if langue_bloc_anglais != 'en':
                        continue
                    cles_anglais = set(valeurs_anglais)
                    communes = cles_cible & cles_anglais
                    if not communes:
                        continue
                    candidats_anglais.append((len(communes) / len(cles_cible | cles_anglais), len(communes), valeurs_anglais))
                if not candidats_anglais:
                    continue
                _, _, valeurs_anglais = max(candidats_anglais, key=lambda item: item[:2])
                for cle, liste_anglaise in valeurs_anglais.items():
                    liste_cible = valeurs_cible.get(cle, ())
                    for valeur_anglaise, valeur_cible in zip(liste_anglaise, liste_cible):
                        if valeur_anglaise == valeur_cible:
                            continue
                        normalisee = cls.normaliser_source_anglaise_jam(valeur_anglaise)
                        if normalisee:
                            candidats_textes.setdefault(normalisee, set()).add(valeur_cible)
        for pc in sorted(cls._fichiers_jam(jam_root_pc)):
            relatif = pc.relative_to(jam_root_pc)
            ps2 = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.trouver_ps2_jam(relatif, ps2_index)
            if ps2 is None:
                continue
            fichiers_paires += 1
            blocs_pc = cls.blocs_texte(pc.read_bytes())
            blocs_ps2 = cls.blocs_texte(ps2.read_bytes())
            for bloc_pc in blocs_pc:
                candidats = [bloc for bloc in blocs_ps2 if bloc['namespace'] == bloc_pc['namespace']]
                bloc_ps2 = cls.choisir_bloc_structurel(bloc_pc['payload'], candidats)
                if bloc_ps2 is None:
                    continue
                valeurs_pc = parser(bloc_pc['payload'])
                valeurs_ps2 = parser(bloc_ps2['payload'])
                for cle, liste_pc in valeurs_pc.items():
                    liste_ps2 = valeurs_ps2.get(cle, ())
                    for valeur_pc, valeur_ps2 in zip(liste_pc, liste_ps2):
                        valeur_adaptee = cls.adapter_texte_ps2_vers_pc(valeur_pc, cls.adapter_glyph_accent(valeur_ps2))
                        if valeur_adaptee is None:
                            continue
                        if valeur_pc == valeur_adaptee:
                            continue
                        normalisee = cls.normaliser_source_anglaise_jam(valeur_pc)
                        if normalisee:
                            candidats_textes.setdefault(normalisee, set()).add(valeur_ps2)
        cles_sures = {cle: tuple(sorted(valeurs)) for cle, valeurs in candidats_cles.items()}
        textes_surs = {texte: next(iter(valeurs)) for texte, valeurs in candidats_textes.items() if len(valeurs) == 1}
        print('[MEMOIRE JAM]', fichiers_paires, 'fichiers couples |', len(cles_sures), 'cles globales |', len(textes_surs), 'textes reutilisables |', blocs_cible, 'blocs cible |', blocs_autres_refuses, 'autres langues refusees |', blocs_inconnus_ignores, 'inconnus ignores')
        return (cles_sures, textes_surs)

    @classmethod
    def choisir_bloc_structurel(cls, pc_payload, candidats):
        """Choisit le bloc PS2 par langue, namespace et couverture des clés PC."""
        import LSL_MCL_ANALISES
        pc_valeurs = cls.parse_chaines(pc_payload)
        if not pc_valeurs:
            return None
        pc_cles = set(pc_valeurs)
        candidats_cible = []
        candidats_inconnus = []
        langues_connues_non_cibles = 0
        for candidat in candidats:
            valeurs = cls.parse_chaines(candidat['payload'])
            if not valeurs:
                continue
            cles = set(valeurs)
            communes = pc_cles & cles
            if not communes:
                continue
            couverture = len(communes) / len(pc_cles)
            union = pc_cles | cles
            similarite = len(communes) / len(union)
            langue_bloc, scores_langues = LSL_MCL_ANALISES.LSL_MCL_Analises.identifier_langue_bloc_texte(candidat['payload'])
            score = (couverture, similarite, scores_langues.get(V.LANGUE_CIBLE, 0))
            if langue_bloc == V.LANGUE_CIBLE:
                candidats_cible.append((score, candidat))
            elif langue_bloc == 'inconnue':
                candidats_inconnus.append((score, candidat))
            else:
                langues_connues_non_cibles += 1
        if candidats_cible:
            return max(candidats_cible, key=lambda element: element[0])[1]
        if candidats_inconnus and (not langues_connues_non_cibles):
            return max(candidats_inconnus, key=lambda element: element[0])[1]
        return None
