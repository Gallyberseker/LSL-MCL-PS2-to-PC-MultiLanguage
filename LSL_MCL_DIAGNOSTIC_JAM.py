"""Diagnostics Larry MCL : LSL_MCL_DIAGNOSTIC_JAM."""
from pathlib import Path
import LSL_MCL_VARIABLES as V
import LSL_MCL_ANALISES
import LSL_MCL_EXTRACTIONS
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES

class DiagnosticJam:
    """Traitements composés par LSL_MCL_Diagnostics."""

    @classmethod
    def diagnostiquer_jam_pc_ps2(cls, contexte):
        """Diagnostique jam PC PS2_VERSION."""
        import json
        import re
        journal = contexte['journal']
        nom_version_cible = contexte.get('nom_version_cible', 'PC_VERSION')
        sources = ((nom_version_cible, contexte.get('pc_version'), contexte['rapport_pc']), ('PC_VERSION_BACKUP', contexte.get('pc_backup'), contexte.get('rapport_backup', contexte['rapport_pc'])), ('PS2_VERSION', contexte.get('ps2'), contexte['rapport_ps2']))
        resume_global = {'fichiers_jam': 0, 'chaines': 0, 'styles': 0, 'rectangles': 0, 'liaisons': 0, 'livre_noir': 0, 'erreurs': 0, 'plateformes': {}}
        for plateforme, racine, destination in sources:
            resume_plateforme = {'plateforme': plateforme, 'source': str(racine) if racine is not None else None, 'fichiers_jam': 0, 'chaines': 0, 'styles': 0, 'rectangles': 0, 'liaisons': 0, 'livre_noir': 0, 'erreurs': [], 'rapports': []}
            resume_global['plateformes'][plateforme] = resume_plateforme
            if racine is None or not racine.exists():
                journal.attention('jam', f'{plateforme} absent.')
                continue
            dossier_jam = destination / 'JAM_DETAILS' / plateforme
            dossier_jam.mkdir(parents=True, exist_ok=True)
            fichiers = sorted((fichier for fichier in racine.rglob('*') if fichier.is_file() and fichier.suffix.lower() == '.jam'))
            journal.entete('jam', f'ANALYSE JAM {plateforme}')
            journal.ecrire('jam', f'Fichiers JAM : {len(fichiers)}')
            for numero, fichier in enumerate(fichiers, start=1):
                relatif = fichier.relative_to(racine)
                journal.ecrire('jam', f'[{numero}/{len(fichiers)}] {relatif}')
                try:
                    analyse = LSL_MCL_ANALISES.LSL_MCL_Analises.analyser_jam_detaille(fichier, racine, plateforme)
                    dossier_relatif = dossier_jam / relatif.parent
                    dossier_relatif.mkdir(parents=True, exist_ok=True)
                    rapport_jam = dossier_relatif / (relatif.name + '.json')
                    rapport_jam.write_text(json.dumps(analyse, ensure_ascii=False, indent=2), encoding='utf-8')
                    nombre_chaines = len(analyse['chaines'])
                    nombre_styles = len(analyse['styles'])
                    nombre_rectangles = len(analyse['rectangles'])
                    nombre_liaisons = len(analyse['liaisons'])
                    nombre_livre = len(analyse['livre_noir'])
                    resume_plateforme['fichiers_jam'] += 1
                    resume_plateforme['chaines'] += nombre_chaines
                    resume_plateforme['styles'] += nombre_styles
                    resume_plateforme['rectangles'] += nombre_rectangles
                    resume_plateforme['liaisons'] += nombre_liaisons
                    resume_plateforme['livre_noir'] += nombre_livre
                    resume_plateforme['rapports'].append({'fichier': analyse['fichier'], 'rapport': str(rapport_jam.relative_to(contexte['rapport'])).replace('\\', '/'), 'taille': analyse['taille'], 'sha256': analyse['sha256'], 'chunks': len(analyse['chunks']), 'chaines': nombre_chaines, 'styles': nombre_styles, 'rectangles': nombre_rectangles, 'liaisons': nombre_liaisons, 'livre_noir': nombre_livre, 'erreurs': analyse['erreurs']})
                    resume_global['fichiers_jam'] += 1
                    resume_global['chaines'] += nombre_chaines
                    resume_global['styles'] += nombre_styles
                    resume_global['rectangles'] += nombre_rectangles
                    resume_global['liaisons'] += nombre_liaisons
                    resume_global['livre_noir'] += nombre_livre
                except Exception as erreur:
                    message = f'{relatif} : {erreur}'
                    resume_plateforme['erreurs'].append(message)
                    resume_global['erreurs'] += 1
                    journal.erreur('jam', f'{plateforme} : {message}')
            fichier_resume = destination / f'JAM_RESUME_{plateforme}.json'
            fichier_resume.write_text(json.dumps(resume_plateforme, ensure_ascii=False, indent=2), encoding='utf-8')
        (contexte['rapport'] / '06_CARTE_BINAIRE_JAM_RESUME.json').write_text(json.dumps(resume_global, ensure_ascii=False, indent=2), encoding='utf-8')
        journal.ecrire('jam', f"JAM analysés : {resume_global['fichiers_jam']}")
        journal.ecrire('textes', f"Chaînes techniques : {resume_global['chaines']}")
        journal.ecrire('polices', f"Styles : {resume_global['styles']}")
        journal.ecrire('menus', f"Rectangles : {resume_global['rectangles']}")
        return resume_global

    @classmethod
    def diagnostiquer_cles_textes_pc_ps2(cls, contexte):
        """Diagnostique cles textes PC PS2_VERSION."""
        import json
        journal = contexte['journal']
        journal.entete('textes', 'CLÉS ET TEXTES PC / PS2_VERSION')
        textes_backup_ps2 = contexte.get('textes_backup_ps2_uniquement', False)
        nom_version_cible = contexte.get('nom_version_cible', 'PC_VERSION')
        source_backup = ('PC_VERSION_BACKUP', contexte.get('pc_backup'), contexte.get('rapport_backup', contexte['rapport_pc']))
        source_ps2 = ('PS2_VERSION', contexte.get('ps2'), contexte['rapport_ps2'])
        if textes_backup_ps2:
            sources = (source_backup, source_ps2)
        else:
            sources = ((nom_version_cible, contexte.get('pc_version'), contexte['rapport_pc']), source_backup, source_ps2)
        entrees_par_source = {}
        for plateforme, racine, destination in sources:
            entrees = []
            if racine is None or not racine.exists():
                journal.attention('textes', f'{plateforme} absent.')
                entrees_par_source[plateforme] = entrees
                continue
            fichiers_jam = sorted((fichier for fichier in racine.rglob('*') if fichier.is_file() and fichier.suffix.lower() == '.jam'))
            journal.ecrire('textes', f'{plateforme} : {len(fichiers_jam)} JAM')
            for numero, fichier in enumerate(fichiers_jam, start=1):
                try:
                    nouvelles = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.extraire_entrees_textes_jam(fichier, racine, plateforme)
                    entrees.extend(nouvelles)
                    relatif = fichier.relative_to(racine)
                    sortie_jam = destination / 'TEXTES_CLES' / relatif.parent / (relatif.name + '.textes.json')
                    sortie_jam.parent.mkdir(parents=True, exist_ok=True)
                    sortie_jam.write_text(json.dumps({'plateforme': plateforme, 'fichier': str(relatif).replace('\\', '/'), 'nombre_entrees': len(nouvelles), 'entrees': nouvelles}, ensure_ascii=False, indent=2), encoding='utf-8')
                    journal.ecrire('textes', f'[{plateforme}] [{numero}/{len(fichiers_jam)}] {fichier.relative_to(racine)} : {len(nouvelles)} entrées')
                except Exception as erreur:
                    journal.erreur('textes', f'{plateforme} {fichier} : {erreur}')
            entrees_par_source[plateforme] = entrees
            journal.ecrire('textes', f'{plateforme} : {len(entrees)} entrées texte')
        pc = entrees_par_source.get('PC_VERSION_BACKUP' if textes_backup_ps2 else nom_version_cible, [])
        if not pc:
            pc = entrees_par_source.get('PC_VERSION_BACKUP', [])
        ps2 = entrees_par_source.get('PS2_VERSION', [])
        index_ps2 = {}
        for entree in ps2:
            identifiant = (entree['fichier_normalise'], entree['namespace'], entree['cle'])
            index_ps2.setdefault(identifiant, []).append(entree)
        for candidats in index_ps2.values():
            candidats.sort(key=lambda entree: (entree.get('langue_bloc') == LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(V.LANGUE_CIBLE), entree.get('scores_langues', {}).get(LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(V.LANGUE_CIBLE), 0), -entree.get('numero_bloc_texte', 0)), reverse=True)
        correspondances = []
        absents_ps2 = []
        variables_incompatibles = []
        for entree_pc in pc:
            identifiant = (entree_pc['fichier_normalise'], entree_pc['namespace'], entree_pc['cle'])
            candidats = index_ps2.get(identifiant, [])
            if not candidats:
                absents_ps2.append(entree_pc)
                continue
            langue_demandee = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(V.LANGUE_CIBLE)
            candidats_langue = [candidat for candidat in candidats if candidat.get('langue_bloc') == langue_demandee]
            entree_ps2 = candidats_langue[0] if candidats_langue else candidats[0]
            valeurs_par_langue = {}
            for candidat in candidats:
                langue = candidat.get('langue_bloc', 'inconnue')
                valeurs_par_langue.setdefault(langue, []).append({'valeur': candidat['valeur'], 'variables': candidat['variables'], 'longueur_octets': candidat['longueur_octets'], 'numero_bloc_texte': candidat['numero_bloc_texte'], 'chunk_index': candidat['chunk_index'], 'offset_valeur': candidat['offset_valeur'], 'offset_valeur_hex': candidat['offset_valeur_hex']})
            variables_pc = sorted(entree_pc['variables'])
            variables_ps2 = sorted(entree_ps2['variables'])
            compatible = variables_pc == variables_ps2
            comparaison = {'identifiant': entree_pc['identifiant'], 'fichier_pc': entree_pc['fichier'], 'fichier_ps2': entree_ps2['fichier'], 'namespace': entree_pc['namespace'], 'cle': entree_pc['cle'], 'valeur_pc': entree_pc['valeur'], 'valeur_ps2': entree_ps2['valeur'], 'langue_ps2_selectionnee': entree_ps2.get('langue_bloc', 'inconnue'), 'valeurs_ps2_par_langue': valeurs_par_langue, 'score_francais_bloc_ps2': entree_ps2.get('score_francais_bloc', 0), 'nombre_candidats_ps2': len(candidats), 'offset_pc': entree_pc['offset_valeur'], 'offset_pc_hex': entree_pc['offset_valeur_hex'], 'offset_ps2': entree_ps2['offset_valeur'], 'offset_ps2_hex': entree_ps2['offset_valeur_hex'], 'variables_pc': variables_pc, 'variables_ps2': variables_ps2, 'variables_compatibles': compatible, 'longueur_pc': entree_pc['longueur_octets'], 'longueur_ps2': entree_ps2['longueur_octets'], 'difference_longueur': entree_ps2['longueur_octets'] - entree_pc['longueur_octets'], 'traduction_directe_possible': compatible}
            correspondances.append(comparaison)
            if not compatible:
                variables_incompatibles.append(comparaison)
        dossier_correspondances = contexte['rapport_comparaison'] / 'TEXTES_PAR_JAM'
        groupes = {}
        for comparaison in correspondances:
            groupes.setdefault(comparaison['fichier_pc'], {'correspondances': [], 'absents_ps2': [], 'variables_incompatibles': []})['correspondances'].append(comparaison)
        for entree in absents_ps2:
            groupes.setdefault(entree['fichier'], {'correspondances': [], 'absents_ps2': [], 'variables_incompatibles': []})['absents_ps2'].append(entree)
        for comparaison in variables_incompatibles:
            groupes.setdefault(comparaison['fichier_pc'], {'correspondances': [], 'absents_ps2': [], 'variables_incompatibles': []})['variables_incompatibles'].append(comparaison)
        index_rapports = []
        for fichier_pc, contenu in sorted(groupes.items()):
            chemin_normalise = LSL_MCL_OUTILS.LSL_MCL_Outils.normaliser_chemin_jam(fichier_pc)
            relatif = Path(chemin_normalise)
            sortie = dossier_correspondances / relatif.parent / (relatif.name + '.correspondances.json')
            sortie.parent.mkdir(parents=True, exist_ok=True)
            document = {'fichier_pc': fichier_pc, 'fichier_normalise': chemin_normalise, 'langue_cible_courante': LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(V.LANGUE_CIBLE), 'nombre_correspondances': len(contenu['correspondances']), 'nombre_absents_ps2': len(contenu['absents_ps2']), 'nombre_variables_incompatibles': len(contenu['variables_incompatibles']), **contenu}
            sortie.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding='utf-8')
            index_rapports.append({'fichier_pc': fichier_pc, 'rapport': str(sortie.relative_to(contexte['rapport'])).replace('\\', '/'), 'correspondances': len(contenu['correspondances']), 'absents_ps2': len(contenu['absents_ps2']), 'variables_incompatibles': len(contenu['variables_incompatibles'])})
        (contexte['rapport_comparaison'] / '07_INDEX_CORRESPONDANCES_TEXTES.json').write_text(json.dumps({'langue_cible_courante': LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(V.LANGUE_CIBLE), 'nombre_fichiers': len(index_rapports), 'nombre_correspondances': len(correspondances), 'nombre_absents_ps2': len(absents_ps2), 'nombre_variables_incompatibles': len(variables_incompatibles), 'rapports': index_rapports}, ensure_ascii=False, indent=2), encoding='utf-8')
        journal.ecrire('comparaison', f'Correspondances texte : {len(correspondances)}')
        journal.ecrire('comparaison', f'Textes PC absents sur PS2_VERSION : {len(absents_ps2)}')
        journal.ecrire('comparaison', f'Variables incompatibles : {len(variables_incompatibles)}')
        return {'pc': pc, 'ps2': ps2, 'correspondances': correspondances, 'absents_ps2': absents_ps2, 'variables_incompatibles': variables_incompatibles}
