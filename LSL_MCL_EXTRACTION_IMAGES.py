"""Extraction Larry MCL : LSL_MCL_EXTRACTION_IMAGES."""
from pathlib import Path
import time
import json
import LSL_MCL_VARIABLES as V
import LSL_MCL_COMPUTER
import LSL_MCL_IMAGES
import LSL_MCL_JAMS
import LSL_MCL_MENU
import LSL_MCL_OUTILS
from LSL_MCL_SUIVI import SuiviProgression

class ExtractionImages:
    """Traitements hérités par LSL_MCL_Extractions."""

    @classmethod
    def dossier_extraction_images_ps2(cls):
        """Retourne le dossier d'extraction propre à l'édition PS2 locale."""
        executable = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(V.PS2_VERSION)
        if executable is None:
            return None
        version = executable.name.upper()
        return V.IMAGE_EXTRACT / f'IMG_PS2_EN_{version}'

    @classmethod
    def extraction_images_ps2_complete(cls, dossier):
        """Vérifie qu'une extraction PS2 a été terminée proprement."""
        if dossier is None:
            return False
        marqueur = Path(dossier) / 'extraction_complete.txt'
        return Path(dossier).is_dir() and marqueur.is_file()

    @classmethod
    def index_noms_jam_pc_pour_images(cls):
        """Index PC utilisé uniquement pour la casse des noms d'images PS2."""
        jam_root_pc = V.PC_VERSION_BACKUP / 'Data' / 'JamFiles' / 'PC'
        if not jam_root_pc.exists():
            jam_root_pc = V.PC_VERSION / 'Data' / 'JamFiles' / 'PC'
        index = {}
        if not jam_root_pc.exists():
            return index
        for jam_pc in jam_root_pc.rglob('*'):
            if not jam_pc.is_file() or jam_pc.suffix.lower() != '.jam':
                continue
            relatif = str(jam_pc.relative_to(jam_root_pc)).replace('\\', '__').replace('/', '__')
            index[relatif.casefold()] = relatif
        return index

    @classmethod
    def extraire_images_ps2_version(cls):
        """Extrait les BMP, DDS et ICO de la copie PS2_VERSION courante
dans un dossier séparé selon le SLES détecté."""
        executable = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(V.PS2_VERSION)
        if executable is None:
            print('[IMAGES PS2] Version PS2 introuvable.')
            return False
        version = executable.name.upper()
        destination_root = V.IMAGE_EXTRACT / f'IMG_PS2_EN_{version}'
        marqueur = destination_root / 'extraction_complete.txt'
        if cls.extraction_images_ps2_complete(destination_root):
            print('[IMAGES PS2] Extraction deja complete :', destination_root.name)
            return True
        jam_root = V.PS2_VERSION / 'Data' / 'JamFiles'
        if not jam_root.exists():
            print('[IMAGES PS2] Data/JamFiles absent.')
            return False
        if destination_root.exists():
            print('[IMAGES PS2] Extraction incomplete detectee, reconstruction :', destination_root.name)
            LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(destination_root)
        destination_root.mkdir(parents=True, exist_ok=True)
        for format_image in ('BMP', 'DDS', 'ICO'):
            (destination_root / format_image).mkdir(parents=True, exist_ok=True)
        manifeste = {}
        inconnus = []
        total = {'BMP': 0, 'DDS': 0, 'ICO': 0}
        jams = [p for p in jam_root.rglob('*') if p.is_file() and p.suffix.lower() == '.jam']
        print()
        print('=' * 70)
        print('EXTRACTION IMAGES PS2 :', version)
        print('=' * 70)
        print('JAM analyses :', len(jams))
        print('Destination :', destination_root)
        debut_extraction = time.perf_counter()
        index_jam_pc = cls.index_noms_jam_pc_pour_images()
        suivi = SuiviProgression('EXTRACTION PS2', len(jams))
        for numero_jam, jam in enumerate(sorted(jams), 1):
            suivi.avancer(numero_jam - 1, jam.name)
            candidats, inconnus_jam = LSL_MCL_IMAGES.LSL_MCL_Images.scanner_images_jam_mmap(jam, jam_root)
            inconnus.extend(inconnus_jam)
            candidats.sort(key=lambda item: (item[0], -item[1]['taille']))
            retenus = []
            for pos, info in candidats:
                fin = pos + info['taille']
                imbrique = any((pos >= ancien_pos and fin <= ancien_pos + ancien_info['taille'] for ancien_pos, ancien_info in retenus))
                if not imbrique:
                    retenus.append((pos, info))
            compte = {}
            with jam.open('rb') as flux_images:
                for pos, info in retenus:
                    fmt = info['format'].upper()
                    if fmt not in ('BMP', 'DDS', 'ICO'):
                        continue
                    compte[fmt] = compte.get(fmt, 0) + 1
                    total[fmt] += 1
                    numero = compte[fmt]
                    nom_jam_image = LSL_MCL_IMAGES.LSL_MCL_Images.nom_image_ps2_normalise(jam, jam_root, index_jam_pc)
                    nom = f"{nom_jam_image}__{fmt}__{numero:04d}__{pos:08X}__{info['description']}{info['extension']}"
                    while nom.upper().startswith('PS2__'):
                        nom = nom[5:]
                    flux_images.seek(pos)
                    bloc_image = flux_images.read(info['taille'])
                    if len(bloc_image) != info['taille']:
                        raise RuntimeError(f'Lecture image PS2 incomplete : {jam} a 0x{pos:X}')
                    destination = LSL_MCL_IMAGES.LSL_MCL_Images.chemin_image_classee(destination_root, fmt, info['largeur'], info['hauteur'], nom)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(bloc_image)
                    validation_image = LSL_MCL_IMAGES.LSL_MCL_Images.image_valide(destination)
                    if validation_image is None:
                        destination.unlink(missing_ok=True)
                        raise RuntimeError(f'Image PS2 extraite invalide : {destination}')
                    entree = {'jam': str(jam.relative_to(jam_root)), 'format': fmt, 'extension': info['extension'], 'offset': pos, 'offset_hex': f'0x{pos:08X}', 'taille': info['taille'], 'poids_octets': info['taille'], 'largeur': info['largeur'], 'hauteur': info['hauteur'], 'sha256': LSL_MCL_OUTILS.LSL_MCL_Outils.sha256(bloc_image), 'edition_ps2': version}
                    for champ in ('bpp', 'compression', 'fourcc', 'mipmaps'):
                        if champ in info:
                            entree[champ] = info[champ]
                    manifeste[nom] = entree
        suivi.terminer()
        (destination_root / 'emplacement_image.json').write_text(json.dumps(manifeste, indent=4, ensure_ascii=False), encoding='utf-8')
        (destination_root / 'signatures_images_non_prises_en_charge.json').write_text(json.dumps(inconnus, indent=4, ensure_ascii=False), encoding='utf-8')
        marqueur.write_text(f"EXTRACTION IMAGES PS2 COMPLETE\nEdition PS2 : {version}\nBMP : {total['BMP']}\nDDS : {total['DDS']}\nICO : {total['ICO']}\n", encoding='utf-8')
        print()
        print('[IMAGES PS2] Extraction terminee :', version)
        for fmt in ('BMP', 'DDS', 'ICO'):
            print(f'{fmt:6} :', total[fmt])
        print('[IMAGES PS2] Temps total :', f'{time.perf_counter() - debut_extraction:.3f} s')
        return True

    @classmethod
    def extraire_images(cls):
        """Extrait les images des JAM PC par type et dimensions et écrit le manifeste."""
        image_extract_pc = V.IMAGE_EXTRACT / 'IMG_PC_VERSION_BACKUP'
        image_extract_pc.mkdir(parents=True, exist_ok=True)
        LSL_MCL_MENU.LSL_MCL_Menu.titre('EXTRACTION DE TOUTES LES IMAGES')
        data_root = V.PC_VERSION / 'Data'
        jam_root = data_root / 'JamFiles' / 'PC'
        if not jam_root.exists():
            raise RuntimeError('PC_VERSION/Data/JamFiles/PC absent.')
        V.MANIFEST.unlink(missing_ok=True)
        V.UNKNOWN_IMAGES.unlink(missing_ok=True)
        LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(image_extract_pc)
        image_extract_pc.mkdir(parents=True, exist_ok=True)
        LSL_MCL_IMAGES.LSL_MCL_Images.creer_dossiers_images(image_extract_pc)
        manifeste = {}
        inconnus = []
        total = {}
        jams = [p for p in jam_root.rglob('*') if p.is_file() and p.suffix.lower() == '.jam']
        print('JAM analyses :', len(jams))
        debut_extraction = time.perf_counter()
        suivi = SuiviProgression('EXTRACTION PC', len(jams))
        for numero_jam, jam in enumerate(sorted(jams), 1):
            suivi.avancer(numero_jam - 1, jam.name)
            debut_jam = time.perf_counter()
            candidats, inconnus_jam = LSL_MCL_IMAGES.LSL_MCL_Images.scanner_images_jam_mmap(jam, jam_root)
            inconnus.extend(inconnus_jam)
            candidats.sort(key=lambda item: (item[0], -item[1]['taille']))
            retenus = []
            for pos, info in candidats:
                fin = pos + info['taille']
                imbrique = any((pos >= p and fin <= p + i['taille'] for p, i in retenus))
                if not imbrique:
                    retenus.append((pos, info))
            compte = {}
            with jam.open('rb') as flux_images:
                for pos, info in retenus:
                    fmt = info['format']
                    compte[fmt] = compte.get(fmt, 0) + 1
                    total[fmt] = total.get(fmt, 0) + 1
                    numero = compte[fmt]
                    nom = f"{LSL_MCL_JAMS.LSL_MCL_jams.nom_jam(jam, jam_root)}__{fmt}__{numero:04d}__{pos:08X}__{info['description']}{info['extension']}"
                    flux_images.seek(pos)
                    bloc = flux_images.read(info['taille'])
                    if len(bloc) != info['taille']:
                        raise RuntimeError(f'Lecture incomplète : {jam} à 0x{pos:X}')
                    destination = LSL_MCL_IMAGES.LSL_MCL_Images.chemin_image_classee(image_extract_pc, fmt, info['largeur'], info['hauteur'], nom)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(bloc)
                    validation_image = LSL_MCL_IMAGES.LSL_MCL_Images.image_valide(destination)
                    if validation_image is None:
                        destination.unlink(missing_ok=True)
                        raise RuntimeError(f'Image PC extraite invalide : {destination}')
                    entree = {'jam': str(jam.relative_to(jam_root)), 'format': fmt, 'extension': info['extension'], 'offset': pos, 'offset_hex': f'0x{pos:08X}', 'taille': info['taille'], 'poids_octets': info['taille'], 'largeur': info['largeur'], 'hauteur': info['hauteur'], 'sha256': LSL_MCL_OUTILS.LSL_MCL_Outils.sha256(bloc)}
                    for champ in ('bpp', 'compression', 'fourcc', 'mipmaps'):
                        if champ in info:
                            entree[champ] = info[champ]
                    manifeste[nom] = entree
            duree_jam = time.perf_counter() - debut_jam
            print('[SCAN IMAGE]', jam.relative_to(jam_root), f': {duree_jam:.3f} s,', len(retenus), 'image(s)')
        suivi.terminer()
        V.MANIFEST.write_text(json.dumps(manifeste, indent=4, ensure_ascii=False), encoding='utf-8')
        V.UNKNOWN_IMAGES.write_text(json.dumps(inconnus, indent=4, ensure_ascii=False), encoding='utf-8')
        print()
        print('Extraction validee :')
        for fmt in sorted(total):
            print(f'{fmt:6} :', total[fmt])
        print()
        print('Manifest :', V.MANIFEST)
        print('[SCAN OPTIMISE] Temps total :', f'{time.perf_counter() - debut_extraction:.3f} s')
