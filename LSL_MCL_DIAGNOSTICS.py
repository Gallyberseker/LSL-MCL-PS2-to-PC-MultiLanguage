"""Diagnostics Larry MCL : LSL_MCL_DIAGNOSTICS."""
from pathlib import Path
import LSL_MCL_VARIABLES as V
import LSL_MCL_MENU
from LSL_MCL_DIAGNOSTIC_FICHIERS import DiagnosticFichiers
from LSL_MCL_DIAGNOSTIC_JAM import DiagnosticJam
from LSL_MCL_DIAGNOSTIC_RESSOURCES import DiagnosticRessources
from LSL_MCL_JOURNAL_DIAGNOSTIC import JournalDiagnostic

class LSL_MCL_Diagnostics(DiagnosticFichiers, DiagnosticJam, DiagnosticRessources):
    """Traitements composés par LSL_MCL_Diagnostics."""
    JournalDiagnostic = JournalDiagnostic

    @classmethod
    def diagnostiquer_textes_jam(cls, data_root):
        """Analyse les textes JAM et produit les informations de diagnostic nécessaires au contrôle de localisation."""
        LSL_MCL_MENU.LSL_MCL_Menu.titre('DIAGNOSTIQUE TOTAL TEXTE')
        contexte = cls.preparer_diagnostic_complet(None, 'Diagnostique_total_Texte')
        if contexte.get('pc_backup') is None or not contexte['pc_backup'].exists() or contexte.get('ps2') is None or (not contexte['ps2'].exists()):
            print('[TEXTES JAM] Backup PC ou source PS2_VERSION absent.')
            return False
        journal = contexte['journal']
        contexte['textes_backup_ps2_uniquement'] = True
        journal.ecrire('environnement', 'Mode textes rapide : PC_VERSION_BACKUP <-> PS2_VERSION uniquement.')
        try:
            journal.entete('textes', 'INDEXATION DÉTAILLÉE DES TEXTES JAM')
            resultat = cls.diagnostiquer_cles_textes_pc_ps2(contexte)
            print()
            print('[TEXTES JAM] Entrées PC :', len(resultat['pc']))
            print('[TEXTES JAM] Entrées PS2_VERSION :', len(resultat['ps2']))
            print('[TEXTES JAM] Correspondances :', len(resultat['correspondances']))
            print('[TEXTES JAM] Absentes sur PS2_VERSION :', len(resultat['absents_ps2']))
            print('[TEXTES JAM] Variables incompatibles :', len(resultat['variables_incompatibles']))
            print('[TEXTES JAM] Rapports :', contexte['rapport'])
            return True
        except Exception as erreur:
            journal.erreur('textes', f'Échec du diagnostic des textes : {erreur}')
            raise
        finally:
            journal.terminer()

    @classmethod
    def diagnostiquer_jeu_complet(cls, game_root):
        """Analyse les sources disponibles, leurs JAM, textes et ressources PS2."""
        import json
        LSL_MCL_MENU.LSL_MCL_Menu.titre('DIAGNOSTIQUE TOTAL COMPLET')
        contexte = cls.preparer_diagnostic_complet(game_root)
        journal = contexte['journal']
        try:
            journal.entete('execution', 'ANALYSE DES SOURCES PC ET PS2_VERSION')
            sources = (('PC_VERSION', contexte['pc_version'], contexte['rapport_pc'], '02_INVENTAIRE_PC.json', 'pc'), ('PC_VERSION_BACKUP', contexte['pc_backup'], contexte['rapport_backup'], '02_INVENTAIRE_PC_VERSION_BACKUP.json', 'pc'), ('PS2_VERSION', contexte['ps2'], contexte['rapport_ps2'], '03_INVENTAIRE_PS2.json', 'ps2'))
            for nom, racine, destination, fichier_rapport, section in sources:
                if racine is None or not racine.exists():
                    journal.attention(section, f'{nom} absent.')
                    continue
                journal.ecrire(section, f'Inventaire de {nom} : {racine}')
                inventaire = cls.inventorier_source_complete(nom, racine)
                (destination / fichier_rapport).write_text(json.dumps(inventaire, ensure_ascii=False, indent=2), encoding='utf-8')
                journal.ecrire(section, f"{nom} : {inventaire['nombre_fichiers']} fichiers")
            journal.entete('jam', 'ANALYSE INTERNE DES JAM')
            cls.diagnostiquer_jam_pc_ps2(contexte)
            journal.entete('textes', 'INDEXATION COMPLÈTE DES TEXTES')
            cls.diagnostiquer_cles_textes_pc_ps2(contexte)
            journal.entete('ps2', 'CARTOGRAPHIE DE LOCALISATION PS2_VERSION')
            cls.diagnostiquer_localisation_ps2(contexte)
            journal.ecrire('execution', 'Diagnostic terminé avec succès.')
            print()
            print('[DIAGNOSTIC] Rapports :')
            print(contexte['rapport'])
        except Exception as erreur:
            journal.erreur('execution', f'Échec du diagnostic : {erreur}')
            raise
        finally:
            journal.terminer()

    @classmethod
    def preparer_contexte_diagnostic_cible(cls, data_root, nom_dossier):
        """Construit le contexte de diagnostic pour un dossier Data cible déterminé."""
        data_root = Path(data_root) if data_root is not None else None
        if data_root is None or not data_root.exists() or (not data_root.is_dir()):
            return None
        game_root = data_root.parent if data_root.name.lower() == 'data' else data_root
        contexte = cls.preparer_diagnostic_complet(game_root, nom_dossier)
        contexte['pc_version'] = data_root
        contexte['sources_presentes']['pc_version'] = True
        try:
            chemin_cible = data_root.resolve()
        except Exception:
            chemin_cible = data_root
        correspondances_cibles = ((V.PC_VERSION_EDIT_FINI / 'Data', 'PC_FINAL'), (V.PC_VERSION_EDIT_TEMPS / 'Data', 'PC_TEMP'), (V.PC_VERSION_BACKUP / 'Data', 'PC_VERSION_BACKUP_SOURCE'))
        nom_version_cible = 'PC_VERSION'
        for chemin_connu, nom_connu in correspondances_cibles:
            try:
                meme_chemin = chemin_connu.resolve() == chemin_cible
            except Exception:
                meme_chemin = chemin_connu == chemin_cible
            if meme_chemin:
                nom_version_cible = nom_connu
                break
        contexte['nom_version_cible'] = nom_version_cible
        contexte['journal'].ecrire('environnement', f'Source PC analysée : {nom_version_cible} -> {data_root}')
        return contexte

    @classmethod
    def preparer_diagnostic_complet(cls, game_root, nom_dossier='Diagnostique_total_Complet'):
        """Prépare les sources, index et répertoires nécessaires au diagnostic complet."""
        dossier = V.RAPPORTS / nom_dossier
        pc_dossier = dossier / 'PC_VERSION'
        backup_dossier = dossier / 'PC_VERSION_BACKUP'
        ps2_dossier = dossier / 'PS2_VERSION'
        comparaison_dossier = dossier / 'COMPARAISON'
        for chemin in (dossier, pc_dossier, backup_dossier, ps2_dossier, comparaison_dossier):
            chemin.mkdir(parents=True, exist_ok=True)
        pc_version_data = None
        if game_root is not None:
            try:
                racine_version = Path(game_root)
                candidat = racine_version / 'Data'
                if candidat.exists():
                    pc_version_data = candidat
                else:
                    print('[DIAGNOSTIC] Data PC absent :', candidat)
            except Exception as erreur:
                print('[DIAGNOSTIC] Chemin PC invalide :', erreur)
        pc_backup_data = V.PC_VERSION_BACKUP / 'Data'
        ps2_data = V.PS2_VERSION / 'Data'
        temp_data = V.PC_VERSION_EDIT_TEMPS / 'Data'
        final_data = V.PC_VERSION_EDIT_FINI / 'Data'
        sources_presentes = {'pc_version': pc_version_data is not None and pc_version_data.exists() and pc_version_data.is_dir(), 'pc_backup': pc_backup_data.exists() and pc_backup_data.is_dir(), 'ps2': ps2_data.exists() and ps2_data.is_dir(), 'temp': temp_data.exists() and temp_data.is_dir(), 'final': final_data.exists() and final_data.is_dir(), 'images_extraites': V.IMAGE_EXTRACT.exists() and V.IMAGE_EXTRACT.is_dir(), 'images_injection': V.IMAGE_INJECT.exists() and V.IMAGE_INJECT.is_dir(), 'manifeste_images': V.MANIFEST.exists() and V.MANIFEST.is_file(), 'images_inconnues': V.UNKNOWN_IMAGES.exists() and V.UNKNOWN_IMAGES.is_file()}
        contexte = {'rapport': dossier, 'rapport_pc': pc_dossier, 'rapport_backup': backup_dossier, 'rapport_ps2': ps2_dossier, 'rapport_comparaison': comparaison_dossier, 'pc_version': pc_version_data, 'pc_backup': pc_backup_data, 'ps2': ps2_data, 'temp': temp_data, 'final': final_data, 'images_extraites': V.IMAGE_EXTRACT, 'images_injection': V.IMAGE_INJECT, 'manifeste_images': V.MANIFEST, 'images_inconnues': V.UNKNOWN_IMAGES, 'sources_presentes': sources_presentes}
        journal = cls.JournalDiagnostic(dossier)
        contexte['journal'] = journal
        journal.entete('environnement', 'ÉTAT DES SOURCES')
        chemins = {'pc_version': pc_version_data, 'pc_backup': pc_backup_data, 'ps2': ps2_data, 'temp': temp_data, 'final': final_data, 'images_extraites': V.IMAGE_EXTRACT, 'images_injection': V.IMAGE_INJECT, 'manifeste_images': V.MANIFEST, 'images_inconnues': V.UNKNOWN_IMAGES}
        for nom, chemin in chemins.items():
            present = sources_presentes[nom]
            etat = 'PRÉSENT' if present else 'ABSENT'
            chemin_affiche = str(chemin) if chemin is not None else 'Non détecté'
            journal.ecrire('environnement', f'{nom} : {etat}')
            journal.ecrire('environnement', f'{nom} chemin : {chemin_affiche}')
        if not sources_presentes['pc_version']:
            journal.attention('environnement', 'Jeu PC non détecté.')
        if not sources_presentes['pc_backup']:
            journal.attention('environnement', 'Backup PC absent.')
        if not sources_presentes['ps2']:
            journal.attention('environnement', 'Source PS2_VERSION absente.')
        if not sources_presentes['pc_version'] and (not sources_presentes['pc_backup']) and (not sources_presentes['ps2']):
            journal.erreur('environnement', 'Aucune source PC ou PS2_VERSION disponible pour le diagnostic.')
        print()
        print('[DIAGNOSTIC] État des sources :')
        for nom, present in sources_presentes.items():
            print(' -', nom, ':', 'PRÉSENT' if present else 'ABSENT')
        return contexte
