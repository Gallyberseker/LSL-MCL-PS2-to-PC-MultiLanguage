"""Synchronisation des durées AOS et restauration des voix françaises."""
from pathlib import Path
import csv
import re
import LSL_MCL_VARIABLES as V
import LSL_MCL_ACX
import LSL_MCL_LANGUAGES
import LSL_MCL_TEXTES

class LSL_MCL_AudioAos:
    """Traitements AOS hérités par LSL_MCL_Audios."""

    @classmethod
    def synchroniser_durees_aos(cls, data_root, langue_cible='fr'):
        """Copie les durées PS2 des seules voix AFS injectées, sans changer les index PC."""
        rapport = V.ROOT / 'RAPPORT_INJECTION_AFS.csv'
        if not rapport.is_file():
            raise FileNotFoundError(f"Rapport d'injection AFS absent : {rapport}")
        banques = {}
        with rapport.open('r', encoding='utf-8-sig', newline='') as entree:
            for ligne in csv.DictReader(entree, delimiter=';'):
                if ligne['etat'] not in ('INJECTE', 'CONVERTI_ET_INJECTE'):
                    continue
                banque = Path(ligne['conteneur'].replace('\\', '/')).stem.upper()
                nom = Path(ligne['entree_pc'].replace('\\', '/')).stem.upper()
                if banque and nom:
                    banques.setdefault(banque, set()).add(nom)
        racine_pc = Path(data_root) / 'JamFiles' / 'PC' / 'Levels'
        if not racine_pc.is_dir():
            raise FileNotFoundError(f'JAM PC introuvables : {racine_pc}')
        A = cls
        C = LSL_MCL_ACX.LSL_MCL_Acx
        motif = re.compile(b'(Segment\\s+"([^"\\r\\n]+)"\\s+)([0-9]+(?:\\.[0-9]+)?)(\\s*\\{Stream\\s+"([^"\\r\\n]+)")')
        fichiers, corrections, absentes = (0, 0, [])
        for pc_path in sorted(racine_pc.glob('*.JAM')):
            if not banques:
                break
            ps2_path = A._ps2_jam(pc_path.name)
            pc = C._jam2_acx_lire(pc_path)
            ps2 = C._jam2_acx_lire(ps2_path)
            if C._jam2_acx_reconstruire(pc) != pc['raw']:
                raise RuntimeError(f'JAM PC non reconstructible sans perte : {pc_path.name}')
            tables_ps2 = {}
            for bloc in ps2['blocs']:
                if bloc['cs'] != bloc['ds']:
                    continue
                for banque, extension in bloc['cles']:
                    if extension.upper() == 'AOS' and banque.upper() in banques:
                        table = {}
                        for m in motif.finditer(bytes(bloc['data'])):
                            if m.group(5).upper() == banque.upper().encode('ascii'):
                                table[m.group(2).upper()] = m.group(3)
                        tables_ps2[banque.upper()] = table
            changements_fichier = 0
            for bloc in pc['blocs']:
                if bloc['cs'] != bloc['ds']:
                    continue
                candidats = {nom.upper() for nom, ext in bloc['cles'] if ext.upper() == 'AOS' and nom.upper() in tables_ps2}
                if not candidats:
                    continue
                original = bytes(bloc['data'])

                def remplacer(m):
                    """Remplace la correspondance audio dans le texte AOS."""
                    nonlocal changements_fichier
                    banque = m.group(5).decode('ascii').upper()
                    segment = m.group(2).decode('ascii').upper()
                    if banque not in candidats or segment not in banques[banque]:
                        return m.group(0)
                    cible = tables_ps2[banque].get(segment.encode('ascii'))
                    if cible is None:
                        absentes.append((pc_path.name, banque, segment, m.group(3).decode('ascii')))
                        return m.group(0)
                    if cible != m.group(3):
                        changements_fichier += 1
                    return m.group(1) + cible + m.group(4)
                nouveau = motif.sub(remplacer, original)
                if nouveau != original:
                    bloc['data'] = bytearray(nouveau)
            if changements_fichier:
                resultat = C._jam2_acx_reconstruire(pc)
                temporaire = pc_path.with_suffix('.aos_tmp')
                try:
                    temporaire.write_bytes(resultat)
                    if C._jam2_acx_reconstruire(C._jam2_acx_lire(temporaire)) != resultat:
                        raise RuntimeError(f'Vérification AOS impossible : {pc_path.name}')
                    temporaire.replace(pc_path)
                finally:
                    temporaire.unlink(missing_ok=True)
                fichiers += 1
                corrections += changements_fichier
                print(f'[AOS DURÉES] {pc_path.name} : {changements_fichier} durées PS2')
        print(f'[AOS DURÉES] {corrections} durées actualisées dans {fichiers} JAM')
        if absentes:
            print(f'[AOS DURÉES] {len(absentes)} durées PS2 absentes : durées PC conservées')
        return corrections
    CIBLES = {'CCMPSTRT': ('LCMPSTRT.JAM', ('D74GU01A',)), 'CS1PTANI': ('LCRPSTRT.JAM', tuple((f'PF00LY4{x}' for x in 'ABCDEF'))), 'DG1V35GT': ('LDRMGIRL.JAM', ('27LYO1AA',)), 'FR1FB2GN': ('LFRTMAIN.JAM', ('FQ00LY9G', 'FQ00LY9H', 'FQ00LY9I')), 'PT1TF1GQ': ('LCMPTAPR.JAM', ('TF00MN1A', 'TF00MN1B', 'TF00MN1C', 'TF00MN1D', 'TF00MN1E', 'TF00MN1F', 'TF00MN5A', 'TF00MN5B', 'TF00MN5C', 'TF00MN7A', 'TF00MN7B', 'TF00MN7C', 'TF01MN1A', 'TF01MN1B', 'TP02MN1A', 'TP02MN1B', 'TP02MN1C', 'TP02MN1D', 'TP03MN1A', 'TP03MN1B', 'TP03MN1C'))}

    @classmethod
    def _nom(cls, nom):
        """Normalise le nom d’une ressource audio."""
        return Path(str(nom).replace('\\', '/')).name.lower()

    @classmethod
    def _trouver_entree_afs(cls, info, nom):
        """Trouve un enfant AFS par nom exact, puis par stem."""
        cible = cls._nom(nom)
        stem = Path(cible).stem
        exact = []
        memes_stems = []
        for i, n in enumerate(info['names']):
            nn = cls._nom(n)
            if nn == cible:
                exact.append(i)
            elif Path(nn).stem == stem:
                memes_stems.append(i)
        if len(exact) == 1:
            return exact[0]
        if len(memes_stems) == 1:
            return memes_stems[0]
        return None

    @classmethod
    def _chercher_banque(cls, raw, identifiants, chemin=()):
        """Trouve récursivement l'AFS qui contient les AHX/ADX demandés."""
        A = cls
        try:
            info = A.lire_afs(raw)
        except Exception:
            return None
        stems = {Path(A.nom_afs(n)).stem.upper() for n in info['names'] if n}
        trouves = [x for x in identifiants if x.upper() in stems]
        if trouves:
            return {'raw': raw, 'info': info, 'path': chemin, 'found': trouves}
        for i, payload in enumerate(info['payloads']):
            if not payload.startswith(b'AFS\x00'):
                continue
            nom = info['names'][i] if i < len(info['names']) else ''
            cle = nom if nom else f'#{i}'
            r = cls._chercher_banque(payload, identifiants, chemin + ((cle, i),))
            if r:
                return r
        return None

    @classmethod
    def _remplacer_banque_par_chemin(cls, pc_raw, chemin, banque_ps2):
        """Descend dans l'AFS PC et remplace uniquement la banque terminale."""
        A = cls
        if not chemin:
            return banque_ps2
        info = A.lire_afs(pc_raw)
        nom_ps2, index_ps2 = chemin[0]
        index_pc = None
        if not str(nom_ps2).startswith('#'):
            index_pc = cls._trouver_entree_afs(info, nom_ps2)
        if index_pc is None and 0 <= index_ps2 < info['count']:
            if info['payloads'][index_ps2].startswith(b'AFS\x00'):
                index_pc = index_ps2
        if index_pc is None:
            raise RuntimeError(f'Chemin AFS PC introuvable pour {nom_ps2} (index PS2 {index_ps2}).')
        enfant = info['payloads'][index_pc]
        if not enfant.startswith(b'AFS\x00'):
            raise RuntimeError(f"{nom_ps2}: le correspondant PC n'est pas un AFS.")
        nouveaux = list(info['payloads'])
        nouveaux[index_pc] = cls._remplacer_banque_par_chemin(enfant, chemin[1:], banque_ps2)
        return A.construire_afs(pc_raw, nouveaux)

    @classmethod
    def _ressource_jam(cls, jam, nom, extension):
        """Retourne le bloc JAM2 correspondant à NOM.EXT."""
        cible = (nom.upper(), extension.upper())
        candidats = [b for b in jam['blocs'] if cible in {(n.upper(), e.upper()) for n, e in b['cles']}]
        if len(candidats) != 1:
            raise RuntimeError(f'JAM2: {nom}.{extension} attendu 1 fois, trouvé {len(candidats)}.')
        return candidats[0]

    @classmethod
    def _remplacer_aos(cls, pc_path, ps2_path, stream, identifiants):
        """Remplace uniquement STREAM.AOS PC par la table PS2 complète."""
        C = LSL_MCL_ACX.LSL_MCL_Acx
        pc = C._jam2_acx_lire(pc_path)
        ps2 = C._jam2_acx_lire(ps2_path)
        if C._jam2_acx_reconstruire(pc) != pc['raw']:
            raise RuntimeError(f'{pc_path.name}: reconstruction JAM2 PC non identique.')
        bloc_pc = cls._ressource_jam(pc, stream, 'AOS')
        bloc_ps2 = cls._ressource_jam(ps2, stream, 'AOS')
        texte_ps2 = bytes(bloc_ps2['data']).decode('latin-1', errors='ignore')
        absents = [x for x in identifiants if f'"{x}"' not in texte_ps2]
        if absents:
            raise RuntimeError(f"{stream}.AOS PS2 ne contient pas : {', '.join(absents)}")
        if bloc_pc['cs'] != bloc_pc['ds'] or bloc_ps2['cs'] != bloc_ps2['ds']:
            raise RuntimeError(f'{stream}.AOS compressé : modification refusée.')
        bloc_pc['data'] = bytearray(bloc_ps2['data'])
        resultat = C._jam2_acx_reconstruire(pc)
        temp = pc_path.with_suffix(pc_path.suffix + '.audio_tmp')
        temp.write_bytes(resultat)
        try:
            verif = C._jam2_acx_lire(temp)
            bloc = cls._ressource_jam(verif, stream, 'AOS')
            texte = bytes(bloc['data']).decode('latin-1', errors='ignore')
            manquants = [x for x in identifiants if f'"{x}"' not in texte]
            if manquants:
                raise RuntimeError(f"Validation AOS échouée : {', '.join(manquants)}")
            temp.replace(pc_path)
        finally:
            if temp.exists():
                temp.unlink()

    @classmethod
    def _ps2_jam(cls, nom):
        """Localise un JAM PS2 LEVELS sans dépendre de la casse du chemin."""
        racine = Path(V.PS2_VERSION) / 'Data' / 'JAMFILES' / 'PS2' / 'LEVELS'
        direct = racine / nom
        if direct.is_file():
            return direct
        if racine.is_dir():
            for p in racine.iterdir():
                if p.is_file() and p.name.lower() == nom.lower():
                    return p
        raise FileNotFoundError(f'JAM PS2 introuvable : {nom}')

    @classmethod
    def restaurer_32_voix(cls, temp_data, langue_cible='fr'):
        """Restaure les banques PS2 des 32 voix françaises manquantes et leurs tables AOS."""
        langue = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible)
        if langue != 'fr':
            print('[AUDIO 32] Correctif spécifique aux voix FR : ignoré.')
            return 0
        pc_afs = Path(temp_data) / 'Audio' / 'CRI' / 'afs.afs'
        ps2_dir = Path(V.PS2_VERSION) / 'Data' / 'Audio' / 'CRI'
        ps2_afs = LSL_MCL_LANGUAGES.LSL_MCL_Languages.trouver_fichier_langue(ps2_dir, 'afs.afs', langue)
        if not pc_afs.is_file() or ps2_afs is None:
            raise FileNotFoundError('afs.afs PC/PS2 nécessaire au correctif 32 voix.')
        pc_raw = pc_afs.read_bytes()
        ps2_raw = Path(ps2_afs).read_bytes()
        for stream, (jam_nom, ids) in cls.CIBLES.items():
            trouve = cls._chercher_banque(ps2_raw, ids)
            if not trouve:
                raise RuntimeError(f'[{stream}] banque PS2 contenant {ids[0]} introuvable.')
            pc_raw = cls._remplacer_banque_par_chemin(pc_raw, trouve['path'], trouve['raw'])
            chemin = ' / '.join((str(x[0]) for x in trouve['path'])) or '<racine>'
            print(f'[AUDIO 32] {stream}: banque AFS PS2 restaurée ({len(ids)} voix).')
        cls.lire_afs(pc_raw)
        pc_afs.write_bytes(pc_raw)
        levels_pc = Path(temp_data) / 'JamFiles' / 'PC' / 'Levels'
        for stream, (jam_nom, ids) in cls.CIBLES.items():
            pc_jam = levels_pc / jam_nom
            ps2_jam = cls._ps2_jam(jam_nom)
            if not pc_jam.is_file():
                raise FileNotFoundError(f'JAM PC introuvable : {pc_jam}')
            cls._remplacer_aos(pc_jam, ps2_jam, stream, ids)
            print(f'[AUDIO 32] {stream}.AOS: table PS2 restaurée.')
        total = sum((len(v[1]) for v in cls.CIBLES.values()))
        print(f'[AUDIO 32] TERMINE : {total}/32 voix restaurées.')
        return total
