"""Service images : validation."""
from pathlib import Path
from PIL import Image
import io
import struct

class ValidationImages:
    """Opérations de validation des images du jeu."""

    @staticmethod
    def dimensions_pillow(bloc):
        """Retourne les dimensions décodées par Pillow, ou None si illisible."""
        try:
            with Image.open(io.BytesIO(bloc)) as image:
                return image.size
        except Exception:
            return None

    @staticmethod
    def bmp_valide(data, pos):
        """Valide une image BMP à l'offset donné et retourne ses métadonnées."""
        if pos + 26 > len(data) or data[pos:pos + 2] != b'BM':
            return None
        try:
            taille = struct.unpack_from('<I', data, pos + 2)[0]
            dib = struct.unpack_from('<I', data, pos + 14)[0]
            if dib == 12:
                w = struct.unpack_from('<H', data, pos + 18)[0]
                h = struct.unpack_from('<H', data, pos + 20)[0]
                bpp = struct.unpack_from('<H', data, pos + 24)[0]
                compression = 0
            else:
                if pos + 54 > len(data):
                    return None
                w = abs(struct.unpack_from('<i', data, pos + 18)[0])
                h = abs(struct.unpack_from('<i', data, pos + 22)[0])
                bpp = struct.unpack_from('<H', data, pos + 28)[0]
                compression = struct.unpack_from('<I', data, pos + 30)[0]
        except struct.error:
            return None
        if dib not in (12, 40, 52, 56, 108, 124):
            return None
        if bpp not in (1, 4, 8, 16, 24, 32):
            return None
        if not (1 <= w <= 8192 and 1 <= h <= 8192):
            return None
        if taille < 26 or pos + taille > len(data):
            return None
        return {'format': 'BMP', 'extension': '.bmp', 'taille': taille, 'largeur': w, 'hauteur': h, 'bpp': bpp, 'compression': compression, 'description': f'{w}x{h}__{bpp}bpp'}

    @staticmethod
    def dds_valide(data, pos):
        """Valide une image DDS à l'offset donné et retourne ses métadonnées."""
        if pos + 128 > len(data) or data[pos:pos + 4] != b'DDS ':
            return None
        try:
            header = struct.unpack_from('<I', data, pos + 4)[0]
            h = struct.unpack_from('<I', data, pos + 12)[0]
            w = struct.unpack_from('<I', data, pos + 16)[0]
            mipmaps = max(1, struct.unpack_from('<I', data, pos + 28)[0])
            pf = struct.unpack_from('<I', data, pos + 76)[0]
            fourcc = data[pos + 84:pos + 88]
        except struct.error:
            return None
        if header != 124 or pf != 32:
            return None
        bloc8 = (b'DXT1', b'ATI1', b'BC4U', b'BC4S')
        bloc16 = (b'DXT3', b'DXT5', b'ATI2', b'BC5U', b'BC5S')
        if fourcc in bloc8:
            bloc = 8
        elif fourcc in bloc16:
            bloc = 16
        else:
            return None
        if not (1 <= w <= 8192 and 1 <= h <= 8192):
            return None
        taille = 128
        mw = w
        mh = h
        for _ in range(mipmaps):
            taille += max(1, (mw + 3) // 4) * max(1, (mh + 3) // 4) * bloc
            mw = max(1, mw // 2)
            mh = max(1, mh // 2)
        if pos + taille > len(data):
            return None
        fmt = fourcc.decode('ascii', errors='replace')
        return {'format': 'DDS', 'extension': '.dds', 'taille': taille, 'largeur': w, 'hauteur': h, 'fourcc': fmt, 'mipmaps': mipmaps, 'description': f'{w}x{h}__{fmt}'}

    @staticmethod
    def jpg_valide(data, pos):
        """Valide une image JPG à l'offset donné et retourne ses métadonnées."""
        if data[pos:pos + 3] != b'\xff\xd8\xff':
            return None
        fin = data.find(b'\xff\xd9', pos + 3)
        if fin < 0:
            return None
        taille = fin + 2 - pos
        if taille < 100:
            return None
        dim = ValidationImages.dimensions_pillow(data[pos:pos + taille])
        if not dim:
            return None
        w, h = dim
        return {'format': 'JPG', 'extension': '.jpg', 'taille': taille, 'largeur': w, 'hauteur': h, 'description': f'{w}x{h}'}

    @staticmethod
    def png_valide(data, pos):
        """Valide une image PNG à l'offset donné et retourne ses métadonnées."""
        signature = b'\x89PNG\r\n\x1a\n'
        if data[pos:pos + 8] != signature:
            return None
        if pos + 24 > len(data):
            return None
        try:
            w, h = struct.unpack_from('>II', data, pos + 16)
        except struct.error:
            return None
        p = pos + 8
        while p + 12 <= len(data):
            longueur = struct.unpack_from('>I', data, p)[0]
            type_chunk = data[p + 4:p + 8]
            p += longueur + 12
            if p > len(data):
                return None
            if type_chunk == b'IEND':
                return {'format': 'PNG', 'extension': '.png', 'taille': p - pos, 'largeur': w, 'hauteur': h, 'description': f'{w}x{h}'}
        return None

    @staticmethod
    def webp_valide(data, pos):
        """Valide une image WEBP à l'offset donné et retourne ses métadonnées."""
        if pos + 12 > len(data):
            return None
        if data[pos:pos + 4] != b'RIFF' or data[pos + 8:pos + 12] != b'WEBP':
            return None
        taille = struct.unpack_from('<I', data, pos + 4)[0] + 8
        if taille < 16 or pos + taille > len(data):
            return None
        dim = ValidationImages.dimensions_pillow(data[pos:pos + taille])
        if not dim:
            return None
        return {'format': 'WEBP', 'extension': '.webp', 'taille': taille, 'largeur': dim[0], 'hauteur': dim[1], 'description': f'{dim[0]}x{dim[1]}'}

    @staticmethod
    def gif_valide(data, pos):
        """Valide une image GIF à l'offset donné et retourne ses métadonnées."""
        if data[pos:pos + 6] not in (b'GIF87a', b'GIF89a'):
            return None
        recherche = pos + 13
        while True:
            fin = data.find(b';', recherche)
            if fin < 0:
                return None
            taille = fin + 1 - pos
            dim = ValidationImages.dimensions_pillow(data[pos:pos + taille])
            if dim:
                return {'format': 'GIF', 'extension': '.gif', 'taille': taille, 'largeur': dim[0], 'hauteur': dim[1], 'description': f'{dim[0]}x{dim[1]}'}
            recherche = fin + 1

    @staticmethod
    def ico_valide(data, pos):
        """Lit le répertoire ICO sans déclencher les avertissements de Pillow.

        Chaque entrée doit pointer vers des octets présents dans le JAM.
        Les dimensions déclarées dans l'entrée identifient l'icône extraite.
        """
        if data[pos:pos + 4] != b'\x00\x00\x01\x00':
            return None
        if pos + 6 > len(data):
            return None
        nombre = struct.unpack_from('<H', data, pos + 4)[0]
        if not 1 <= nombre <= 256:
            return None
        repertoire_fin = 6 + nombre * 16
        if pos + repertoire_fin > len(data):
            return None
        max_fin = repertoire_fin
        dimensions = []
        for index in range(nombre):
            p = pos + 6 + index * 16
            if p + 16 > len(data):
                return None
            taille = struct.unpack_from('<I', data, p + 8)[0]
            offset = struct.unpack_from('<I', data, p + 12)[0]
            largeur = data[p] or 256
            hauteur = data[p + 1] or 256
            if taille == 0 or offset < repertoire_fin:
                return None
            if pos + offset + taille > len(data):
                return None
            signature = data[pos + offset:pos + offset + 8]
            if signature != b'\x89PNG\r\n\x1a\n':
                if taille < 40 or struct.unpack_from('<I', data, pos + offset)[0] not in (40, 52, 56, 108, 124):
                    return None
            dimensions.append((largeur, hauteur))
            max_fin = max(max_fin, offset + taille)
        if max_fin < 22 or pos + max_fin > len(data):
            return None
        dim = max(dimensions, key=lambda taille: taille[0] * taille[1])
        return {'format': 'ICO', 'extension': '.ico', 'taille': max_fin, 'largeur': dim[0], 'hauteur': dim[1], 'description': f'{dim[0]}x{dim[1]}'}

    @staticmethod
    def image_valide(chemin):
        """
        VALIDATEUR CENTRAL DES IMAGES EXTRAITES.

        Reconnecte tous les validateurs spécialisés du moteur :
            BMP       -> bmp_valide()
            DDS       -> dds_valide()
            JPG/JPEG  -> jpg_valide()
            PNG       -> png_valide()
            WEBP      -> webp_valide()
            GIF       -> gif_valide()
            ICO       -> ico_valide()

        Le fichier réellement écrit sur le disque est relu puis contrôlé.
        Retourne les informations du validateur si l'image est correcte,
        sinon None.
        """
        chemin = Path(chemin)
        if not chemin.is_file():
            return None
        try:
            data = chemin.read_bytes()
        except OSError:
            return None
        if not data:
            return None
        validateurs = {'.bmp': ValidationImages.bmp_valide, '.dds': ValidationImages.dds_valide, '.jpg': ValidationImages.jpg_valide, '.jpeg': ValidationImages.jpg_valide, '.png': ValidationImages.png_valide, '.webp': ValidationImages.webp_valide, '.gif': ValidationImages.gif_valide, '.ico': ValidationImages.ico_valide}
        validateur = validateurs.get(chemin.suffix.lower())
        if validateur is None:
            return None
        try:
            information = validateur(data, 0)
        except (OSError, ValueError, TypeError, struct.error):
            return None
        if not information:
            return None
        if information.get('taille') != len(data):
            return None
        return information
