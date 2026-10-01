"""Recherche indexée des voix russes dans les banques AFS du moteur existant."""
from pathlib import Path
import csv
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import LSL_MCL_VARIABLES as V
import LSL_MCL_OUTILS
import LSL_MCL_LANGUAGES
import LSL_MCL_TEXTES
from LSL_MCL_AUDIOS import LSL_MCL_Audios

class LSL_MCL_Audios_RU:
    """Localise l'AFS gameplay russe en réutilisant les codecs et gabarits PC."""

    @staticmethod
    def _progression(etape, actuel, total, detail='', force=False):
        """Affiche une barre compacte, limitée à quatre rafraîchissements par seconde."""
        maintenant = time.monotonic()
        precedent = getattr(LSL_MCL_Audios_RU, '_dernier_affichage', 0.0)
        if not force and actuel < total and (maintenant - precedent < 0.25):
            return
        LSL_MCL_Audios_RU._dernier_affichage = maintenant
        ratio = min(1.0, actuel / total) if total else 1.0
        largeur = 25
        barre = '█' * int(ratio * largeur) + '░' * (largeur - int(ratio * largeur))
        ligne = f'[AFS RU] {etape} [{barre}] {actuel}/{total} ({ratio:.0%}) {detail}'
        print('\r' + ligne[:150].ljust(150), end='\n' if actuel >= total else '', flush=True)

    @staticmethod
    def _indexer(noms):
        """Prépare les correspondances exactes et par nom sans extension."""
        exacts, stems, marqueurs = ({}, {}, [])
        for index, nom in enumerate(noms):
            if not nom:
                continue
            normalise = LSL_MCL_Audios.nom_afs(nom)
            exacts.setdefault(normalise, []).append(index)
            stems.setdefault(Path(normalise).stem, []).append(index)
            if LSL_MCL_LANGUAGES.LSL_MCL_Languages.texte_contient_marqueur_langue(nom, 'ru'):
                marqueurs.append((index, normalise))
        return (exacts, stems, marqueurs)

    @staticmethod
    def _choisir(index, nom_pc):
        """Applique les mêmes priorités que le moteur audio, sans rescanner l'AFS."""
        exacts, stems, marqueurs = index
        normalise = LSL_MCL_Audios.nom_afs(nom_pc)
        suffixe = Path(normalise).suffix
        base = Path(normalise).stem
        candidats = [i for i, nom in marqueurs if Path(nom).suffix == suffixe and (base in Path(nom).stem or Path(nom).stem in base)]
        if len(candidats) == 1:
            return candidats[0]
        if len(exacts.get(normalise, ())) == 1:
            return exacts[normalise][0]
        if len(stems.get(base, ())) == 1:
            return stems[base][0]
        return None

    @staticmethod
    def _convertir_lot(travaux, max_workers=None):
        """Convertit plusieurs pistes indépendantes en parallèle, sans modifier les AFS."""
        if not travaux:
            return {}
        if max_workers is None:
            max_workers = min(4, max(1, (os.cpu_count() or 2) // 2))
        max_workers = min(max_workers, len(travaux))
        resultats = {}

        def convertir(travail):
            k, source_index, nom, ps_nom, source, original = travail
            try:
                conversion, detail = LSL_MCL_Audios.convertir_audio_pour_pc(source, original, ps_nom)
            except (OSError, ValueError, RuntimeError) as erreur:
                conversion, detail = LSL_MCL_Audios.refus_audio(f'Echec de la conversion : {erreur}', source, original)
            return (k, source_index, nom, ps_nom, conversion, detail)
        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix='audio_ru') as pool:
            futurs = {pool.submit(convertir, travail): travail for travail in travaux}
            termines = 0
            for futur in as_completed(futurs):
                resultat = futur.result()
                resultats[resultat[0]] = resultat
                termines += 1
                LSL_MCL_Audios_RU._progression('Conversions RU', termines, len(travaux), resultat[2], force=termines == len(travaux))
        return resultats

    @staticmethod
    def localiser_afs_gameplay(data_root, langue_cible='ru'):
        """Injecte les voix de la langue cible dans les banques gameplay PC et consigne les entrées pour la synchronisation AOS."""
        if LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible) != 'ru':
            raise ValueError('Ce module est réservé à la langue russe')
        dossier_pc = Path(data_root) / 'Audio' / 'CRI'
        dossier_ps2 = V.PS2_VERSION / 'Data' / 'Audio' / 'CRI'
        pc_path = LSL_MCL_OUTILS.LSL_MCL_Outils.trouver_fichier_ci(dossier_pc, 'afs.afs')
        ps_path = LSL_MCL_LANGUAGES.LSL_MCL_Languages.trouver_fichier_langue(dossier_ps2, 'afs.afs', langue_cible)
        if pc_path is None or ps_path is None:
            print('[AFS RU] afs.afs absent.')
            return 0
        A = LSL_MCL_Audios
        pc_raw = pc_path.read_bytes()
        ps_raw = ps_path.read_bytes()
        pc = A.lire_afs(pc_raw)
        ps = A.lire_afs(ps_raw)
        index_top = LSL_MCL_Audios_RU._indexer(ps['names'])
        top_payloads = list(pc['payloads'])
        bilan, utilises = ([], set())
        remplaces = conteneurs = 0
        banques = sum((payload.startswith(b'AFS\x00') for payload in pc['payloads']))
        avance = 0
        cache_ps2 = {}
        for i, pc_payload in enumerate(pc['payloads']):
            if not pc_payload.startswith(b'AFS\x00'):
                continue
            avance += 1
            nom_conteneur = pc['names'][i] if i < len(pc['names']) else ''
            print(f'\n[AFS RU] Banque {avance}/{banques} : {nom_conteneur}', flush=True)
            j = LSL_MCL_Audios_RU._choisir(index_top, nom_conteneur)
            if j is None:
                bilan.append((nom_conteneur, '', '', 'CONTENEUR_PC_SANS_CORRESPONDANCE', ''))
                continue
            ps_payload = ps['payloads'][j]
            if not ps_payload.startswith(b'AFS\x00'):
                bilan.append((nom_conteneur, '', '', 'CONTENEUR_PS2_NON_AFS', ''))
                continue
            try:
                pc_inner = A.lire_afs(pc_payload)
                ps_inner = cache_ps2.get(j)
                if ps_inner is None:
                    ps_inner = A.lire_afs(ps_payload)
                    cache_ps2[j] = ps_inner
            except (ValueError, IndexError) as erreur:
                bilan.append((nom_conteneur, '', '', 'CONTENEUR_ILLISIBLE', str(erreur)))
                continue
            index_inner = LSL_MCL_Audios_RU._indexer(ps_inner['names'])
            inner_payloads = list(pc_inner['payloads'])
            changed = 0
            travaux = []
            for k, nom in enumerate(pc_inner['names']):
                if not A.nom_afs(nom).endswith(('.adx', '.ahx')):
                    continue
                source_index = LSL_MCL_Audios_RU._choisir(index_inner, nom)
                if source_index is None:
                    bilan.append((nom_conteneur, nom, '', 'SANS_CORRESPONDANCE', ''))
                    continue
                ps_nom = ps_inner['names'][source_index]
                source = ps_inner['payloads'][source_index]
                original = pc_inner['payloads'][k]
                pc_adx = A.analyser_entete_adx(original)
                different = len(source) < 20 or len(original) < 20 or source[4] != original[4] or (source[7] != original[7]) or (source[8:12] != original[8:12]) or (source[4] not in (16, 17) and source[18] != original[18])
                if pc_adx and different:
                    travaux.append((k, source_index, nom, ps_nom, source, original))
                    continue
                if different:
                    bilan.append((nom_conteneur, nom, ps_nom, 'CODEC_OU_FORMAT_INCOMPATIBLE', A.refus_audio('Conversion non definie pour cette entree', source, original)[1]))
                    continue
                utilises.add((j, source_index))
                if original == source:
                    bilan.append((nom_conteneur, nom, ps_nom, 'IDENTIQUE', ''))
                else:
                    inner_payloads[k] = source
                    changed += 1
                    bilan.append((nom_conteneur, nom, ps_nom, 'INJECTE', ''))
            if travaux:
                print(f'[AFS RU] {len(travaux)} conversion(s) nécessaire(s), traitement parallèle...', flush=True)
                resultats = LSL_MCL_Audios_RU._convertir_lot(travaux)
                for k, source_index, nom, ps_nom, source_originale, original in travaux:
                    _, _, _, _, conversion, detail = resultats[k]
                    if conversion is None:
                        bilan.append((nom_conteneur, nom, ps_nom, 'CONVERSION_REFUSEE', detail))
                        continue
                    utilises.add((j, source_index))
                    if original == conversion:
                        bilan.append((nom_conteneur, nom, ps_nom, 'IDENTIQUE', detail))
                        continue
                    inner_payloads[k] = conversion
                    changed += 1
                    bilan.append((nom_conteneur, nom, ps_nom, 'CONVERTI_ET_INJECTE', detail))
            if changed:
                top_payloads[i] = A.construire_afs(pc_payload, inner_payloads)
                conteneurs += 1
                remplaces += changed
            print(f'[AFS RU] Banque {avance}/{banques} terminée : {changed} son(s) injecté(s).', flush=True)
        for j, payload in enumerate(ps['payloads']):
            if not payload.startswith(b'AFS\x00'):
                continue
            contenu = cache_ps2.get(j)
            if contenu is None:
                try:
                    contenu = A.lire_afs(payload)
                    cache_ps2[j] = contenu
                except ValueError:
                    continue
            for k, nom in enumerate(contenu['names']):
                if nom.lower().endswith(('.adx', '.ahx')) and (j, k) not in utilises:
                    bilan.append((ps['names'][j], '', nom, 'PS2_NON_INJECTE', ''))
        if remplaces:
            print(f'[AFS RU] Reconstruction finale : {remplaces} son(s) / {conteneurs} banque(s).', flush=True)
            pc_path.write_bytes(A.construire_afs(pc_raw, top_payloads))
        rapport = V.ROOT / 'RAPPORT_INJECTION_AFS.csv'
        with rapport.open('w', newline='', encoding='utf-8-sig') as fichier:
            sortie = csv.writer(fichier, delimiter=';')
            sortie.writerow(('conteneur', 'entree_pc', 'entree_ps2', 'etat', 'detail'))
            sortie.writerows(bilan)
        print('[AFS RU] Rapport :', rapport)
        print(f"[AFS RU] {remplaces} sons dans {conteneurs} banques ; {sum((r[3] == 'CONVERSION_REFUSEE' for r in bilan))} conversions refusées.")
        return remplaces
