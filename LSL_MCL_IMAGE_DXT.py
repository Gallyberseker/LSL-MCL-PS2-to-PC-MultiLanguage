"""Service images : dxt."""
import struct

class CodecDxt:
    """Opérations de dxt des images du jeu."""

    @staticmethod
    def rgb565(r, g, b):
        """Convertit une couleur RGB en entier RGB565."""
        return (r * 31 + 127) // 255 << 11 | (g * 63 + 127) // 255 << 5 | (b * 31 + 127) // 255

    @staticmethod
    def rgb565_inverse(c):
        """Décode une couleur RGB565 en composantes RGB."""
        return ((c >> 11 & 31) * 255 // 31, (c >> 5 & 63) * 255 // 63, (c & 31) * 255 // 31)

    @staticmethod
    def palette_couleur(c0, c1, transparent):
        """Construit la palette interpolée d'un bloc DXT."""
        a = CodecDxt.rgb565_inverse(c0)
        b = CodecDxt.rgb565_inverse(c1)
        if transparent:
            c2 = tuple(((a[i] + b[i]) // 2 for i in range(3)))
            return [a, b, c2, (0, 0, 0)]
        c2 = tuple(((2 * a[i] + b[i]) // 3 for i in range(3)))
        c3 = tuple(((a[i] + 2 * b[i]) // 3 for i in range(3)))
        return [a, b, c2, c3]

    @staticmethod
    def bloc_couleur(pixels, autoriser_transparence):
        """Encode les couleurs et indices d'un bloc DXT de seize pixels."""
        transparent = autoriser_transparence and any((a < 128 for _, _, _, a in pixels))
        couleurs = [(r, g, b) for r, g, b, a in pixels if not transparent or a >= 128]
        if not couleurs:
            couleurs = [(0, 0, 0)]
        sombre = min(couleurs, key=lambda c: sum(c))
        clair = max(couleurs, key=lambda c: sum(c))
        c0 = CodecDxt.rgb565(*clair)
        c1 = CodecDxt.rgb565(*sombre)
        if transparent:
            if c0 > c1:
                c0, c1 = (c1, c0)
        else:
            if c0 < c1:
                c0, c1 = (c1, c0)
            elif c0 == c1:
                if c0 < 65535:
                    c0 += 1
                else:
                    c1 -= 1
            if c0 <= c1:
                raise RuntimeError('Bloc DXT opaque invalide : c0 doit être supérieur à c1.')
        palette = CodecDxt.palette_couleur(c0, c1, transparent)
        bits = 0
        for index, pixel in enumerate(pixels):
            r, g, b, a = pixel
            if transparent and a < 128:
                choix = 3
            else:
                limite = 3 if transparent else 4
                choix = min(range(limite), key=lambda i: (r - palette[i][0]) ** 2 + (g - palette[i][1]) ** 2 + (b - palette[i][2]) ** 2)
            bits |= choix << index * 2
        return struct.pack('<HHI', c0, c1, bits)

    @staticmethod
    def pixels_bloc(image, bx, by):
        """Extrait un bloc de seize pixels en répétant les bords si nécessaire."""
        px = image.load()
        return [px[min(bx + x, image.width - 1), min(by + y, image.height - 1)] for y in range(4) for x in range(4)]

    @staticmethod
    def encoder_dxt(image, fourcc):
        """Encode une image RGBA en blocs DXT1, DXT3 ou DXT5."""
        sortie = bytearray()
        for y in range(0, image.height, 4):
            for x in range(0, image.width, 4):
                pixels = CodecDxt.pixels_bloc(image, x, y)
                if fourcc == b'DXT1':
                    sortie += CodecDxt.bloc_couleur(pixels, True)
                elif fourcc == b'DXT3':
                    sortie += CodecDxt.alpha_dxt3(pixels)
                    sortie += CodecDxt.bloc_couleur(pixels, False)
                elif fourcc == b'DXT5':
                    sortie += CodecDxt.alpha_dxt5(pixels)
                    sortie += CodecDxt.bloc_couleur(pixels, False)
                else:
                    raise ValueError(f'DDS {fourcc!r} non convertible automatiquement')
        return bytes(sortie)

    @staticmethod
    def alpha_dxt3(pixels):
        """Encode les seize valeurs alpha sur quatre bits chacune."""
        bits = 0
        for index, pixel in enumerate(pixels):
            valeur = (pixel[3] * 15 + 127) // 255
            bits |= valeur << index * 4
        return struct.pack('<Q', bits)

    @staticmethod
    def alpha_dxt5(pixels):
        """Encode les bornes alpha et les indices interpolés d'un bloc DXT5."""
        valeurs = [pixel[3] for pixel in pixels]
        a0 = max(valeurs)
        a1 = min(valeurs)
        if a0 == a1:
            if a0:
                a1 = a0 - 1
            else:
                a0 = 1
        palette = CodecDxt.alpha_palette_dxt5(a0, a1)
        bits = 0
        for index, alpha in enumerate(valeurs):
            choix = min(range(8), key=lambda i: abs(alpha - palette[i]))
            bits |= choix << index * 3
        return bytes((a0, a1)) + bits.to_bytes(6, 'little')

    @staticmethod
    def alpha_palette_dxt5(a0, a1):
        """Construit les huit valeurs alpha DXT5 à partir des deux bornes.
    
            Les bornes sont des entiers de 0 à 255. Leur ordre détermine
            l’interpolation et la présence des valeurs fixes 0 et 255.
            """
        if a0 > a1:
            return [a0, a1, (6 * a0 + a1) // 7, (5 * a0 + 2 * a1) // 7, (4 * a0 + 3 * a1) // 7, (3 * a0 + 4 * a1) // 7, (2 * a0 + 5 * a1) // 7, (a0 + 6 * a1) // 7]
        return [a0, a1, (4 * a0 + a1) // 5, (3 * a0 + 2 * a1) // 5, (2 * a0 + 3 * a1) // 5, (a0 + 4 * a1) // 5, 0, 255]
