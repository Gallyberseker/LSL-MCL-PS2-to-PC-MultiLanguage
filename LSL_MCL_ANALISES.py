"""Analyse des langues, marqueurs de localisation et diagnostics JAM de Larry MCL."""
from pathlib import Path
import LSL_MCL_VARIABLES as V
import LSL_MCL_COMPUTER
import LSL_MCL_JAMS
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES

class LSL_MCL_Analises:
    """Fournit les analyses utilisées par la construction et les diagnostics."""

    @staticmethod
    def lire_marqueur_localisation_pc(data_root):
        """Lit le marqueur UTF-8 de localisation présent dans le dossier Data.

Retourne son contenu, ou None si le marqueur est absent ou illisible.
Les erreurs de lecture sont conservées dans les logs console."""
        data_root = Path(data_root)
        marqueur = data_root / V.MARQUEUR_LOCALISATION_PC
        if not marqueur.exists():
            return None
        try:
            return marqueur.read_text(encoding='utf-8', errors='replace')
        except OSError as erreur:
            print('[MARQUEUR] Impossible de lire :', marqueur)
            print('[MARQUEUR] Erreur :', erreur)
            return None

    @staticmethod
    def ecrire_marqueur_localisation_pc(data_root, langue_cible):
        """Écrit la langue installée, son origine et l’édition PS2 dans le marqueur Data.

Crée le dossier si nécessaire et retourne le chemin du marqueur.
Les erreurs d’écriture sont propagées ; les informations sont journalisées."""
        data_root = Path(data_root)
        data_root.mkdir(parents=True, exist_ok=True)
        try:
            langue = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper()
        except Exception:
            langue = str(langue_cible).upper()
        executable_ps2 = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(V.PS2_VERSION)
        if executable_ps2 is not None:
            edition_ps2 = executable_ps2.name.upper()
        else:
            edition_ps2 = 'INCONNUE'
        marqueur = data_root / V.MARQUEUR_LOCALISATION_PC
        if not V.ACTIVE_TRADUCTION_TEXTE_JAM:
            source = 'données PC (géométrie)'
        elif langue.lower() in V.PROFILS_LANGUES:
            source = 'PS2'
        else:
            source = 'catalogue autre langue'
        contenu = f'LEISURE SUIT LARRY MCL - LOCALISATION\n======================================\n\nVersion installee : {langue}\nSource localisation : {source}\nEdition PS2 : {edition_ps2}\nInstallation modifiee : OUI\n'
        marqueur.write_text(contenu, encoding='utf-8')
        print('[MARQUEUR] Localisation enregistree :', marqueur)
        print('[MARQUEUR] Langue :', langue)
        print('[MARQUEUR] Edition PS2 :', edition_ps2)
        return marqueur

    @staticmethod
    def analyser_jam_detaille(fichier, racine, plateforme):
        """Retourne un inventaire détaillé des ressources et structures d’un JAM.

Inclut blocs, textes structurés, namespaces, rectangles, polices et
liaisons détectées. Les erreurs des analyses de blocs et de textes sont
consignées dans le résultat. Ne modifie pas le fichier."""
        import LSL_MCL_DIAGNOSTICS
        import LSL_MCL_EXTRACTIONS
        import hashlib
        import re
        data = fichier.read_bytes()
        resultat = {'plateforme': plateforme, 'fichier': str(fichier.relative_to(racine)).replace('\\', '/'), 'adresse': str(fichier.resolve()), 'taille': len(data), 'sha256': LSL_MCL_DIAGNOSTICS.LSL_MCL_Diagnostics.empreinte_sha256(fichier, data=data), 'chunks': [], 'chaines': [], 'index_cles': [], 'espaces_noms': [], 'rectangles': [], 'styles': [], 'liaisons': [], 'livre_noir': [], 'erreurs': []}
        try:
            chunks = LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(data)
            for index, chunk in enumerate(chunks):
                header, taille1, taille2, debut, fin = chunk
                contenu = data[debut:fin]
                resultat['chunks'].append({'index': index, 'header_hex': header.hex() if isinstance(header, bytes) else str(header), 'offset_debut': debut, 'offset_debut_hex': f'0x{debut:X}', 'offset_fin': fin, 'offset_fin_hex': f'0x{fin:X}', 'taille_declaree_1': taille1, 'taille_declaree_2': taille2, 'taille_reelle': len(contenu), 'alignement_4': debut % 4, 'alignement_16': debut % 16, 'structure_valide': taille1 == taille2 and fin <= len(data), 'sha256': hashlib.sha256(contenu).hexdigest()})
        except Exception as erreur:
            resultat['erreurs'].append(f'Chunks JAM : {erreur}')
        try:
            resultat['chaines'] = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.extraire_entrees_textes_jam(fichier, racine, plateforme, data=data)
            index_cles = {}
            for entree in resultat['chaines']:
                identifiant = (entree['namespace'], entree['cle'])
                fiche = index_cles.setdefault(identifiant, {'namespace': entree['namespace'], 'cle': entree['cle'], 'nombre_occurrences': 0, 'langues': {}, 'offsets_valeurs': []})
                fiche['nombre_occurrences'] += 1
                langue = entree.get('langue_bloc', 'inconnue')
                fiche['langues'][langue] = fiche['langues'].get(langue, 0) + 1
                fiche['offsets_valeurs'].append({'offset': entree['offset_valeur'], 'offset_hex': entree['offset_valeur_hex'], 'langue': langue, 'numero_bloc_texte': entree['numero_bloc_texte']})
            resultat['index_cles'] = sorted(index_cles.values(), key=lambda fiche: (fiche['namespace'], fiche['cle']))
        except Exception as erreur:
            resultat['erreurs'].append(f'Textes structurés JAM : {erreur}')
        motif_namespace = re.compile(b'NameSpace\\s+"([^"]+)"')
        for correspondance in motif_namespace.finditer(data):
            resultat['espaces_noms'].append({'nom': correspondance.group(1).decode('cp1252', errors='replace'), 'offset': correspondance.start(), 'offset_hex': f'0x{correspondance.start():X}'})
        motif_rectangle = re.compile(b'Rectangle\\s+(-?\\d+(?:\\.\\d+)?)\\s+(-?\\d+(?:\\.\\d+)?)\\s+(-?\\d+(?:\\.\\d+)?)\\s+(-?\\d+(?:\\.\\d+)?)')
        for correspondance in motif_rectangle.finditer(data):
            valeurs = [float(valeur) for valeur in correspondance.groups()]
            resultat['rectangles'].append({'offset': correspondance.start(), 'offset_hex': f'0x{correspondance.start():X}', 'gauche': valeurs[0], 'haut': valeurs[1], 'droite': valeurs[2], 'bas': valeurs[3], 'largeur': valeurs[2] - valeurs[0], 'hauteur': valeurs[3] - valeurs[1]})
        motif_style = re.compile(b'Name\\s+"([^"]+)".{0,700}?Scale\\s+(-?\\d+(?:\\.\\d+)?)\\s+(-?\\d+(?:\\.\\d+)?)', re.DOTALL)
        for correspondance in motif_style.finditer(data):
            resultat['styles'].append({'nom': correspondance.group(1).decode('cp1252', errors='replace'), 'echelle_x': float(correspondance.group(2)), 'echelle_y': float(correspondance.group(3)), 'offset': correspondance.start(), 'offset_hex': f'0x{correspondance.start():X}'})
        motif_liaison = re.compile(b'(?:DataLink|DataComponentAsset)\\s+"([^"]+)".{0,500}?(?:Name|Parent)\\s+"([^"]*)"', re.DOTALL)
        for correspondance in motif_liaison.finditer(data):
            resultat['liaisons'].append({'identifiant': correspondance.group(1).decode('cp1252', errors='replace'), 'reference': correspondance.group(2).decode('cp1252', errors='replace'), 'offset': correspondance.start(), 'offset_hex': f'0x{correspondance.start():X}'})
        marqueurs_livre = (b'StatsScreen', b'StuffGotten', b'OverallPlayTime', b'BlackBook', b'BookMenu', b'ITITLE', b'STITLE', b'DESC_WHT', b'DESC_GRY', b'OBJECTIF', b'FILLES', b'OBJETS', b'TENUES', b'STATS')
        for marqueur in marqueurs_livre:
            position = 0
            while True:
                position = data.find(marqueur, position)
                if position < 0:
                    break
                debut = max(0, position - 500)
                fin = min(len(data), position + 1000)
                contexte_brut = data[debut:fin].decode('cp1252', errors='ignore')
                contexte_texte = ''.join((caractere if caractere in '\r\n\t' or ord(caractere) >= 32 else ' ' for caractere in contexte_brut))
                contexte_texte = re.sub('[ \\t]{2,}', ' ', contexte_texte).strip()
                resultat['livre_noir'].append({'marqueur': marqueur.decode('ascii', errors='replace'), 'offset': position, 'offset_hex': f'0x{position:X}', 'contexte_texte': contexte_texte})
                position += len(marqueur)
        return resultat

    @staticmethod
    def identifier_langue_bloc_texte(payload):
        """Retourne la langue probable du bloc et les scores FR, EN, DE, ES et IT.

Une langue est retenue si son score atteint 3 et dépasse strictement
le deuxième meilleur score ; sinon retourne "inconnue"."""
        valeurs = LSL_MCL_TEXTES.LSL_MCL_Textes.parse_chaines(payload)
        codes = ('fr', 'en', 'de', 'es', 'it')
        scores = {code: LSL_MCL_TEXTES.LSL_MCL_Textes.score_langue(valeurs, code) for code in codes}
        classement = sorted(scores.items(), key=lambda element: element[1], reverse=True)
        meilleur_code, meilleur_score = classement[0]
        deuxieme_score = classement[1][1]
        langue = meilleur_code if meilleur_score >= 3 and meilleur_score > deuxieme_score else 'inconnue'
        return (langue, scores)

    @staticmethod
    def score_francais_bloc(payload):
        """Calcule le score français des chaînes structurées du bloc.

Conserve le comptage historique de mots indicateurs comme solution
de repli lorsque le calcul principal échoue ou ne retourne pas un nombre."""
        try:
            score = LSL_MCL_TEXTES.LSL_MCL_Textes.score_francais(LSL_MCL_TEXTES.LSL_MCL_Textes.parse_chaines(payload))
            if isinstance(score, (int, float)):
                return score
        except Exception:
            pass
        mots = (b'sauveg', b'charg', b'supprim', b'retour', b'quitter', b'choisissez', b'objectif', b'progression', b'annuler', b'fichier', b'partie')
        texte = payload.lower()
        return sum((texte.count(mot) for mot in mots))

    @staticmethod
    def analyser_adaptations_console_vers_pc(resultat_textes, resultat_tri, dossier_rapport):
        """Analyse les incompatibilités de textes PS2 avec les variables PC.

Regroupe les occurrences et classe les propositions d’adaptation.
Écrit les rapports JSON dans le dossier demandé et retourne les analyses,
leur résumé et leur dossier. Aucun JAM n’est modifié."""
        import json
        import re
        import unicodedata
        dossier = Path(dossier_rapport) / 'ADAPTATION_CONSOLE_VERS_PC'
        dossier.mkdir(parents=True, exist_ok=True)
        langue_cible = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(V.LANGUE_CIBLE)
        textes_console = resultat_tri.get('textes_console', [])
        correspondances = resultat_textes.get('correspondances', [])

        def identifiant(fichier, namespace, cle):
            """Normalise le chemin, le namespace et la clé pour apparier les entrées."""
            return (LSL_MCL_OUTILS.LSL_MCL_Outils.normaliser_chemin_jam(fichier or ''), namespace or '', cle or '')

        def normaliser_recherche(texte):
            """Normalise un texte pour comparer les marqueurs matériels de console."""
            texte = unicodedata.normalize('NFKC', texte or '').casefold()
            return ' '.join(texte.split())

        def variables(texte):
            """Extrait les variables de substitution présentes dans le texte."""
            return re.findall('%[A-Za-z]', texte or '')

        def variables_normalisees(texte):
            """Retourne les variables en minuscules et triées pour comparaison."""
            return sorted((variable.casefold() for variable in variables(texte)))
        marqueurs_interdits = ('memory card', 'carte memoire', 'carte mémoire', 'speicherkarte', 'tarjeta de memoria', 'scheda di memoria', 'playstation', 'sony', 'controller', 'manette', 'mando', 'controlador')
        raccords_finaux = (' sur la', ' sur le', ' dans la', ' dans le', ' de la', ' du', ' on the', ' in the', ' from the', ' of the', ' auf der', ' auf dem', ' in der', ' von der', ' en la', ' en el', ' de la', ' del', ' sulla', ' sul', ' nella', ' nel', ' della', ' del')

        def contient_console(texte, variables_pc=()):
            """Détecte les références matérielles PS2 incompatibles avec le texte PC."""
            normalise = normaliser_recherche(texte)
            pc_attend_m = any((variable.casefold() == '%m' for variable in variables_pc))
            return '%m' in variables_normalisees(texte) and (not pc_attend_m) or any((marqueur in normalise for marqueur in marqueurs_interdits))
        mots_liaison_finaux = {'a', 'à', 'au', 'aux', 'de', 'des', 'du', 'dans', 'en', 'la', 'le', 'les', 'par', 'pour', 'sur', 'at', 'by', 'for', 'from', 'in', 'of', 'on', 'the', 'to', 'am', 'an', 'auf', 'aus', 'bei', 'der', 'die', 'im', 'in', 'mit', 'von', 'vom', 'zu', 'zum', 'zur', 'a', 'al', 'de', 'del', 'el', 'en', 'la', 'las', 'los', 'para', 'por', 'a', 'al', 'alla', 'dalla', 'della', 'di', 'in', 'nella', 'nel', 'per', 'sul', 'sulla'}

        def normaliser_casse_variables(texte, variables_pc):
            """Rétablit la casse des variables attendues par la version PC."""
            trouvees = list(re.finditer('%[A-Za-z]', texte or ''))
            if len(trouvees) != len(variables_pc):
                return texte
            if [m.group(0).casefold() for m in trouvees] != [variable.casefold() for variable in variables_pc]:
                return texte
            morceaux = []
            position = 0
            for match, variable_pc in zip(trouvees, variables_pc):
                morceaux.append(texte[position:match.start()])
                morceaux.append(variable_pc)
                position = match.end()
            morceaux.append(texte[position:])
            return ''.join(morceaux)

        def proposition_semantiquement_complete(texte, variables_pc):
            """Écarte les propositions vides, trop courtes ou grammaticalement tronquées."""
            sans_ponctuation = re.sub('[.!?…\\s]+$', '', texte or '')
            if not sans_ponctuation:
                return False
            if re.match("^(?:la|le|les)\\s+n[’']|^(?:the)\\s+(?:is|was|has)|^(?:der|die|das)\\s+(?:ist|wurde)|^(?:el|la|los|las)\\s+(?:es|está|se)|^(?:il|lo|la|gli|le)\\s+(?:è|e|non)", sans_ponctuation.casefold()):
                return False
            derniere_variable = re.search('%[A-Za-z]$', sans_ponctuation)
            if derniere_variable:
                avant_variable = sans_ponctuation[:derniere_variable.start()]
                mots_avant = re.findall('[^\\W\\d_]+', avant_variable, flags=re.UNICODE)
                return bool(mots_avant)
            sans_variables = re.sub('%[A-Za-z]', ' ', sans_ponctuation)
            mots = re.findall('[^\\W\\d_]+', sans_variables, flags=re.UNICODE)
            if len(mots) < 2:
                return False
            return mots[-1].casefold() not in mots_liaison_finaux

        def nettoyer_proposition(texte_ps2, variables_pc, texte_pc):
            """Retire prudemment les clauses propres à la console et conserve la ponctuation PC."""
            texte = (texte_ps2 or '').strip()
            normalise = normaliser_recherche(texte)
            positions = [normalise.find(marqueur) for marqueur in marqueurs_interdits if marqueur in normalise]
            pc_attend_m = any((variable.casefold() == '%m' for variable in variables_pc))
            variable_memoire = re.search('%[mM](?=\\W|$)', texte)
            if positions and variable_memoire and (not pc_attend_m):
                position = min(positions)
                prefixe = texte[:position]
                prefixe_normalise = normaliser_recherche(prefixe)
                debut_retrait = position
                for raccord in sorted(raccords_finaux, key=len, reverse=True):
                    if prefixe_normalise.endswith(raccord):
                        debut_retrait = max(0, position - len(raccord))
                        break
                texte = (texte[:debut_retrait].rstrip() + ' ' + texte[variable_memoire.end():].lstrip()).strip()
                phrases = re.split('(?<=[.!?])\\s+', texte)
                phrases_utiles = [phrase for phrase in phrases if phrase.strip() and (not contient_console(phrase, variables_pc))]
                texte = ' '.join(phrases_utiles).strip()
            elif positions:
                position = min(positions)
                prefixe = texte[:position].rstrip(' ,;:-.()[]')
                prefixe_normalise = normaliser_recherche(prefixe)
                for raccord in sorted(raccords_finaux, key=len, reverse=True):
                    if prefixe_normalise.endswith(raccord):
                        prefixe = prefixe[:len(prefixe) - len(raccord)].rstrip()
                        break
                texte = prefixe
            attendues = [variable.casefold() for variable in variables_pc]
            texte = re.sub('\\s*%[mM](?=\\W|$)', lambda match: match.group(0) if '%m' in attendues else '', texte)
            texte = re.sub('\\s+([,.;:!?])', '\\1', texte)
            texte = re.sub('[ \\t]{2,}', ' ', texte).strip()
            ponctuation_pc = re.search('([.!?]+)\\s*$', texte_pc or '')
            if texte and ponctuation_pc:
                texte = re.sub('[.!?…]+\\s*$', '', texte).rstrip()
                texte += ponctuation_pc.group(1)
            return texte
        index_pc = {}
        for comparaison in correspondances:
            index_pc[identifiant(comparaison.get('fichier_ps2'), comparaison.get('namespace'), comparaison.get('cle'))] = comparaison
        groupes = {}
        for entree in textes_console:
            cle_groupe = (*identifiant(entree.get('fichier'), entree.get('namespace'), entree.get('cle')), entree.get('langue', 'inconnue'), entree.get('valeur', ''))
            groupe = groupes.setdefault(cle_groupe, {'entree': entree, 'occurrences': []})
            groupe['occurrences'].append({'chunk_index': entree.get('chunk_index'), 'numero_bloc': entree.get('numero_bloc'), 'offset_valeur': entree.get('offset_valeur'), 'offset_valeur_hex': entree.get('offset_valeur_hex')})
        analyses = []
        for groupe in groupes.values():
            entree = groupe['entree']
            cle_index = identifiant(entree.get('fichier'), entree.get('namespace'), entree.get('cle'))
            comparaison = index_pc.get(cle_index)
            texte_ps2 = entree.get('valeur', '')
            langue = entree.get('langue', 'inconnue')
            fiche = {'fichier_ps2': entree.get('fichier'), 'namespace': entree.get('namespace'), 'cle': entree.get('cle'), 'langue': langue, 'texte_ps2': texte_ps2, 'variables_ps2': variables(texte_ps2), 'marqueurs_console': entree.get('marqueurs_console', []), 'nombre_occurrences': len(groupe['occurrences']), 'occurrences': groupe['occurrences'], 'langue_cible_courante': langue_cible}
            if comparaison is None:
                fiche.update({'texte_pc': None, 'variables_pc': [], 'classe': 'CLE_EXCLUSIVEMENT_PS2', 'texte_pc_propose': None, 'decision': 'REJET', 'raison': 'CLE_ABSENTE_PC'})
                analyses.append(fiche)
                continue
            texte_pc = comparaison.get('valeur_pc', '')
            variables_pc = comparaison.get('variables_pc', variables(texte_pc))
            variables_ps2 = comparaison.get('variables_ps2', variables(texte_ps2))
            variables_pc_norm = sorted((v.casefold() for v in variables_pc))
            variables_ps2_norm = sorted((v.casefold() for v in variables_ps2))
            proposition = nettoyer_proposition(texte_ps2, variables_pc, texte_pc)
            variables_proposition = variables_normalisees(proposition)
            proposition = normaliser_casse_variables(proposition, variables_pc)
            mots_proposition = re.findall('[^\\W\\d_]+', re.sub('%[A-Za-z]', ' ', proposition), flags=re.UNICODE)
            fiche.update({'fichier_pc': comparaison.get('fichier_pc'), 'texte_pc': texte_pc, 'variables_pc': variables_pc, 'texte_pc_propose': proposition or None, 'variables_proposition': variables(proposition)})
            if variables_pc_norm == variables_ps2_norm:
                casse_seule = sorted(variables_pc) != sorted(variables_ps2)
                classe = 'CASSE_VARIABLE_DIFFERENTE' if casse_seule else 'VARIABLES_COMPATIBLES'
            elif all((variables_ps2_norm.count(variable) >= variables_pc_norm.count(variable) for variable in set(variables_pc_norm))):
                classe = 'VARIABLE_CONSOLE_SUPPLEMENTAIRE'
            else:
                classe = 'VARIABLE_PC_ABSENTE_OU_SEMANTIQUE_DIFFERENTE'
            fiche['classe'] = classe
            if classe == 'VARIABLE_PC_ABSENTE_OU_SEMANTIQUE_DIFFERENTE':
                fiche.update({'decision': 'REJET', 'raison': 'VARIABLE_PC_OBLIGATOIRE_NON_CONSERVEE'})
            elif classe in {'VARIABLE_CONSOLE_SUPPLEMENTAIRE', 'CASSE_VARIABLE_DIFFERENTE'} and proposition and (variables_proposition == variables_pc_norm) and (not contient_console(proposition, variables_pc)) and proposition_semantiquement_complete(proposition, variables_pc):
                fiche.update({'decision': 'NORMALISATION' if classe == 'CASSE_VARIABLE_DIFFERENTE' else 'AUTO', 'raison': 'CLAUSE_CONSOLE_RETIREE_VARIABLES_PC_CONSERVEES'})
            else:
                fiche.update({'decision': 'REVISION', 'raison': 'PROPOSITION_TROP_COURTE_OU_AMBIGUE' if len(mots_proposition) < 2 or not proposition_semantiquement_complete(proposition, variables_pc) else 'ELEMENT_CONSOLE_OU_VARIABLE_INCOMPATIBLE_RESTANT'})
            analyses.append(fiche)
        analyses.sort(key=lambda fiche: (fiche.get('langue') or '', fiche.get('fichier_ps2') or '', fiche.get('namespace') or '', fiche.get('cle') or '', fiche.get('texte_ps2') or ''))
        decisions = {}
        classes = {}
        for fiche in analyses:
            decisions[fiche['decision']] = decisions.get(fiche['decision'], 0) + 1
            classes[fiche['classe']] = classes.get(fiche['classe'], 0) + 1
        analyses_langue_cible = [fiche for fiche in analyses if fiche.get('langue') == langue_cible]
        cles_logiques = {(fiche.get('fichier_ps2'), fiche.get('namespace'), fiche.get('cle')) for fiche in analyses}
        decisions_cible = {}
        for fiche in analyses_langue_cible:
            decision = fiche['decision']
            decisions_cible[decision] = decisions_cible.get(decision, 0) + 1
        resume = {'langue_cible_courante': langue_cible, 'nombre_detections_console_brutes': len(textes_console), 'nombre_variantes_langues_dedupliquees': len(analyses), 'nombre_cles_logiques': len(cles_logiques), 'nombre_fiches_langue_cible': len(analyses_langue_cible), 'decisions_toutes_langues': decisions, 'decisions_langue_cible': decisions_cible, 'classes': classes, 'aucun_jam_modifie': True, 'regle_securite': "AUTO exige la conservation exacte des variables PC, l'absence de marqueur console et une phrase non vide."}
        (dossier / 'ADAPTATION_CONSOLE_VERS_PC.json').write_text(json.dumps(analyses, ensure_ascii=False, indent=2), encoding='utf-8')
        (dossier / 'ADAPTATION_CONSOLE_VERS_PC_RESUME.json').write_text(json.dumps(resume, ensure_ascii=False, indent=2), encoding='utf-8')
        (dossier / f'ADAPTATION_CONSOLE_VERS_PC_{langue_cible.upper()}.json').write_text(json.dumps(analyses_langue_cible, ensure_ascii=False, indent=2), encoding='utf-8')
        print('[ADAPTATION PC] Variantes langues :', len(analyses))
        print('[ADAPTATION PC] Clés logiques :', len(cles_logiques))
        print('[ADAPTATION PC] Décisions langue cible :', decisions_cible)
        print('[ADAPTATION PC] Rapports :', dossier)
        return {'analyses': analyses, 'resume': resume, 'dossier': dossier}

    @staticmethod
    def analyser_fichier_complet(fichier, racine):
        """Retourne les métadonnées, le type détecté et le SHA-256 d’un fichier.

En cas d’échec, retourne une fiche avec le détail de l’erreur.
Ne modifie pas le fichier."""
        import LSL_MCL_DIAGNOSTICS
        import os
        from datetime import datetime
        informations = {'chemin_relatif': str(fichier.relative_to(racine)).replace('\\', '/'), 'adresse_absolue': str(fichier.resolve()), 'nom': fichier.name, 'extension': fichier.suffix.lower()}
        try:
            statistiques = fichier.stat()
            with fichier.open('rb') as flux:
                entete = flux.read(64)
            informations.update({'taille': statistiques.st_size, 'taille_hexadecimal': f'0x{statistiques.st_size:X}', 'date_modification': datetime.fromtimestamp(statistiques.st_mtime).isoformat(timespec='seconds'), 'lecture_seule': not os.access(fichier, os.W_OK), 'type': LSL_MCL_DIAGNOSTICS.LSL_MCL_Diagnostics.identifier_type_fichier(fichier, entete), 'entete_hexadecimal': entete.hex(), 'sha256': LSL_MCL_DIAGNOSTICS.LSL_MCL_Diagnostics.empreinte_sha256(fichier), 'erreur': None})
        except Exception as erreur:
            informations.update({'taille': 0, 'type': 'ERREUR', 'sha256': None, 'erreur': str(erreur)})
        return informations
