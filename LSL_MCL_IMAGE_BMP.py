"""Service images : bmp."""
from PIL import Image
import io
import struct

class CodecBmp:
    """Opérations de bmp des images du jeu."""

    @staticmethod
    def normaliser_bmp_image(image, original):
        """Réencode les pixels dans le gabarit BMP original en conservant sa taille."""
        template = bytearray(original)
        if template[:2] != b'BM':
            raise ValueError('BMP original invalide')
        dib = struct.unpack_from('<I', template, 14)[0]
        if dib < 40:
            raise ValueError('BMP ancien : fournir un BMP de taille binaire identique')
        offset = struct.unpack_from('<I', template, 10)[0]
        largeur = abs(struct.unpack_from('<i', template, 18)[0])
        hauteur_brute = struct.unpack_from('<i', template, 22)[0]
        hauteur = abs(hauteur_brute)
        bpp = struct.unpack_from('<H', template, 28)[0]
        compression = struct.unpack_from('<I', template, 30)[0]
        if compression != 0:
            raise ValueError(f'BMP compresse {compression}')
        if image.size != (largeur, hauteur):
            raise ValueError(f'dimensions {image.size} != {largeur}x{hauteur}')
        stride = (largeur * bpp + 31) // 32 * 4
        zone = stride * hauteur
        if offset + zone > len(template):
            raise ValueError('Zone pixels BMP invalide')
        bas_haut = hauteur_brute > 0
        pixels_sortie = bytearray(zone)
        if bpp == 24:
            img = image.convert('RGB')
            px = img.load()
            for ligne in range(hauteur):
                y = hauteur - 1 - ligne if bas_haut else ligne
                dest = ligne * stride
                for x in range(largeur):
                    r, g, b = px[x, y]
                    p = dest + x * 3
                    pixels_sortie[p:p + 3] = bytes((b, g, r))
        elif bpp == 32:
            img = image.convert('RGBA')
            px = img.load()
            for ligne in range(hauteur):
                y = hauteur - 1 - ligne if bas_haut else ligne
                dest = ligne * stride
                for x in range(largeur):
                    r, g, b, a = px[x, y]
                    p = dest + x * 4
                    pixels_sortie[p:p + 4] = bytes((b, g, r, a))
        elif bpp == 8:
            palette_debut = 14 + dib
            palette_octets = offset - palette_debut
            couleurs = min(256, palette_octets // 4)
            if couleurs < 2:
                raise ValueError('Palette BMP invalide')
            q = image.convert('RGB').quantize(colors=couleurs, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
            palette = q.getpalette()
            for index in range(couleurs):
                r = palette[index * 3]
                g = palette[index * 3 + 1]
                b = palette[index * 3 + 2]
                p = palette_debut + index * 4
                template[p:p + 4] = bytes((b, g, r, 0))
            brut = q.tobytes()
            for ligne in range(hauteur):
                y = hauteur - 1 - ligne if bas_haut else ligne
                src = y * largeur
                dst = ligne * stride
                pixels_sortie[dst:dst + largeur] = brut[src:src + largeur]
        else:
            raise ValueError(f'BMP {bpp}bpp : conversion automatique non geree')
        template[offset:offset + zone] = pixels_sortie
        return bytes(template)

    @staticmethod
    def normaliser_bmp(fichier, original):
        """Adapte l'image aux dimensions et au gabarit du BMP original."""
        if fichier.suffix.lower() == '.bmp':
            brut = fichier.read_bytes()
            if len(brut) == len(original):
                try:
                    img = Image.open(io.BytesIO(brut))
                    if img.size == Image.open(io.BytesIO(original)).size:
                        return brut
                except Exception:
                    pass
        with Image.open(fichier) as image:
            cible = Image.open(io.BytesIO(original)).size
            if image.size != cible:
                image = image.resize(cible, Image.Resampling.LANCZOS)
            return CodecBmp.normaliser_bmp_image(image, original)
