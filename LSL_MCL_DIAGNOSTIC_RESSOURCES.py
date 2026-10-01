"""Diagnostics Larry MCL : LSL_MCL_DIAGNOSTIC_RESSOURCES."""
from pathlib import Path
from PIL import Image
import re
import hashlib
import LSL_MCL_VARIABLES as V
from LSL_MCL_IMAGE_DETECTION import obtenir_detecteurs
import LSL_MCL_ANALISES
import LSL_MCL_AUDIOS
import LSL_MCL_MENU
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES

class DiagnosticRessources:
    """Traitements composés par LSL_MCL_Diagnostics."""

    @classmethod
    def diagnostiquer_menus_interfaces(cls, data_root):
        """Analyse les menus de la source Data et écrit les rapports associés."""
        import json
        LSL_MCL_MENU.LSL_MCL_Menu.titre('DIAGNOSTIQUE TOTAL MENU')
        contexte = cls.preparer_contexte_diagnostic_cible(data_root, 'Diagnostique_total_menu')
        if contexte is None:
            print('[MENUS] Source Data absente ou invalide.')
            return False
        journal = contexte['journal']
        try:
            journal.entete('menus', 'STYLES, RECTANGLES, COMMANDES ET LIVRE NOIR')
            resume = cls.diagnostiquer_jam_pc_ps2(contexte)
            resume_menus = {'source_analysee': str(Path(data_root).resolve()), 'fichiers_jam': resume['fichiers_jam'], 'chaines': resume['chaines'], 'styles': resume['styles'], 'rectangles': resume['rectangles'], 'liaisons': resume['liaisons'], 'livre_noir': resume['livre_noir'], 'erreurs': resume['erreurs'], 'details_par_plateforme': resume['plateformes']}
            fichier_resume = contexte['rapport'] / '09_MENUS_INTERFACES_RESUME.json'
            fichier_resume.write_text(json.dumps(resume_menus, ensure_ascii=False, indent=2), encoding='utf-8')
            journal.ecrire('menus', f'Résumé menus : {fichier_resume}')
            print()
            print('[MENUS] JAM analysés :', resume['fichiers_jam'])
            print('[MENUS] Styles :', resume['styles'])
            print('[MENUS] Rectangles :', resume['rectangles'])
            print('[MENUS] Liaisons :', resume['liaisons'])
            print('[MENUS] Éléments Livre noir :', resume['livre_noir'])
            print('[MENUS] Rapport :', fichier_resume)
            return True
        except Exception as erreur:
            journal.erreur('menus', f'Échec du diagnostic des menus : {erreur}')
            raise
        finally:
            journal.terminer()

    @classmethod
    def diagnostiquer_localisation_ps2(cls, contexte):
        """Diagnostique localisation PS2_VERSION."""
        import json
        journal = contexte['journal']
        data_ps2 = contexte.get('ps2')
        if data_ps2 is None or not data_ps2.exists():
            journal.attention('ps2', 'Diagnostic localisation PS2_VERSION ignoré : source absente.')
            return None
        dossier = contexte['rapport_ps2'] / 'LOCALISATION_PS2'
        dossier.mkdir(parents=True, exist_ok=True)
        ini = next((fichier for fichier in data_ps2.parent.rglob('*') if fichier.is_file() and fichier.name.lower() == 'larry.ini'), None)
        system_cnf = next((fichier for fichier in data_ps2.parent.rglob('*') if fichier.is_file() and fichier.name.lower() == 'system.cnf'), None)
        texte_ini = ini.read_text(encoding='cp1252', errors='replace') if ini is not None else ''
        correspondance_langues = {'ENGLISH': 'en', 'BRITISH': 'en', 'FRENCH': 'fr', 'GERMAN': 'de', 'SPANISH': 'es', 'ITALIAN': 'it'}
        match_langue = re.search('^\\s*Language\\s+"([^"]+)"', texte_ini, re.I | re.M)
        valeur_ini = match_langue.group(1).upper() if match_langue else None
        langue_active = correspondance_langues.get(valeur_ini, 'inconnue')
        texte_systeme = system_cnf.read_text(encoding='ascii', errors='replace') if system_cnf is not None else ''
        match_executable = re.search('BOOT2\\s*=\\s*cdrom0:\\\\([^;\\r\\n]+)', texte_systeme, re.I)
        executable = match_executable.group(1) if match_executable else None
        editions = {'SLUS_209.56': 'ru', 'SLUS_209.56': 'ru', 'SLES_526.41': 'en', 'SLES_526.42': 'fr', 'SLES_526.43': 'de', 'SLES_526.44': 'es', 'SLES_526.45': 'it'}
        profil = {'racine_ps2': str(data_ps2.parent.resolve()), 'dossier_data': str(data_ps2.resolve()), 'larry_ini': str(ini.resolve()) if ini else None, 'directive': 'Language', 'valeur_ini': valeur_ini, 'langue_active': langue_active, 'system_cnf': str(system_cnf.resolve()) if system_cnf else None, 'executable': executable, 'langue_edition': editions.get(executable, 'inconnue'), 'coherence_ini_executable': langue_active == editions.get(executable) if executable in editions else None, 'valeurs_acceptees': correspondance_langues, 'editions_connues': editions}
        (dossier / '00_PROFIL_SOURCE_PS2.json').write_text(json.dumps(profil, ensure_ascii=False, indent=2), encoding='utf-8')
        banques_jam = []
        fichiers_jam = sorted((fichier for fichier in data_ps2.rglob('*') if fichier.is_file() and fichier.suffix.lower() == '.jam'))
        for fichier in fichiers_jam:
            data = fichier.read_bytes()
            blocs = []
            for numero_bloc, bloc in enumerate(LSL_MCL_TEXTES.LSL_MCL_Textes.blocs_texte(data)):
                langue, scores = LSL_MCL_ANALISES.LSL_MCL_Analises.identifier_langue_bloc_texte(bloc['payload'])
                nombre_entrees = sum((1 for _ in V.ENTRY.finditer(bloc['payload'])))
                blocs.append({'numero_bloc_texte': numero_bloc, 'chunk_index': bloc['chunk_index'], 'namespace': bloc['namespace'], 'langue_detectee': langue, 'scores_langues': scores, 'nombre_entrees': nombre_entrees, 'offset_debut': bloc['begin'], 'offset_debut_hex': f"0x{bloc['begin']:X}", 'offset_fin': bloc['end'], 'offset_fin_hex': f"0x{bloc['end']:X}", 'taille_bloc': bloc['end'] - bloc['begin']})
            relatif = str(fichier.relative_to(data_ps2)).replace('\\', '/')
            banques_jam.append({'fichier': relatif, 'adresse': str(fichier.resolve()), 'taille': len(data), 'sha256': cls.empreinte_sha256(fichier, data=data), 'nombre_blocs_texte': len(blocs), 'langues_detectees': sorted({bloc['langue_detectee'] for bloc in blocs}), 'blocs': blocs, 'rapport_cles_detaille': 'PS2_VERSION/TEXTES_CLES/' + relatif + '.textes.json', 'methode_recuperation': 'fichier_normalise + namespace + cle + langue_detectee'})
        (dossier / '01_BANQUES_TEXTES_JAM.json').write_text(json.dumps(banques_jam, ensure_ascii=False, indent=2), encoding='utf-8')
        archives_audio = []

        def parcourir_afs(data, chemin, base_absolue=0, profondeur=0):
            """
            Parcourt afs.
        
            Paramètres:
                data, chemin, base_absolue, profondeur.
        
            Connexions:
                Appelée par : diagnostiquer_localisation_ps2.
                Appelle : analyser_entete_adx, lire_afs, sha256.
            """
            if profondeur > 8:
                return []
            info = LSL_MCL_AUDIOS.LSL_MCL_Audios.lire_afs(data)
            elements = []
            for index, ((offset, taille), payload) in enumerate(zip(info['entries'], info['payloads'])):
                nom = info['names'][index] if index < len(info['names']) and info['names'][index] else f'entree_{index:05d}'
                chemin_interne = f'{chemin}/{nom}'
                type_ressource = 'binaire'
                if payload.startswith(b'AFS\x00'):
                    type_ressource = 'archive_afs'
                elif LSL_MCL_AUDIOS.LSL_MCL_Audios.analyser_entete_adx(payload) is not None:
                    type_ressource = 'audio_adx'
                element = {'index': index, 'nom': nom, 'chemin_interne': chemin_interne, 'type': type_ressource, 'offset_conteneur': offset, 'offset_conteneur_hex': f'0x{offset:X}', 'offset_absolu': base_absolue + offset, 'offset_absolu_hex': f'0x{base_absolue + offset:X}', 'taille': taille, 'sha256': hashlib.sha256(payload).hexdigest(), 'langue_presumee': langue_active, 'adx': LSL_MCL_AUDIOS.LSL_MCL_Audios.analyser_entete_adx(payload)}
                elements.append(element)
                if type_ressource == 'archive_afs':
                    elements.extend(parcourir_afs(payload, chemin_interne, base_absolue + offset, profondeur + 1))
            return elements
        fichiers_afs = sorted((fichier for fichier in data_ps2.rglob('*') if fichier.is_file() and fichier.suffix.lower() == '.afs'))
        for fichier in fichiers_afs:
            try:
                data = fichier.read_bytes()
                info = LSL_MCL_AUDIOS.LSL_MCL_Audios.lire_afs(data)
                relatif = str(fichier.relative_to(data_ps2)).replace('\\', '/')
                archives_audio.append({'fichier': relatif, 'adresse': str(fichier.resolve()), 'taille': len(data), 'sha256': cls.empreinte_sha256(fichier, data=data), 'nombre_entrees_racine': info['count'], 'alignement': info['alignment'], 'table_noms_offset': info['table_offset'], 'table_noms_taille': info['table_size'], 'entrees': parcourir_afs(data, relatif), 'methode_extraction': 'lire_afs puis extraction offset/taille', 'methode_reconstruction': 'construire_afs en conservant ordre, noms et alignement'})
            except Exception as erreur:
                archives_audio.append({'fichier': str(fichier.relative_to(data_ps2)).replace('\\', '/'), 'erreur': str(erreur)})
        (dossier / '02_ARCHIVES_AFS_ADX.json').write_text(json.dumps(archives_audio, ensure_ascii=False, indent=2), encoding='utf-8')
        cinemas = []
        ffprobe = LSL_MCL_OUTILS.LSL_MCL_Outils.outil('ffprobe.exe') or LSL_MCL_OUTILS.LSL_MCL_Outils.outil('ffprobe')
        fichiers_sfd = sorted((fichier for fichier in data_ps2.rglob('*') if fichier.is_file() and fichier.suffix.lower() == '.sfd'))
        for fichier in fichiers_sfd:
            data = fichier.read_bytes()
            zones = LSL_MCL_AUDIOS.LSL_MCL_Audios.trouver_paquets_audio_sfd(data)
            flux = []
            erreur_ffprobe = None
            if ffprobe:
                rc, sortie, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande([ffprobe, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(fichier)])
                if rc == 0:
                    try:
                        flux = json.loads(sortie)
                    except Exception:
                        erreur_ffprobe = 'JSON ffprobe invalide'
                else:
                    erreur_ffprobe = erreur
            cinemas.append({'fichier': str(fichier.relative_to(data_ps2)).replace('\\', '/'), 'adresse': str(fichier.resolve()), 'taille': len(data), 'sha256': cls.empreinte_sha256(fichier, data=data), 'langue_audio_presumee': langue_active, 'nombre_zones_audio_pes': len(zones), 'capacite_audio_totale': sum((fin - debut for debut, fin in zones)), 'zones_audio': [{'index': index, 'offset_debut': debut, 'offset_debut_hex': f'0x{debut:X}', 'offset_fin': fin, 'offset_fin_hex': f'0x{fin:X}', 'taille': fin - debut} for index, (debut, fin) in enumerate(zones)], 'analyse_ffprobe': flux, 'erreur_ffprobe': erreur_ffprobe, 'methode_localisation': 'conserver vidéo/paquets PC et remplacer uniquement les charges audio'})
        (dossier / '03_CINEMATIQUES_SFD.json').write_text(json.dumps(cinemas, ensure_ascii=False, indent=2), encoding='utf-8')
        images = []
        extensions_images = {'.bmp', '.dds', '.png', '.jpg', '.jpeg', '.gif', '.ico'}
        for fichier in sorted(data_ps2.rglob('*')):
            if not fichier.is_file() or fichier.suffix.lower() not in extensions_images:
                continue
            try:
                with Image.open(fichier) as image:
                    largeur, hauteur = image.size
                    mode = image.mode
            except Exception:
                largeur = hauteur = None
                mode = None
            images.append({'fichier': str(fichier.relative_to(data_ps2)).replace('\\', '/'), 'adresse': str(fichier.resolve()), 'conteneur': None, 'offset': 0, 'offset_hex': '0x0', 'taille': fichier.stat().st_size, 'format': fichier.suffix.lower().lstrip('.').upper(), 'largeur': largeur, 'hauteur': hauteur, 'mode': mode, 'sha256': cls.empreinte_sha256(fichier), 'langue_presumee': langue_active, 'methode_extraction': 'copie directe', 'methode_injection': 'remplacement du fichier avec format identique'})
        for fichier in fichiers_jam:
            data = fichier.read_bytes()
            relatif = str(fichier.relative_to(data_ps2)).replace('\\', '/')
            numero_image = 0
            for signature, detecteur in obtenir_detecteurs().items():
                position = 0
                while True:
                    position = data.find(signature, position)
                    if position < 0:
                        break
                    information = detecteur(data, position)
                    if information:
                        images.append({'fichier': relatif, 'adresse': str(fichier.resolve()), 'conteneur': relatif, 'index': numero_image, 'offset': position, 'offset_hex': f'0x{position:X}', 'taille': information['taille'], 'format': information['format'], 'largeur': information.get('largeur'), 'hauteur': information.get('hauteur'), 'bpp': information.get('bpp'), 'compression': information.get('compression'), 'fourcc': information.get('fourcc'), 'mipmaps': information.get('mipmaps'), 'sha256': hashlib.sha256(data[position:position + information['taille']]).hexdigest(), 'nom_extraction': relatif.replace('/', '__') + f"__{information['format']}__{numero_image:04d}" + information['extension'], 'langue_presumee': langue_active, 'methode_extraction': 'copie offset/taille', 'methode_injection': 'remplacement au même offset ou reconstruction du chunk JAM'})
                        numero_image += 1
                        position += information['taille']
                    else:
                        position += 1
        (dossier / '04_IMAGES_LOCALISEES.json').write_text(json.dumps(images, ensure_ascii=False, indent=2), encoding='utf-8')
        resume = {'profil': profil, 'fichiers_jam': len(banques_jam), 'blocs_textes': sum((x['nombre_blocs_texte'] for x in banques_jam)), 'archives_afs': len(archives_audio), 'entrees_afs': sum((len(x.get('entrees', [])) for x in archives_audio)), 'cinematiques_sfd': len(cinemas), 'images': len(images), 'rapports': ['00_PROFIL_SOURCE_PS2.json', '01_BANQUES_TEXTES_JAM.json', '02_ARCHIVES_AFS_ADX.json', '03_CINEMATIQUES_SFD.json', '04_IMAGES_LOCALISEES.json']}
        (dossier / '00_INDEX_LOCALISATION_PS2.json').write_text(json.dumps(resume, ensure_ascii=False, indent=2), encoding='utf-8')
        journal.ecrire('ps2', f'Localisation PS2_VERSION cartographiée : {len(banques_jam)} JAM, {len(archives_audio)} AFS, {len(cinemas)} SFD, {len(images)} images.')
        return resume

    @classmethod
    def diagnostiquer_videos_audio(cls, data_root):
        """Analyse les formats audio et les pistes des cinématiques de la source Data."""
        import json
        LSL_MCL_MENU.LSL_MCL_Menu.titre('DIAGNOSTIQUE TOTAL VIDEO ET AUDIO')
        contexte = cls.preparer_contexte_diagnostic_cible(data_root, 'Diagnostique_total_video_et_audio')
        if contexte is None:
            print('[VIDEO/AUDIO] Source Data absente ou invalide.')
            return False
        journal = contexte['journal']
        extensions = {'.afs', '.adx', '.sfd', '.m1v', '.mpg', '.mpeg', '.wav', '.ogg', '.mp3', '.ac3', '.aif', '.aiff'}
        sources = (('PC_VERSION_BACKUP', contexte.get('pc_backup')), ('PS2_VERSION', contexte.get('ps2')))
        resume = {'sources': {}, 'nombre_fichiers': 0, 'taille_totale': 0}
        try:
            journal.entete('video', 'INVENTAIRE VIDEO ET AUDIO PC / PS2_VERSION')
            for nom_source, racine in sources:
                fiches = []
                if racine is None or not racine.exists():
                    journal.attention('video', f'{nom_source} absent.')
                    resume['sources'][nom_source] = fiches
                    continue
                fichiers = sorted((fichier for fichier in racine.rglob('*') if fichier.is_file() and fichier.suffix.lower() in extensions))
                for numero, fichier in enumerate(fichiers, start=1):
                    data = fichier.read_bytes()
                    extension = fichier.suffix.lower()
                    fiche = {'fichier': str(fichier.relative_to(racine)).replace('\\', '/'), 'adresse': str(fichier.resolve()), 'extension': extension, 'taille': len(data), 'sha256': cls.empreinte_sha256(fichier, data=data)}
                    if extension == '.adx':
                        fiche['adx'] = LSL_MCL_AUDIOS.LSL_MCL_Audios.analyser_entete_adx(data)
                    elif extension == '.afs':
                        try:
                            info_afs = LSL_MCL_AUDIOS.LSL_MCL_Audios.lire_afs(data)
                            fiche['afs'] = {'nombre_entrees': info_afs['count'], 'alignement': info_afs['alignment'], 'table_noms_offset': info_afs['table_offset'], 'table_noms_taille': info_afs['table_size']}
                        except Exception as erreur:
                            fiche['erreur_afs'] = str(erreur)
                    elif extension == '.sfd':
                        zones = LSL_MCL_AUDIOS.LSL_MCL_Audios.trouver_paquets_audio_sfd(data)
                        fiche['sfd'] = {'nombre_zones_audio': len(zones), 'capacite_audio_totale': sum((fin - debut for debut, fin in zones)), 'zones_audio': [{'index': index, 'offset_debut': debut, 'offset_debut_hex': f'0x{debut:X}', 'offset_fin': fin, 'offset_fin_hex': f'0x{fin:X}', 'taille': fin - debut} for index, (debut, fin) in enumerate(zones)]}
                    fiches.append(fiche)
                    resume['nombre_fichiers'] += 1
                    resume['taille_totale'] += len(data)
                    journal.ecrire('video', f"[{nom_source}] [{numero}/{len(fichiers)}] {fiche['fichier']}")
                resume['sources'][nom_source] = fiches
                sortie = contexte['rapport'] / f'{nom_source}_VIDEO_AUDIO.json'
                sortie.write_text(json.dumps(fiches, ensure_ascii=False, indent=2), encoding='utf-8')
            fichier_resume = contexte['rapport'] / '00_INDEX_VIDEO_AUDIO.json'
            fichier_resume.write_text(json.dumps(resume, ensure_ascii=False, indent=2), encoding='utf-8')
            print('[VIDEO/AUDIO] Fichiers :', resume['nombre_fichiers'])
            print('[VIDEO/AUDIO] Rapport :', contexte['rapport'])
            return True
        except Exception as erreur:
            journal.erreur('video', f'Échec du diagnostic vidéo/audio : {erreur}')
            raise
        finally:
            journal.terminer()
