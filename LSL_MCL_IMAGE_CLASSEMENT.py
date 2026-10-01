"""Service images : classement."""
from pathlib import Path
import LSL_MCL_JAMS
import LSL_MCL_VARIABLES as V

class ClassementImages:
    """Opérations de classement des images du jeu."""

    @staticmethod
    def dossier_image_classee(racine, format_image, largeur, hauteur):
        """
        Retourne automatiquement le dossier correspondant
        au format et aux dimensions exactes de l'image.

        Exemple :
            BMP 32x32   -> BMP/32x32
            BMP 256x128 -> BMP/256x128
            DDS 640x448 -> DDS/640x448
            ICO 16x16   -> ICO/16x16
        """
        format_image = str(format_image).upper()
        dossier = racine / format_image
        if largeur > 0 and hauteur > 0:
            dossier = dossier / f'{largeur}x{hauteur}'
        return dossier

    @staticmethod
    def chemin_image_classee(racine, format_image, largeur, hauteur, nom):
        """Construit le chemin complet d'une image classée."""
        return ClassementImages.dossier_image_classee(racine, format_image, largeur, hauteur) / nom

    @staticmethod
    def creer_dossiers_images(racine):
        """
        Crée uniquement les dossiers principaux des formats.

        Les sous-dossiers de dimensions sont créés automatiquement
        lorsqu'une image est réellement rencontrée.
        """
        for format_image in V.FORMATS_IMAGES:
            (racine / format_image).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def nom_image_ps2_normalise(jam, jam_root, index_jam_pc):
        """
        Normalise UNIQUEMENT le préfixe du nom des images extraites PS2.

        Exemple :
            PS2__LOADSCRN.JAM__BMP__0019__004881D4__512x512__8bpp.bmp
            ->
            LoadScrn.JAM__BMP__0019__004881D4__512x512__8bpp.bmp

        Aucun fichier JAM source n'est renommé.
        """
        relatif_ps2 = LSL_MCL_JAMS.LSL_MCL_jams.nom_jam(jam, jam_root)
        while relatif_ps2.upper().startswith('PS2__'):
            relatif_ps2 = relatif_ps2[5:]
        return index_jam_pc.get(relatif_ps2.casefold(), relatif_ps2)

    @staticmethod
    def cle_image(nom):
        """Normalise le nom sans ses extensions d'image pour apparier une injection."""
        nom = Path(nom).name
        while Path(nom).suffix.lower() in V.EXT_IMAGES:
            nom = Path(nom).stem
        return nom.lower()
