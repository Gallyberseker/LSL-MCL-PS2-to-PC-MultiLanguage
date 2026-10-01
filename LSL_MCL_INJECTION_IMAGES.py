"""Traitements d'injection : images."""
from pathlib import Path
import json
import LSL_MCL_VARIABLES as V
import LSL_MCL_EXTRACTIONS
import LSL_MCL_IMAGES
import LSL_MCL_MENU
import LSL_MCL_TEXTES
from LSL_MCL_SUIVI import SuiviProgression
from LSL_MCL_ECRITURE_JAM import remplacer_emplacement


class InjectionImages:
    """Services d'injection images."""

    @staticmethod
    def injecter_images(data_root):
        """Injecte les images appariées au manifeste en conservant la taille des emplacements."""
        data_root = Path(data_root)
        LSL_MCL_MENU.LSL_MCL_Menu.titre('INJECTION DES IMAGES MODIFIEES')
        if not V.ACTIVE_IMAGE_EXTRACTION:
            print('[IMAGES] Injection automatique désactivée.')
            return 0
        if not V.MANIFEST.exists():
            print('Manifest absent : extraction automatique.')
            LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.extraire_images()
        manifeste = json.loads(V.MANIFEST.read_text(encoding='utf-8'))
        index = {}
        collisions = set()
        for nom, entree in manifeste.items():
            cle = LSL_MCL_IMAGES.LSL_MCL_Images.cle_image(nom)
            if cle in index:
                collisions.add(cle)
            else:
                index[cle] = (nom, entree)
        fichiers = [fichier for fichier in V.IMAGE_INJECT.rglob(
            '*') if fichier.is_file()]
        if not fichiers:
            print('Aucune image a injecter.')
            return 0
        jam_root = data_root / 'JamFiles' / 'PC'
        succes = 0
        suivi = SuiviProgression('INJECTION IMAGES', len(fichiers))
        for numero_fichier, fichier in enumerate(fichiers, 1):
            suivi.avancer(numero_fichier - 1, fichier.name)
            if fichier.suffix.lower() not in V.EXT_IMAGES:
                print('[REFUS IMAGE] Format non pris en charge :', fichier.name)
                continue
            cle = LSL_MCL_IMAGES.LSL_MCL_Images.cle_image(fichier.name)
            if cle in collisions:
                print('[REFUS IMAGE] Cible ambiguë dans le manifeste :', cle)
                continue
            trouve = index.get(cle)
            if not trouve:
                print('[ABSENT]', fichier.name)
                continue
            nom_original, entree = trouve
            jam = jam_root / Path(entree['jam'])
            if not jam.exists():
                print('[ABSENT JAM]', jam)
                continue
            offset = int(entree['offset'])
            taille = int(entree['taille'])
            if offset < 0 or taille <= 0 or offset + taille > jam.stat().st_size:
                print('[REFUS IMAGE] Emplacement hors du JAM :', fichier.name)
                continue
            # Le JAM fournit le gabarit : une extraction peut avoir été modifiée.
            with jam.open('rb') as source_jam:
                source_jam.seek(offset)
                original = source_jam.read(taille)
            if len(original) != taille:
                print('[REFUS IMAGE] Lecture incomplete du gabarit :', fichier.name)
                continue
            try:
                fmt = entree['format']
                if fmt == 'DDS':
                    nouveau = LSL_MCL_IMAGES.LSL_MCL_Images.reconstruire_dds(
                        fichier, original)
                elif fmt == 'BMP':
                    nouveau = LSL_MCL_IMAGES.LSL_MCL_Images.normaliser_bmp(
                        fichier, original)
                else:
                    nouveau = LSL_MCL_IMAGES.LSL_MCL_Images.encoder_generique(
                        fichier, entree)
                if len(nouveau) != entree['taille']:
                    raise ValueError(
                        f'taille finale incorrecte : {len(nouveau)} octets, emplacement attendu : {taille} octets')
                remplacer_emplacement(jam, offset, taille, nouveau)
                print('[OK IMAGE]', fichier.name, '->', entree['jam'])
                succes += 1
            except Exception as erreur:
                print('[REFUS IMAGE]', fichier.name, ':', erreur)
        suivi.terminer()
        print('Images injectees :', succes)
        return succes

    @staticmethod
    def injecter_ecran_sierra_localise(data_root, langue_cible='fr'):
        """Injecte l'écran Sierra de la langue sélectionnée dans son emplacement BMP."""
        data_root = Path(data_root)
        langue_cible = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(
            langue_cible)
        nom_image = 'IntrFram.JAM__BMP__0003__00086C98__512x512__8bpp.bmp'
        image_localisee = LSL_MCL_IMAGES.LSL_MCL_Images.chemin_image_classee(
            V.IMAGE_INJECT, 'BMP', 512, 512, nom_image)
        if not image_localisee.exists():
            print(
                f'[SIERRA {langue_cible.upper()}] Image modifiee absente :', image_localisee)
            return False
        if not V.MANIFEST.exists():
            print(f'[SIERRA {langue_cible.upper()}] Manifest absent.')
            return False
        try:
            manifeste = json.loads(V.MANIFEST.read_text(encoding='utf-8'))
            entree = None
            nom_manifeste = None
            for nom, informations in manifeste.items():
                offset = informations.get('offset')
                format_image = str(informations.get('format', '')).upper()
                jam_relatif = str(informations.get('jam', '')
                                  ).replace('\\', '/').lower()
                if offset == 552088 and format_image == 'BMP' and jam_relatif.endswith('intrfram.jam'):
                    entree = informations
                    nom_manifeste = nom
                    break
            if entree is None:
                print(
                    f'[SIERRA {langue_cible.upper()}] Entree introuvable dans le manifeste.')
                return False
            jam = data_root / 'JamFiles' / 'PC' / Path(entree['jam'])
            if not jam.exists():
                print(
                    f'[SIERRA {langue_cible.upper()}] IntrFram.JAM absent :', jam)
                return False
            offset = int(entree['offset'])
            taille = int(entree['taille'])
            data = jam.read_bytes()
            if offset + taille > len(data):
                raise RuntimeError('Zone BMP hors du fichier IntrFram.JAM.')
            original = data[offset:offset + taille]
            nouveau = LSL_MCL_IMAGES.LSL_MCL_Images.normaliser_bmp(
                image_localisee, original)
            if len(nouveau) != taille:
                raise RuntimeError(
                    f'Taille apres normalisation incorrecte : {len(nouveau)} au lieu de {taille}.')
            remplacer_emplacement(jam, offset, taille, nouveau)
            verification = jam.read_bytes()[offset:offset + taille]
            if verification != nouveau:
                raise RuntimeError('Verification apres injection echouee.')
            print(f'[SIERRA {langue_cible.upper()} INJECTE]',
                  nom_manifeste, '->', entree['jam'], '@', f'0x{offset:08X}')
            return True
        except Exception as erreur:
            print(f'[SIERRA {langue_cible.upper()} INJECTION ERREUR]', erreur)
            return False
