"""Fonctions du domaine ACX pour Larry MCL."""
from collections import Counter
from pathlib import Path
import struct
from LSL_MCL_JAM2 import LSL_MCL_Jam2
import LSL_MCL_EXTRACTIONS
import LSL_MCL_TEXTES

class LSL_MCL_Acx(LSL_MCL_Jam2):
    """Localise les banques audio ACX ; hérite du lecteur JAM2 commun."""

    @staticmethod
    def _jam2_acx_adx_info(donnees, pos):
        """Retourne la taille du flux ADX reconnu à la position donnée, sinon None.

Le calcul conserve le traitement historique de 32 échantillons par bloc."""
        if pos + 24 > len(donnees) or donnees[pos:pos + 2] != b'\x80\x00':
            return None
        cri_rel = int.from_bytes(donnees[pos + 2:pos + 4], 'big')
        cri = pos + cri_rel - 2
        if cri < pos or cri + 6 > len(donnees):
            return None
        if donnees[cri:cri + 6] != b'(c)CRI':
            return None
        encoding = donnees[pos + 4]
        block = donnees[pos + 5]
        bits = donnees[pos + 6]
        canaux = donnees[pos + 7]
        frequence = int.from_bytes(donnees[pos + 8:pos + 12], 'big')
        samples = int.from_bytes(donnees[pos + 12:pos + 16], 'big')
        if encoding not in (2, 3, 4) or block <= 0 or bits <= 0:
            return None
        if canaux <= 0 or frequence <= 0 or samples <= 0:
            return None
        blocs_audio = (samples + 31) // 32
        taille = cri_rel + 4 + blocs_audio * block * canaux
        if pos + taille > len(donnees):
            return None
        return {'size': taille}

    @staticmethod
    def _jam2_acx_scanner(jam):
        """Retourne les flux ADX avec leur bloc, position relative et position absolue.

Analyse les octets originaux du JAM ; relire le fichier après reconstruction."""
        raw = jam['raw']
        resultat = []
        pos = 0
        while True:
            pos = raw.find(b'\x80\x00', pos)
            if pos < 0:
                break
            info = LSL_MCL_Acx._jam2_acx_adx_info(raw, pos)
            if not info:
                pos += 2
                continue
            for bi, bloc in enumerate(jam['blocs']):
                debut = bloc['old'] + 32
                fin = debut + len(bloc['data'])
                if debut <= pos and pos + info['size'] <= fin:
                    info['bloc'] = bi
                    info['pos'] = pos - debut
                    info['abs'] = pos
                    resultat.append(info)
                    break
            pos += max(2, info['size'])
        return resultat

    @staticmethod
    def _jam2_acx_injecter(pc, ps2, langue):
        """Remplace en mémoire les blocs ACX PC par leurs correspondants PS2.

Retourne les nombres de banques remplacées et de flux ADX couverts.
Refuse les correspondances ambiguës, les blocs compressés et les
nombres de flux incompatibles. Aucun fichier n’est écrit ici."""
        adx_pc = LSL_MCL_Acx._jam2_acx_scanner(pc)
        adx_ps2 = LSL_MCL_Acx._jam2_acx_scanner(ps2)
        print(f'[JAM2/ACX] ADX PC : {len(adx_pc)}')
        print(f'[JAM2/ACX] ADX PS2 {langue.upper()} : {len(adx_ps2)}')
        if not adx_pc or not adx_ps2:
            raise ValueError('Aucun flux ADX detecte : injection annulee.')
        comptages_pc = Counter((a['bloc'] for a in adx_pc))
        comptages_ps2 = Counter((a['bloc'] for a in adx_ps2))
        blocs_pc = comptages_pc.keys()
        blocs_ps2 = comptages_ps2.keys()
        index_ps2 = {}
        for bi in blocs_ps2:
            bloc = ps2['blocs'][bi]
            for nom, ext in bloc['cles']:
                if ext == 'ACX':
                    if (nom, ext) in index_ps2:
                        raise ValueError(f'Ressource PS2 ambigue : {nom}.{ext}')
                    index_ps2[nom, ext] = bi
        remplaces = 0
        couverts = 0
        for bi in sorted(blocs_pc):
            bloc_pc = pc['blocs'][bi]
            cles = [(n, e) for n, e in bloc_pc['cles'] if e == 'ACX']
            correspondances = [(cle, index_ps2[cle]) for cle in cles if cle in index_ps2]
            if len(correspondances) != 1:
                noms = ', '.join((f'{n}.{e}' for n, e in cles)) or '<sans nom>'
                raise ValueError(f'Correspondance PS2 {langue.upper()} impossible/ambigue : {noms}')
            cle, bi_ps2 = correspondances[0]
            bloc_ps2 = ps2['blocs'][bi_ps2]
            if bloc_pc['cs'] != bloc_pc['ds'] or bloc_ps2['cs'] != bloc_ps2['ds']:
                raise ValueError(f'{cle[0]}.{cle[1]} compresse : abandon securite.')
            nb_pc = comptages_pc[bi]
            nb_ps2 = comptages_ps2[bi_ps2]
            if nb_pc != nb_ps2:
                raise ValueError(f'{cle[0]}.{cle[1]} : nombre ADX different (PC={nb_pc}, PS2={nb_ps2}).')
            print(f"[JAM2/ACX] {cle[0]}.{cle[1]} : {nb_pc} ADX | {len(bloc_pc['data'])} -> {len(bloc_ps2['data'])} octets")
            bloc_pc['data'] = bytearray(bloc_ps2['data'])
            remplaces += 1
            couverts += nb_pc
        if couverts != len(adx_pc):
            raise ValueError(f'Seulement {couverts}/{len(adx_pc)} ADX couverts.')
        return (remplaces, couverts)

    @staticmethod
    def localiser_audio_jam2_acx_multilangue(temp_data, langue_cible):
        """Localise les ACX des JAM globaux et des niveaux dans le dossier temporaire.

Prend en charge FR, DE, ES et IT. Retourne True si au moins un JAM
a été localisé. Conserve les logs et le bilan console.
Chaque fichier est reconstruit, écrit temporairement puis contrôlé
avant remplacement ; les incompatibilités sont consignées et ignorées."""
        langue = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible)
        if langue not in ('fr', 'de', 'es', 'it'):
            print(f'[JAM2/ACX] Langue {langue.upper()} non prise en charge : ignore.')
            return False
        pc_root = Path(temp_data) / 'JamFiles' / 'PC'
        levels_root = pc_root / 'Levels'
        if not pc_root.is_dir():
            raise FileNotFoundError(f'Dossier JamFiles/PC introuvable : {pc_root}')
        index_ps2 = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.source_ps2_index()
        fichiers_pc = []
        jams_globaux = ('AppInit.JAM', 'IntrFram.JAM', 'GameFram.JAM', 'LoadScrn.JAM')
        for nom in jams_globaux:
            pc_path = pc_root / nom
            if pc_path.is_file():
                fichiers_pc.append((pc_path, Path(nom), 'GLOBAL'))
            else:
                print(f'[JAM2/ACX] JAM global absent côté PC : {nom}')
        if levels_root.is_dir():
            for pc_path in sorted(levels_root.glob('*.JAM'), key=lambda fichier: fichier.name.upper()):
                fichiers_pc.append((pc_path, Path('Levels') / pc_path.name, 'LEVEL'))
        else:
            print('[JAM2/ACX] ATTENTION : dossier Levels absent :', levels_root)
        print()
        print('=' * 72)
        print(' AUDIO JAM2 / ACX MULTILANGUE - JAM GLOBAUX + LEVELS')
        print('=' * 72)
        print(f'Langue      : {langue.upper()}')
        print(f'JAM PC      : {len(fichiers_pc)}')
        print(f"JAM globaux : {sum((1 for _, _, t in fichiers_pc if t == 'GLOBAL'))}")
        print(f"JAM Levels  : {sum((1 for _, _, t in fichiers_pc if t == 'LEVEL'))}")
        print()
        total_analyses = 0
        total_localises = 0
        total_ignores = 0
        total_erreurs = 0
        total_acx = 0
        total_adx = 0
        for numero, (pc_path, chemin_ps2, categorie) in enumerate(fichiers_pc, start=1):
            total_analyses += 1
            print()
            print('-' * 72)
            print(f'[JAM2/ACX] [{numero}/{len(fichiers_pc)}] [{categorie}] {pc_path.name}')
            ps2_path = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.trouver_ps2_jam(chemin_ps2, index_ps2)
            if ps2_path is None:
                ps2_path = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.trouver_ps2_jam(pc_path.name, index_ps2)
            if ps2_path is None:
                print('    IGNORE : aucun JAM PS2 correspondant.')
                total_ignores += 1
                continue
            print(f'    PC  : {pc_path}')
            print(f'    PS2 : {ps2_path}')
            temporaire = pc_path.with_suffix('.JAM.jam2acx_tmp')
            try:
                pc = LSL_MCL_Acx._jam2_acx_lire(pc_path)
                ps2 = LSL_MCL_Acx._jam2_acx_lire(ps2_path)
                reconstruction_originale = LSL_MCL_Acx._jam2_acx_reconstruire(pc)
                if reconstruction_originale != pc['raw']:
                    print('    IGNORE : reconstruction PC non byte-identique.')
                    total_ignores += 1
                    continue
                print('    Reconstruction PC byte-identique : OK')
                remplaces, attendus = LSL_MCL_Acx._jam2_acx_injecter(pc, ps2, langue)
                resultat = LSL_MCL_Acx._jam2_acx_reconstruire(pc)
                temporaire.write_bytes(resultat)
                verification = LSL_MCL_Acx._jam2_acx_lire(temporaire)
                adx_finaux = LSL_MCL_Acx._jam2_acx_scanner(verification)
                if len(adx_finaux) != attendus:
                    temporaire.unlink(missing_ok=True)
                    raise RuntimeError(f'Verification finale ADX incorrecte : {len(adx_finaux)}/{attendus}.')
                temporaire.replace(pc_path)
                total_localises += 1
                total_acx += remplaces
                total_adx += attendus
                print(f'    OK : {remplaces} ACX / {attendus} ADX injectes pour {langue.upper()}.')
            except (OSError, ValueError, RuntimeError, struct.error) as erreur:
                total_erreurs += 1
                temporaire.unlink(missing_ok=True)
                print('    IGNORE / ERREUR :', erreur)
                continue
        print()
        print()
        print('=' * 72)
        print(' BILAN AUDIO JAM2 / ACX ' + langue.upper())
        print('=' * 72)
        print(f'JAM analyses       : {total_analyses}')
        print(f'JAM localises      : {total_localises}')
        print(f'JAM ignores        : {total_ignores}')
        print(f'JAM incompatibles  : {total_erreurs}')
        print(f'ACX injectes       : {total_acx}')
        print(f'ADX injectes       : {total_adx}')
        print('=' * 72)
        return total_localises > 0
