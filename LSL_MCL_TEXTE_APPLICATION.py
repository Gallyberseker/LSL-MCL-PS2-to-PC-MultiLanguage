"""Traitement ApplicationTextes des textes Larry MCL."""
from pathlib import Path
import re
import json
import LSL_MCL_VARIABLES as V

class ApplicationTextes:
    """Services textuels exposés par LSL_MCL_Textes."""

    @classmethod
    def charger_adaptations_pc(cls, langue_cible):
        """Charge les adaptations du catalogue PROFILS_LANGUES_PC.json pour la langue cible."""
        fichier = V.ROOT / 'PROFILS_LANGUES_PC.json'
        if not fichier.exists():
            print('[ADAPTATION PC] Profil absent :', fichier)
            return {}
        donnees = json.loads(fichier.read_text(encoding='utf-8'))
        langue = cls.normaliser_code_langue(langue_cible)
        langues = donnees.get('langues', {})
        profil = langues.get(langue) or langues.get('en', {})
        adaptations = profil.get('adaptations_pc', {})
        resultat = {}
        for source, destination in adaptations.items():
            source_normalisee = cls.normaliser_source_anglaise_jam(source.encode('cp1252'))
            resultat[source_normalisee] = destination.encode('cp1252')
        return resultat

    @classmethod
    def corriger_format_date_sauvegarde(cls, data_root, langue_cible):
        """FR : format de la date affichée dans Charger et Sauvegarder.

        AppInit.JAM / Global / DATA_AIS / DATEFRMT : DD/MM/YYYY HH:mm.
        Les lettres sont les jetons du jeu ; ce n'est pas un strftime Python.
        """
        from LSL_MCL_TEXTE_LANGUE_FR import FORMAT_DATE_SAUVEGARDE
        import LSL_MCL_JAMS
        import LSL_MCL_INJECTIONS
        if langue_cible.lower() != 'fr':
            return 0
        jam = data_root / 'JamFiles' / 'PC' / 'AppInit.JAM'
        if not jam.is_file():
            raise FileNotFoundError('[DATE SAUVEGARDE] AppInit.JAM absent : ' + str(jam))
        original = jam.read_bytes()
        sortie = bytearray(original)
        trouves = 0
        changements = 0
        for bloc in cls.blocs_texte(original):
            if bloc['namespace'].upper() != 'DATA_AIS':
                continue
            payload = bloc['payload']
            entrees = [m for m in V.ENTRY.finditer(payload) if m.group(2).upper() == b'DATEFRMT']
            if not entrees:
                continue
            if len(entrees) != 1 or trouves:
                raise RuntimeError('[DATE SAUVEGARDE] DATEFRMT ambigu dans AppInit.JAM')
            trouves += 1
            ancienne = entrees[0].group(4)
            nouvelle = FORMAT_DATE_SAUVEGARDE
            if ancienne == nouvelle:
                continue
            debut, fin = entrees[0].span(4)
            nouveau = payload[:debut] + nouvelle + payload[fin:]
            caracteres = cls._compter_caracteres(nouveau)
            nouveau, comptes = re.subn(b'ASCIIChar\\s*\\[\\s*\\d+\\s*\\]', f'ASCIIChar   [  {caracteres}  ]'.encode('ascii'), nouveau, count=1)
            if comptes != 1:
                raise RuntimeError('[DATE SAUVEGARDE] ASCIIChar introuvable')
            nouveau = LSL_MCL_INJECTIONS.LSL_MCL_Injection.appliquer_padding_espaces_jam(nouveau, len(payload))
            if nouveau is None:
                raise RuntimeError('[DATE SAUVEGARDE] Bloc DATA_AIS trop petit')
            sortie[bloc['begin']:bloc['end']] = nouveau
            changements += 1
        if not trouves:
            raise RuntimeError('[DATE SAUVEGARDE] DATEFRMT introuvable dans AppInit.JAM')
        if changements:
            resultat = bytes(sortie)
            if len(resultat) != len(original) or LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(resultat) != LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(original):
                raise RuntimeError('[DATE SAUVEGARDE] Structure JAM modifiée')
            cls._ecrire_jam(jam, resultat)
        print('[DATE SAUVEGARDE] FR / AppInit.JAM / DATEFRMT :', 'déjà DD/MM/YYYY HH:mm' if not changements else ancienne.decode('ascii', errors='replace') + ' -> DD/MM/YYYY HH:mm')
        return changements

    @classmethod
    def finaliser_textes_pc_specifiques(cls, data_root, langue_cible):
        """Applique les adaptations PC à taille fixe et contrôle la structure JAM."""
        import LSL_MCL_JAMS
        import LSL_MCL_INJECTIONS
        adaptations = cls.charger_adaptations_pc(langue_cible)
        if not adaptations:
            print('[ADAPTATION PC] Aucune adaptation pour cette langue.')
            return 0
        jam_root = data_root / 'JamFiles' / 'PC'
        total = 0
        utilisees = {source: 0 for source in adaptations}
        for jam in sorted(cls._fichiers_jam(jam_root)):
            original = jam.read_bytes()
            sortie = bytearray(original)
            changements_fichier = 0
            for bloc in cls.blocs_texte(original):
                payload = bloc['payload']
                matches = list(V.ENTRY.finditer(payload))
                if not matches:
                    continue
                morceaux = []
                position = 0
                changements_bloc = 0
                for match in matches:
                    morceaux.append(payload[position:match.start()])
                    ancien = match.group(4)
                    source = cls.normaliser_source_anglaise_jam(ancien)
                    nouveau = adaptations.get(source, ancien)
                    if nouveau != ancien:
                        changements_bloc += 1
                        utilisees[source] += 1
                    fin_cr = b'\r' if match.group(0).endswith(b'\r') else b''
                    morceaux.append(b'"' + match.group(2) + b'" "' + nouveau + b'"' + fin_cr)
                    position = match.end()
                if not changements_bloc:
                    continue
                morceaux.append(payload[position:])
                nouveau_payload = b''.join(morceaux)
                ascii_char = cls._compter_caracteres(nouveau_payload)
                nouveau_payload = re.sub(b'ASCIIChar\\s+\\[\\s*\\d+\\s*\\]', f'ASCIIChar   [  {ascii_char}  ]'.encode('ascii'), nouveau_payload, count=1)
                nouveau_payload = LSL_MCL_INJECTIONS.LSL_MCL_Injection.appliquer_padding_espaces_jam(nouveau_payload, len(payload))
                if nouveau_payload is None:
                    raise RuntimeError(f'{jam.name} : adaptation PC trop longue.')
                sortie[bloc['begin']:bloc['end']] = nouveau_payload
                changements_fichier += changements_bloc
            if not changements_fichier:
                continue
            resultat = bytes(sortie)
            if len(resultat) != len(original):
                raise RuntimeError(f'{jam.name} : taille totale modifiée.')
            if LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(resultat) != LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(original):
                raise RuntimeError(f'{jam.name} : table des chunks modifiée.')
            cls._ecrire_jam(jam, resultat)
            total += changements_fichier
        for source, nombre in utilisees.items():
            etat = 'appliquée' if nombre else 'déjà traduite ou absente'
            print('[ADAPTATION PC]', source, ':', etat)
        print('[ADAPTATION PC] Textes modifiés :', total)
        return total

    @classmethod
    def traduire_tous_jam_localises(cls, data_root, langue_cible):
        """Traduit tous les JAM avec la mémoire PS2 et renvoie le bilan conservé en mémoire."""
        import LSL_MCL_EXTRACTIONS
        V.LANGUE_CIBLE = langue_cible.lower()
        ps2_index = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.source_ps2_index()
        jam_root = data_root / 'JamFiles' / 'PC'
        rapports = []
        textes_a_verifier = []
        traductions_globales, traductions_textes = cls.construire_memoire_jam_globale(jam_root, ps2_index)
        for pc in sorted(cls._fichiers_jam(jam_root)):
            relatif = pc.relative_to(jam_root)
            ps2 = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.trouver_ps2_jam(relatif, ps2_index)
            original = pc.read_bytes()
            nouveau, blocs, chaines = cls.traduire_jam_sans_deplacement(original, ps2.read_bytes() if ps2 is not None else b'', str(relatif), traductions_globales, traductions_textes)
            if len(nouveau) != len(original):
                raise RuntimeError(f'{relatif}: taille JAM modifiee')
            if chaines:
                cls._ecrire_jam(pc, nouveau)
            if V.LANGUE_CIBLE != 'en':
                for bloc in cls.blocs_texte(nouveau):
                    for cle, valeurs in cls.parse_chaines_multiples(bloc['payload']).items():
                        for occurrence, valeur in enumerate(valeurs, start=1):
                            score_en = cls.score_langue({cle: valeur}, 'en')
                            score_cible = cls.score_langue({cle: valeur}, V.LANGUE_CIBLE)
                            if score_en > 0 and score_en > score_cible:
                                textes_a_verifier.append({'fichier': str(relatif).replace('\\', '/'), 'namespace': bloc['namespace'], 'cle': cle, 'occurrence': occurrence, 'valeur': valeur.decode('cp1252', errors='replace')})
            rapports.append({'fichier': str(relatif).replace('\\', '/'), 'etat': 'traduit' if chaines else 'inchange', 'source_ps2_directe': str(ps2) if ps2 is not None else None, 'blocs': blocs, 'chaines': chaines})
        resume = {'langue': V.LANGUE_CIBLE, 'nom_langue': V.PROFILS_LANGUES[V.LANGUE_CIBLE]['nom'], 'fichiers_analyses': len(rapports), 'fichiers_modifies': sum((item.get('chaines', 0) > 0 for item in rapports)), 'chaines_traduites': sum((item.get('chaines', 0) for item in rapports)), 'textes_probablement_non_localises': len(textes_a_verifier), 'a_verifier': textes_a_verifier, 'details': rapports}
        print()
        print('[TRADUCTION AUTO] Langue :', resume['nom_langue'])
        print('[TRADUCTION AUTO] Fichiers modifies :', resume['fichiers_modifies'])
        print('[TRADUCTION AUTO] Chaines traduites :', resume['chaines_traduites'])
        print('[TRADUCTION AUTO] Textes encore probablement anglais :', resume['textes_probablement_non_localises'])
        return resume

    @staticmethod
    def _ecrire_jam(fichier, donnees):
        """Publie un JAM à taille fixe avec le service d’écriture partagé des injections."""
        from LSL_MCL_ECRITURE_JAM import remplacer_emplacement
        fichier = Path(fichier)
        if fichier.stat().st_size != len(donnees):
            raise RuntimeError(f'{fichier.name} : taille JAM modifiée avant écriture.')
        remplacer_emplacement(fichier, 0, len(donnees), donnees)
