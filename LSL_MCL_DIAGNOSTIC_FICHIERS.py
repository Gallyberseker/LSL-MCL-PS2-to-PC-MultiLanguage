"""Diagnostics Larry MCL : LSL_MCL_DIAGNOSTIC_FICHIERS."""
from pathlib import Path
import hashlib
import LSL_MCL_VARIABLES as V
import LSL_MCL_ANALISES
import LSL_MCL_JAMS

class DiagnosticFichiers:
    """Traitements composés par LSL_MCL_Diagnostics."""

    @classmethod
    def verifier_structure_jam(cls, original_data, nouveau_data, nom):
        """Vérifie le nombre de blocs JAM et la cohérence des tailles reconstruites."""
        original_chunks = LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(original_data)
        nouveau_chunks = LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(nouveau_data)
        if len(original_chunks) != len(nouveau_chunks):
            raise RuntimeError(f'{nom} : nombre de chunks modifie {len(original_chunks)} -> {len(nouveau_chunks)}')
        for index, chunk in enumerate(nouveau_chunks):
            header, taille1, taille2, debut, fin = chunk
            if taille1 != taille2:
                raise RuntimeError(f'{nom} chunk {index} : tailles incoherentes {taille1} != {taille2}')
            if fin > len(nouveau_data):
                raise RuntimeError(f'{nom} chunk {index} sort du fichier')
        print('[STRUCTURE OK]', nom, ':', len(nouveau_chunks), 'chunks')

    @classmethod
    def empreinte_sha256(cls, fichier, data=None):
        """Calcule SHA-256 directement pour les données fournies ou utilise le cache pour un fichier."""
        if data is not None:
            return hashlib.sha256(data).hexdigest()
        fichier = Path(fichier)
        try:
            informations = fichier.stat()
            cle_cache = (str(fichier.resolve()), informations.st_size, informations.st_mtime_ns)
        except OSError:
            cle_cache = (str(fichier.absolute()), len(data) if data is not None else None, None)
        empreinte = V._CACHE_SHA256_FICHIERS.get(cle_cache)
        if empreinte is not None:
            return empreinte
        calcul = hashlib.sha256()
        if data is not None:
            calcul.update(data)
        else:
            with fichier.open('rb') as flux:
                while True:
                    bloc = flux.read(1024 * 1024)
                    if not bloc:
                        break
                    calcul.update(bloc)
        empreinte = calcul.hexdigest()
        V._CACHE_SHA256_FICHIERS[cle_cache] = empreinte
        return empreinte

    @classmethod
    def identifier_type_fichier(cls, fichier, entete):
        """Identifie le format à partir des signatures binaires et de l’extension."""
        import mimetypes
        extension = fichier.suffix.lower()
        try:
            with fichier.open('rb') as flux:
                signature = flux.read(36864)
        except Exception:
            signature = entete
        if not signature:
            return 'Fichier vide'
        if signature.startswith(b'MZ'):
            return 'Executable Windows PE'
        if signature.startswith(b'\x7fELF'):
            return 'Executable ELF / PS2_VERSION'
        if signature.startswith(b'\xca\xfe\xba\xbe'):
            return 'Executable Java Class'
        if signature.startswith(b'\x1bLua'):
            return 'Bytecode Lua'
        if signature.startswith(b'AFS\x00'):
            return 'Archive CRI AFS'
        if signature.startswith(b'@UTF'):
            return 'Table CRI UTF'
        if signature.startswith(b'CPK '):
            return 'Archive CRI CPK'
        if signature.startswith(b'CRILAYLA'):
            return 'Compression CRI Layla'
        if signature.startswith(b'HCA\x00'):
            return 'Audio CRI HCA'
        if signature.startswith(b'AIXF'):
            return 'Audio CRI AIX'
        if signature.startswith(b'VAGp'):
            return 'Audio Sony PlayStation VAG'
        if len(signature) >= 16 and signature[0:2] == b'\x80\x00' and (b'(c)CRI' in signature[:64]):
            return 'Audio CRI ADX'
        if signature.startswith(b'BM'):
            return 'Image BMP'
        if signature.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'Image PNG'
        if signature.startswith(b'\xff\xd8\xff'):
            return 'Image JPEG'
        if signature.startswith((b'GIF87a', b'GIF89a')):
            return 'Image GIF'
        if signature.startswith(b'DDS '):
            return 'Texture DirectDraw DDS'
        if signature.startswith(b'TIM2'):
            return 'Texture PlayStation 2 TIM2'
        if signature.startswith(b'\x10\x00\x00\x00'):
            return 'Image PlayStation TIM probable'
        if signature.startswith((b'II*\x00', b'MM\x00*')):
            return 'Image TIFF'
        if signature.startswith(b'\x00\x00\x01\x00'):
            return 'Image ICO'
        if signature.startswith(b'\xabKTX'):
            return 'Texture Khronos KTX'
        if signature.startswith(b'RIFF') and signature[8:12] == b'WEBP':
            return 'Image WebP'
        if signature.startswith(b'OggS'):
            return 'Conteneur audio OGG'
        if signature.startswith(b'fLaC'):
            return 'Audio FLAC'
        if signature.startswith(b'ID3'):
            return 'Audio MP3 avec métadonnées ID3'
        if len(signature) >= 2 and signature[0] == 255 and (signature[1] & 224 == 224):
            return 'Flux audio MPEG/MP3 probable'
        if signature.startswith(b'FORM'):
            return 'Audio AIFF/IFF'
        if signature.startswith(b'RIFF'):
            sous_type = signature[8:12]
            if sous_type == b'WAVE':
                return 'Audio WAV'
            if sous_type == b'AVI ':
                return 'Vidéo AVI'
            if sous_type == b'WEBP':
                return 'Image WebP'
            return f"Conteneur RIFF ({sous_type.decode('latin-1', errors='replace')})"
        if signature.startswith(b'BIK'):
            return 'Vidéo Bink'
        if signature.startswith(b'SMK'):
            return 'Vidéo Smacker'
        if signature.startswith(b'\x00\x00\x01\xba'):
            if extension == '.sfd':
                return 'Cinématique CRI Sofdec SFD'
            if extension == '.pss':
                return 'Vidéo PlayStation 2 PSS'
            return 'Conteneur MPEG Program Stream'
        if signature.startswith(b'\x00\x00\x01\xb3'):
            return 'Flux vidéo MPEG-1/MPEG-2'
        if signature[4:8] in (b'ftyp', b'moov', b'mdat'):
            return 'Conteneur vidéo MP4/MOV'
        if signature.startswith(b'PK\x03\x04'):
            return 'Archive ZIP'
        if signature.startswith(b'Rar!\x1a\x07'):
            return 'Archive RAR'
        if signature.startswith(b"7z\xbc\xaf'\x1c"):
            return 'Archive 7-Zip'
        if signature.startswith(b'\x1f\x8b'):
            return 'Archive GZIP'
        if signature.startswith(b'BZh'):
            return 'Archive BZIP2'
        if signature.startswith(b'\xfd7zXZ\x00'):
            return 'Archive XZ'
        if signature.startswith(b'%PDF-'):
            return 'Document PDF'
        if signature.startswith(b'SQLite format 3\x00'):
            return 'Base de données SQLite'
        if signature.startswith(b'\x00\x01\x00\x00'):
            return 'Police TrueType TTF'
        if signature.startswith(b'OTTO'):
            return 'Police OpenType OTF'
        if signature.startswith((b'wOFF', b'wOF2')):
            return 'Police Web Open Font'
        if len(signature) > 32774 and signature[32769:32774] == b'CD001':
            return 'Image disque ISO 9660'
        types_extensions = {'.jam': 'Conteneur JAM du jeu', '.sfd': 'Cinématique CRI Sofdec SFD', '.afs': 'Archive CRI AFS', '.adx': 'Audio CRI ADX', '.aix': 'Audio CRI AIX', '.hca': 'Audio CRI HCA', '.vag': 'Audio PlayStation VAG', '.pss': 'Vidéo PlayStation 2 PSS', '.m1v': 'Flux vidéo MPEG-1', '.m2v': 'Flux vidéo MPEG-2', '.mpg': 'Vidéo MPEG', '.mpeg': 'Vidéo MPEG', '.mp4': 'Vidéo MP4', '.avi': 'Vidéo AVI', '.bik': 'Vidéo Bink', '.smk': 'Vidéo Smacker', '.bmp': 'Image BMP', '.dds': 'Texture DDS', '.tim': 'Image PlayStation TIM', '.tm2': 'Texture PlayStation 2 TIM2', '.tga': 'Image TGA', '.png': 'Image PNG', '.jpg': 'Image JPEG', '.jpeg': 'Image JPEG', '.gif': 'Image GIF', '.wav': 'Audio WAV', '.ogg': 'Audio OGG', '.mp3': 'Audio MP3', '.flac': 'Audio FLAC', '.iso': 'Image disque ISO', '.bin': 'Données binaires', '.dat': 'Données binaires DAT', '.pak': 'Archive PAK', '.arc': 'Archive ARC', '.zip': 'Archive ZIP', '.rar': 'Archive RAR', '.7z': 'Archive 7-Zip', '.txt': 'Document texte', '.ini': 'Configuration INI', '.cfg': 'Configuration', '.xml': 'Document XML', '.json': 'Document JSON', '.csv': 'Données CSV', '.log': 'Journal texte', '.exe': 'Executable Windows', '.dll': 'Bibliothèque Windows', '.elf': 'Executable ELF', '.irx': 'Module PlayStation 2 IRX', '.ttf': 'Police TrueType', '.otf': 'Police OpenType'}
        if extension in types_extensions:
            return types_extensions[extension]
        echantillon = signature[:4096]
        try:
            texte = echantillon.decode('utf-8')
            caracteres_lisibles = sum((caractere.isprintable() or caractere in '\r\n\t' for caractere in texte))
            if texte and caracteres_lisibles / len(texte) > 0.9:
                if texte.lstrip().startswith(('{', '[')):
                    return 'Texte JSON probable'
                if texte.lstrip().startswith('<'):
                    return 'Texte XML probable'
                return 'Fichier texte UTF-8'
        except UnicodeDecodeError:
            pass
        type_mime, _ = mimetypes.guess_type(fichier.name)
        if type_mime:
            return f'Type MIME probable : {type_mime}'
        return f'Fichier binaire inconnu (signature {signature[:16].hex()})'

    @classmethod
    def indexer_inventaire(cls, inventaire):
        """Indexe les fiches par chemin relatif sans tenir compte de la casse."""
        return {fichier['chemin_relatif'].lower(): fichier for fichier in inventaire['fichiers']}

    @classmethod
    def inventorier_source_complete(cls, nom, racine):
        """Inventorie les dossiers et analyse les fichiers avec un seul parcours de la source."""
        resultat = {'nom': nom, 'racine': str(racine), 'presente': racine.exists(), 'fichiers': [], 'dossiers': [], 'nombre_fichiers': 0, 'taille_totale': 0, 'extensions': {}, 'types': {}, 'erreurs': []}
        if not racine.exists():
            return resultat
        chemins = sorted(racine.rglob('*'))
        for dossier in sorted((chemin for chemin in chemins if chemin.is_dir())):
            resultat['dossiers'].append(str(dossier.relative_to(racine)).replace('\\', '/'))
        for fichier in sorted((chemin for chemin in chemins if chemin.is_file())):
            informations = LSL_MCL_ANALISES.LSL_MCL_Analises.analyser_fichier_complet(fichier, racine)
            resultat['fichiers'].append(informations)
            resultat['nombre_fichiers'] += 1
            resultat['taille_totale'] += informations.get('taille', 0)
            extension = informations.get('extension') or '[sans extension]'
            type_fichier = informations.get('type', 'Inconnu')
            resultat['extensions'][extension] = resultat['extensions'].get(extension, 0) + 1
            resultat['types'][type_fichier] = resultat['types'].get(type_fichier, 0) + 1
            if informations.get('erreur'):
                resultat['erreurs'].append({'fichier': informations['chemin_relatif'], 'erreur': informations['erreur']})
        return resultat
