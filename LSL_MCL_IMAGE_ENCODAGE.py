"""Service images : encodage."""
from PIL import Image
import io
import struct
from LSL_MCL_IMAGE_DXT import CodecDxt

class EncodageImages:
    """Opérations de encodage des images du jeu."""

    @staticmethod
    def infos_dds(data):
        """Lit les dimensions, mipmaps et format du gabarit DDS."""
        if len(data) < 128 or data[:4] != b'DDS ':
            raise ValueError('DDS invalide')
        return {'largeur': struct.unpack_from('<I', data, 16)[0], 'hauteur': struct.unpack_from('<I', data, 12)[0], 'mipmaps': max(1, struct.unpack_from('<I', data, 28)[0]), 'fourcc': data[84:88]}

    @staticmethod
    def reconstruire_dds(fichier, original):
        """Reconstruit le DDS aux dimensions, mipmaps et taille du modèle original."""
        infos = EncodageImages.infos_dds(original)
        if fichier.suffix.lower() == '.dds':
            nouveau = fichier.read_bytes()
            try:
                ni = EncodageImages.infos_dds(nouveau)
                if ni == infos and len(nouveau) == len(original):
                    return nouveau
            except Exception:
                pass
        fourcc = infos['fourcc']
        if fourcc not in (b'DXT1', b'DXT3', b'DXT5'):
            raise ValueError(f'{fourcc!r} : fournir un DDS deja encode')
        with Image.open(fichier) as source:
            image = source.convert('RGBA')
        dimensions = (infos['largeur'], infos['hauteur'])
        if image.size != dimensions:
            image = image.resize(dimensions, Image.Resampling.LANCZOS)
        corps = bytearray()
        mip = image
        for niveau in range(infos['mipmaps']):
            corps += CodecDxt.encoder_dxt(mip, fourcc)
            if niveau + 1 < infos['mipmaps']:
                mip = mip.resize((max(1, mip.width // 2), max(1, mip.height // 2)), Image.Resampling.LANCZOS)
        resultat = original[:128] + corps
        if len(resultat) != len(original):
            raise ValueError(f'taille DDS generee {len(resultat)} != {len(original)}')
        return resultat

    @staticmethod
    def remplir_slot(payload, taille):
        """Complète le payload avec des zéros sans dépasser l'emplacement binaire."""
        if len(payload) > taille:
            raise ValueError(f'{len(payload)} octets > slot {taille}')
        return payload + b'\x00' * (taille - len(payload))

    @staticmethod
    def encoder_generique(fichier, entree):
        """Adapte le format et les dimensions, puis retient le plus grand encodage admissible."""
        with Image.open(fichier) as source:
            image = source.copy()
        dimensions = (entree['largeur'], entree['hauteur'])
        if image.size != dimensions:
            image = image.resize(dimensions, Image.Resampling.LANCZOS)
        fmt = entree['format']
        limite = entree['taille']
        meilleur = None

        def retenir(payload):
            """Conserve uniquement le plus grand résultat admissible."""
            nonlocal meilleur
            if len(payload) <= limite and (meilleur is None or len(payload) > len(meilleur)):
                meilleur = payload
        if fmt == 'JPG':
            image = image.convert('RGB')
            for qualite in range(98, 14, -4):
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=qualite, optimize=True, progressive=False)
                retenir(buffer.getvalue())
        elif fmt == 'PNG':
            for couleurs in (None, 256, 128, 64):
                img = image
                if couleurs:
                    img = image.convert('RGBA').quantize(colors=couleurs, method=Image.Quantize.FASTOCTREE)
                buffer = io.BytesIO()
                img.save(buffer, format='PNG', optimize=True, compress_level=9)
                retenir(buffer.getvalue())
        elif fmt == 'GIF':
            buffer = io.BytesIO()
            image.convert('P', palette=Image.Palette.ADAPTIVE).save(buffer, format='GIF', optimize=True)
            retenir(buffer.getvalue())
        elif fmt == 'WEBP':
            for qualite in range(98, 14, -4):
                buffer = io.BytesIO()
                image.save(buffer, format='WEBP', quality=qualite, method=6)
                retenir(buffer.getvalue())
        elif fmt == 'ICO':
            buffer = io.BytesIO()
            image.save(buffer, format='ICO')
            retenir(buffer.getvalue())
        else:
            raise ValueError(f'Format {fmt} non gere')
        if meilleur is None:
            raise ValueError("Impossible de faire tenir l'image dans son emplacement")
        return EncodageImages.remplir_slot(meilleur, limite)
