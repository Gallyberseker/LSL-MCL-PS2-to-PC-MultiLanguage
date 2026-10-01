"""Localisation des banques audio PC à partir des ressources PS2."""
from pathlib import Path
import csv
import LSL_MCL_VARIABLES as V
import LSL_MCL_LANGUAGES
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES
from LSL_MCL_AFS import LSL_MCL_Afs
from LSL_MCL_AUDIO_CODECS import LSL_MCL_AudioCodecs
from LSL_MCL_AUDIO_AOS import LSL_MCL_AudioAos

class LSL_MCL_Audios(LSL_MCL_Afs, LSL_MCL_AudioCodecs, LSL_MCL_AudioAos):
    """Interface audio du moteur ; compose les traitements AFS, codecs et AOS."""

    @classmethod
    def localiser_afs_gameplay(cls, data_root, langue_cible='fr'):
        """Injecte les voix de la langue cible dans les banques gameplay PC et consigne les entrées pour la synchronisation AOS."""
        dossier_pc = data_root / 'Audio' / 'CRI'
        dossier_ps2 = V.PS2_VERSION / 'Data' / 'Audio' / 'CRI'
        pc_path = LSL_MCL_OUTILS.LSL_MCL_Outils.trouver_fichier_ci(dossier_pc, 'afs.afs')
        ps_path = LSL_MCL_LANGUAGES.LSL_MCL_Languages.trouver_fichier_langue(dossier_ps2, 'afs.afs', langue_cible)
        if pc_path is None or ps_path is None:
            print('[AFS] afs.afs absent.')
            return 0
        pc_raw = pc_path.read_bytes()
        ps_raw = ps_path.read_bytes()
        pc = cls.lire_afs(pc_raw)
        ps = cls.lire_afs(ps_raw)
        top_payloads = list(pc['payloads'])
        remplaces = 0
        conteneurs = 0
        bilan = []
        ps_utilises = set()
        for i, pc_payload in enumerate(pc['payloads']):
            if not pc_payload.startswith(b'AFS\x00'):
                continue
            nom_conteneur = pc['names'][i] if i < len(pc['names']) else ''
            j = cls.choisir_entree_audio_langue(ps['names'], nom_conteneur, langue_cible)
            if j is None:
                bilan.append((nom_conteneur, '', '', 'CONTENEUR_PC_SANS_CORRESPONDANCE', ''))
                continue
            ps_payload = ps['payloads'][j]
            if not ps_payload.startswith(b'AFS\x00'):
                bilan.append((nom_conteneur, '', '', 'CONTENEUR_PS2_NON_AFS', ''))
                continue
            try:
                pc_inner = cls.lire_afs(pc_payload)
                ps_inner = cls.lire_afs(ps_payload)
            except Exception as erreur:
                bilan.append((nom_conteneur, '', '', 'CONTENEUR_ILLISIBLE', str(erreur)))
                continue
            inner_payloads = list(pc_inner['payloads'])
            changed = 0
            for k, nom in enumerate(pc_inner['names']):
                nom_normalise = cls.nom_afs(nom)
                if not nom_normalise.endswith(('.adx', '.ahx')):
                    continue
                source_index = cls.choisir_entree_audio_langue(ps_inner['names'], nom, langue_cible)
                if source_index is None:
                    bilan.append((nom_conteneur, nom, '', 'SANS_CORRESPONDANCE', ''))
                    continue
                ps_nom = ps_inner['names'][source_index]
                source = ps_inner['payloads'][source_index]
                original = pc_inner['payloads'][k]
                pc_adx = cls.analyser_entete_adx(original)
                different = len(source) < 20 or len(original) < 20 or source[4] != original[4] or (source[7] != original[7]) or (source[8:12] != original[8:12]) or (source[4] not in (16, 17) and source[18] != original[18])
                detail = ''
                if nom_normalise.endswith(('.adx', '.ahx')) and pc_adx and different:
                    try:
                        conversion, detail = cls.convertir_audio_pour_pc(source, original, ps_nom)
                    except (OSError, ValueError, RuntimeError) as erreur:
                        conversion, detail = cls.refus_audio(f'Echec de la conversion : {erreur}', source, original)
                    if conversion is None:
                        bilan.append((nom_conteneur, nom, ps_nom, 'CONVERSION_REFUSEE', detail))
                        continue
                    source = conversion
                elif different:
                    bilan.append((nom_conteneur, nom, ps_nom, 'CODEC_OU_FORMAT_INCOMPATIBLE', cls.refus_audio('Conversion non definie pour cette entree', source, original)[1]))
                    continue
                if original == source:
                    bilan.append((nom_conteneur, nom, ps_nom, 'IDENTIQUE', detail))
                    ps_utilises.add((j, source_index))
                    continue
                inner_payloads[k] = source
                ps_utilises.add((j, source_index))
                bilan.append((nom_conteneur, nom, ps_nom, 'CONVERTI_ET_INJECTE' if detail else 'INJECTE', detail))
                changed += 1
            if changed:
                top_payloads[i] = cls.construire_afs(pc_payload, inner_payloads)
                conteneurs += 1
                remplaces += changed
        for j, payload in enumerate(ps['payloads']):
            if not payload.startswith(b'AFS\x00'):
                continue
            try:
                contenu = cls.lire_afs(payload)
            except ValueError:
                continue
            for k, nom in enumerate(contenu['names']):
                if nom.lower().endswith(('.adx', '.ahx')) and (j, k) not in ps_utilises:
                    bilan.append((ps['names'][j], '', nom, 'PS2_NON_INJECTE', ''))
        if remplaces:
            pc_path.write_bytes(cls.construire_afs(pc_raw, top_payloads))
        rapport = V.ROOT / 'RAPPORT_INJECTION_AFS.csv'
        with rapport.open('w', newline='', encoding='utf-8-sig') as fichier:
            sortie = csv.writer(fichier, delimiter=';')
            sortie.writerow(('conteneur', 'entree_pc', 'entree_ps2', 'etat', 'detail'))
            sortie.writerows(bilan)
        print('[AFS] Rapport :', rapport)
        print('[AFS] Audios convertis et injectes :', sum((r[3] == 'CONVERTI_ET_INJECTE' for r in bilan)))
        print('[AFS] Conversions refusees :', sum((r[3] == 'CONVERSION_REFUSEE' for r in bilan)))
        print('[AFS] Entrees PS2 non injectees :', sum((r[3] == 'PS2_NON_INJECTE' for r in bilan)))
        print('[AFS] Conteneurs ' + LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper() + ' :', conteneurs)
        print('[AFS] Sons ' + LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper() + ' :', remplaces)
        return remplaces

    @classmethod
    def localiser_adx_afs(cls, data_root, langue_cible='fr'):
        """Injecte les pistes PS2 compatibles ou converties, puis vérifie la banque AFS reconstruite."""
        dossier_pc = Path(data_root) / 'Audio' / 'CRI'
        dossier_ps2 = V.PS2_VERSION / 'Data' / 'Audio' / 'CRI'
        pc_path = LSL_MCL_OUTILS.LSL_MCL_Outils.trouver_fichier_ci(dossier_pc, 'adx.afs')
        ps_path = LSL_MCL_LANGUAGES.LSL_MCL_Languages.trouver_fichier_langue(dossier_ps2, 'adx.afs', langue_cible)
        if pc_path is None or ps_path is None:
            print('[ADX] adx.afs PC ou PS2 absent.')
            return 0
        pc_raw = pc_path.read_bytes()
        ps_raw = ps_path.read_bytes()
        pc = cls.lire_afs(pc_raw)
        ps = cls.lire_afs(ps_raw)
        nouveaux = list(pc['payloads'])
        changes = 0
        convertis = 0
        injectes_directs = 0
        refuses = 0
        for i, original in enumerate(pc['payloads']):
            nom_pc = pc['names'][i] if i < len(pc['names']) else ''
            source_index = None
            if nom_pc:
                source_index = cls.choisir_entree_audio_langue(ps['names'], nom_pc, langue_cible)
            if source_index is None and pc['count'] == ps['count']:
                source_index = i
            if source_index is None or source_index >= len(ps['payloads']):
                continue
            nom_ps2 = ps['names'][source_index] if source_index < len(ps['names']) else ''
            source = ps['payloads'][source_index]
            info_pc = cls.analyser_entete_adx(original)
            info_ps2 = cls.analyser_entete_adx(source)
            if not info_pc:
                continue
            if not info_ps2:
                continue
            cible_ahx = info_pc['encodage'] in (16, 17)
            champs = ['encodage', 'canaux', 'frequence_hz']
            if not cible_ahx:
                champs.append('version_adx')
            compatible = all((info_ps2.get(champ) == info_pc.get(champ) for champ in champs))
            detail = ''
            candidat = source
            if not compatible:
                try:
                    candidat, detail = cls.convertir_audio_pour_pc(source, original, nom_ps2 or nom_pc)
                except (OSError, ValueError, RuntimeError) as erreur:
                    candidat = None
                    detail = f'Echec conversion : {erreur}'
                if candidat is None:
                    refuses += 1
                    continue
                convertis += 1
                etat = 'CONVERTI_ET_INJECTE'
            else:
                injectes_directs += 1
                etat = 'INJECTE_COMPATIBLE'
            info_final = cls.analyser_entete_adx(candidat)
            if not info_final:
                refuses += 1
                continue
            if any((info_final.get(champ) != info_pc.get(champ) for champ in champs)):
                refuses += 1
                continue
            if info_final['nombre_echantillons'] <= 0:
                refuses += 1
                continue
            if candidat != original:
                nouveaux[i] = candidat
                changes += 1
            else:
                etat = 'IDENTIQUE'
        reconstruit = cls.construire_afs(pc_raw, nouveaux)
        controle = cls.lire_afs(reconstruit)
        if controle['count'] != pc['count']:
            raise RuntimeError(f"AFS reconstruit invalide : {controle['count']} entrées au lieu de {pc['count']}.")
        if len(controle['payloads']) != len(nouveaux):
            raise RuntimeError('AFS reconstruit : table de payloads incohérente.')
        for i, payload in enumerate(controle['payloads']):
            if nouveaux[i] != pc['payloads'][i]:
                if cls.analyser_entete_adx(payload) is None:
                    raise RuntimeError(f"Validation finale échouée à l'entrée AFS #{i}.")
        if changes:
            pc_path.write_bytes(reconstruit)
        langue = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper()
        print('[ADX] Langue :', langue)
        print('[ADX] Entrées PC :', pc['count'])
        print('[ADX] Modifiées :', changes)
        print('[ADX] Injectées déjà compatibles :', injectes_directs)
        print('[ADX] Converties au format PC :', convertis)
        print('[ADX] Refusées / PC conservé :', refuses)
        return changes
