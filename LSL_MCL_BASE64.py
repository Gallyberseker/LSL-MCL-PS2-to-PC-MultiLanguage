"""Génération des images Sierra intégrées pour l'injection dans Larry MCL."""

import base64
import hashlib
import re
import tempfile
import zlib
from pathlib import Path

import LSL_MCL_VARIABLES as V
import LSL_MCL_IMAGES
import LSL_MCL_TEXTES


class LSL_MCL_Base64:
    """Décode et vérifie les images Sierra avant de les publier."""

    @staticmethod
    def generer_ecran_sierra_localise(langue_cible="fr"):
        """Génère l'image Sierra de la langue cible pour l'injection.

        Vérifie la taille, la signature BMP et l'empreinte SHA-256 avant
        écriture. Remplace la destination uniquement après une écriture
        complète. Renvoie False si l'image est absente ou en cas d'échec.
        """
        langue_cible = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(
            langue_cible)

        images_par_langue = {code: f'BASE64_IMG_{code.upper()}_ALLRIGHT_SIERRA'
                             for code in ('fr', 'en', 'de', 'es', 'it', 'ru')}

        empreintes_attendues = {'ru': 'e1eeb7aca0356cee14c394d87b77b7cbc680d64f758dd394a609766c3c073432', 'fr': '3f8f38cff0d0d5c1f16eb5d17874a8501dfc9ca1fbcddaea717fe735708e903b', 'en': '5d050df701352d0a97c9cf37fdfd1c484689b4ed7805311ac8ad5ebb4a7075f5',
                                'de': '95ad554df401fbbdc9d820a0f13e477910562773c55ad719af3e96dc6521a1cb', 'es': '56cff9cd79aadb88131bac06a924646555d468a525ccd76a203c7c93b904b3f6', 'it': '80a99460f10ec721c24c60ad845bdfe0d53e80026eeb4de795e0cb4e4473e7d7'}

        nom_variable = images_par_langue.get(langue_cible)

        if nom_variable is None:
            print("[SIERRA] Aucune image integree pour la langue :", langue_cible)
            return False

        temporaire = None
        try:
            image_base64 = getattr(V, nom_variable)
            chaine = re.sub(r"\s+", "", image_base64)
            if not chaine:
                raise RuntimeError("Donnees Base64 Sierra absentes.")
            donnees_bmp = zlib.decompress(
                base64.b64decode(chaine, validate=True))
            if len(donnees_bmp) not in (262728, 786486):
                raise RuntimeError(
                    f"Taille BMP Sierra incorrecte : {len(donnees_bmp)} octets.")
            if not donnees_bmp.startswith(b"BM"):
                raise RuntimeError("Signature BMP Sierra invalide.")
            if hashlib.sha256(donnees_bmp).hexdigest() != empreintes_attendues[langue_cible]:
                raise RuntimeError("Empreinte Sierra incorrecte.")

            nom_image = "IntrFram.JAM__BMP__0003__00086C98__512x512__8bpp.bmp"
            destination = LSL_MCL_IMAGES.LSL_MCL_Images.chemin_image_classee(
                V.IMAGE_INJECT, "BMP", 512, 512, nom_image)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=destination.parent, prefix=".sierra_",
                suffix=".tmp", delete=False,
            ) as fichier:
                temporaire = Path(fichier.name)
                fichier.write(donnees_bmp)
            temporaire.replace(destination)
            print(
                f"[SIERRA {langue_cible.upper()}] Image generee :", destination.name)
            return True
        except (OSError, ValueError, RuntimeError, zlib.error) as erreur:
            print(f"[SIERRA {langue_cible.upper()} ERREUR]", erreur)
            return False
        finally:
            if temporaire is not None:
                try:
                    temporaire.unlink(missing_ok=True)
                except OSError as erreur:
                    print(
                        "[SIERRA NETTOYAGE] Fichier temporaire conserve :", temporaire)
                    print(erreur)
