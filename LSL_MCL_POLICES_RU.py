"""Fusionne les lettres russes et les commandes PC dans l'atlas GUFMAIN."""
import re
import struct


class PolicesRusses:
    """Conserve les glyphes russes et le format TGA indexé de leur atlas."""

    @staticmethod
    def _caracteres(definition):
        """Lit les codes sur un octet du CharacterSet de GUFMAIN."""
        debut = definition.find(b'Font2D "GUFMAIN"')
        if debut < 0:
            raise ValueError('Définition GUFMAIN absente.')
        table = re.search(
            rb'CharacterSet\s*\[\s*(\d+)\s*\]\s*\{([^}]*)\}',
            definition[debut:],
        )
        if table is None:
            raise ValueError('CharacterSet GUFMAIN absent.')
        valeurs = []
        for jeton in re.finditer(rb'"([^"]*)"|(\d+)', table[2]):
            chaine, nombre = jeton.groups()
            if chaine is not None:
                if len(chaine) != 1:
                    raise ValueError('Un caractère GUFMAIN doit occuper un octet.')
                code = chaine[0]
            else:
                code = int(nombre)
            if not 0 <= code <= 255:
                raise ValueError('Code GUFMAIN hors de la plage 0–255.')
            valeurs.append(code)
        if not valeurs or len(valeurs) != int(table[1]):
            raise ValueError('Nombre de caractères GUFMAIN incohérent.')
        return valeurs

    @staticmethod
    def _lire(tga, caracteres):
        """Valide l'atlas et renvoie ses lignes dans l'ordre haut-gauche."""
        if (len(tga) < 18 or tga[1:3] != b'\x01\x01'
                or tga[7] != 32 or tga[16] != 8):
            raise ValueError('Atlas GUFMAIN : TGA indexé 8 bits attendu.')
        origine, nombre = struct.unpack_from('<HH', tga, 3)
        largeur, hauteur = struct.unpack_from('<HH', tga, 12)
        if not nombre or origine + nombre > 256 or not largeur or not hauteur:
            raise ValueError('Dimensions ou palette GUFMAIN invalides.')
        debut = 18 + tga[0]
        fin_palette = debut + nombre * 4
        if fin_palette > len(tga):
            raise ValueError('Palette GUFMAIN tronquée.')
        palette = [tga[i:i + 4] for i in range(debut, fin_palette, 4)]
        pixels = tga[fin_palette:]
        if len(pixels) != largeur * hauteur:
            raise ValueError('Taille de pixels GUFMAIN inattendue.')
        if any(not origine <= pixel < origine + nombre for pixel in set(pixels)):
            raise ValueError('Indice de couleur GUFMAIN absent de la palette.')
        lignes = [pixels[y * largeur:(y + 1) * largeur] for y in range(hauteur)]
        if not tga[17] & 32:
            lignes.reverse()
        if tga[17] & 16:
            lignes = [ligne[::-1] for ligne in lignes]
        separateurs = {i + origine for i, couleur in enumerate(palette)
                       if couleur == b'\x00\xfd\x01\x00'}
        limites = [x for x in range(largeur)
                   if lignes[0][x] in separateurs
                   and all(ligne[x] == lignes[0][x] for ligne in lignes)]
        if (len(limites) != len(caracteres) + 1
                or limites[0] != 0 or limites[-1] != largeur - 1):
            raise ValueError('Séparateurs GUFMAIN incompatibles avec CharacterSet.')
        return origine, palette, lignes, limites

    @staticmethod
    def fusionner(pc, russe):
        """Restitue les commandes PC à partir du code 169 sans modifier les lettres RU."""
        codes_pc = PolicesRusses._caracteres(pc['definition'])
        codes_ru = PolicesRusses._caracteres(russe['definition'])
        origine_pc, palette_pc, lignes_pc, limites_pc = PolicesRusses._lire(
            pc['principale'], codes_pc,
        )
        origine_ru, palette_ru, lignes_ru, limites_ru = PolicesRusses._lire(
            russe['principale'], codes_ru,
        )
        hauteur = len(lignes_ru)
        try:
            transparent = palette_ru.index(b'\x00\x00\x00\x00') + origine_ru
        except ValueError as erreur:
            raise ValueError('Couleur transparente GUFMAIN russe absente.') from erreur
        # setdefault conserve la première occurrence, comme list.index auparavant.
        couleurs_ru = {}
        for index, couleur in enumerate(palette_ru):
            couleurs_ru.setdefault(couleur, index)
        positions_pc = {}
        for index, code in enumerate(codes_pc):
            positions_pc.setdefault(code, index)
        conversion = {}
        for index, couleur in enumerate(palette_pc):
            cible = couleurs_ru.get(couleur)
            if cible is None:
                cible = min(range(len(palette_ru)), key=lambda j: sum(
                    (couleur[k] - palette_ru[j][k]) ** 2 * (4 if k == 3 else 1)
                    for k in range(4)))
            conversion[index + origine_pc] = cible + origine_ru
        lignes = [bytearray() for _ in range(hauteur)]
        nombre = 0
        for index, code in enumerate(codes_ru):
            if code >= 169 and code in positions_pc:
                source = positions_pc[code]
                gauche, droite = limites_pc[source:source + 2]
                largeur_glyphe = droite - gauche
                for y in range(hauteur):
                    if y < len(lignes_pc):
                        segment = bytes(conversion[v] for v in lignes_pc[y][gauche:droite])
                    else:
                        # Prolonge le séparateur lorsque l'atlas russe est plus haut.
                        segment = bytes([conversion[lignes_pc[0][gauche]]])
                        segment += bytes([transparent]) * (largeur_glyphe - 1)
                    lignes[y].extend(segment)
                nombre += 1
            else:
                gauche, droite = limites_ru[index:index + 2]
                for y in range(hauteur):
                    lignes[y].extend(lignes_ru[y][gauche:droite])
        for y in range(hauteur):
            lignes[y].append(lignes_ru[y][limites_ru[-1]])
        largeur = len(lignes[0])
        if largeur > 65535 or nombre == 0:
            raise ValueError('Fusion des commandes PC impossible.')
        entete = bytearray(russe['principale'][:18])
        struct.pack_into('<HH', entete, 12, largeur, hauteur)
        if entete[17] & 16:
            lignes = [ligne[::-1] for ligne in lignes]
        if not entete[17] & 32:
            lignes.reverse()
        fin_prefixe = 18 + entete[0] + len(palette_ru) * 4
        prefixe = russe['principale'][18:fin_prefixe]
        resultat = bytes(entete) + prefixe + b''.join(lignes)
        PolicesRusses._lire(resultat, codes_ru)
        print(f'[RU POLICE] {nombre} glyphes PC restaurés ; lettres russes conservées.')
        return {**russe, 'principale': resultat}
