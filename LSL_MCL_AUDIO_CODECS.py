


"""Analyse des codecs CRI et conversion audio pour les gabarits PC."""
from pathlib import Path
import io
import json
import struct
import tempfile
import wave
import LSL_MCL_LANGUAGES
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES

class LSL_MCL_AudioCodecs:
    """Traitements des codecs hérités par LSL_MCL_Audios."""

    @classmethod
    def profil_audio_sfd_pc(cls, ffmpeg, chemin):
        """Lit la piste PC du conteneur plutot que de supposer un ADX brut."""
        outil = LSL_MCL_OUTILS.LSL_MCL_Outils.outil('ffprobe.exe') or LSL_MCL_OUTILS.LSL_MCL_Outils.outil('ffprobe')
        if not outil:
            voisin = Path(ffmpeg).with_name('ffprobe.exe')
            outil = str(voisin) if voisin.exists() else None
        if not outil:
            raise RuntimeError('ffprobe absent : format audio PC inconnu.')
        rc, sortie, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande([outil, '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_name,sample_rate,channels,duration:format=duration', '-of', 'json', str(chemin)])
        if rc != 0:
            raise RuntimeError('Analyse de la piste PC impossible : ' + (erreur or 'ffprobe en echec'))
        donnees = json.loads(sortie)
        flux = donnees.get('streams', [])
        if not flux:
            return None
        piste = flux[0]
        taux = int(piste.get('sample_rate') or 0)
        canaux = int(piste.get('channels') or 0)
        duree = float(piste.get('duration') or donnees.get('format', {}).get('duration') or 0)
        if not 8000 <= taux <= 192000 or canaux not in (1, 2):
            raise RuntimeError('Frequence ou canaux PC invalides.')
        return {'codec_name': piste.get('codec_name', ''), 'frequence_hz': taux, 'canaux': canaux, 'duree_secondes': duree}

    @classmethod
    def decrire_audio(cls, data):
        """Décrit les champs CRI utiles au diagnostic, même pour un AHX."""
        if data[:4] == b'RIFF' and data[8:12] == b'WAVE':
            try:
                with wave.open(io.BytesIO(data), 'rb') as fichier:
                    return f'codec=WAV(PCM); frequence={fichier.getframerate()} Hz; canaux={fichier.getnchannels()}; version=non applicable'
            except (EOFError, wave.Error):
                return 'codec=WAV(invalide); frequence=inconnue; canaux=inconnus'
        if len(data) < 20 or data[:2] != b'\x80\x00':
            return 'codec=inconnu; frequence=inconnue; canaux=inconnus; version=inconnue'
        codec = 'AHX' if data[4] in (16, 17) else 'ADX'
        return f"codec={codec}(mode=0x{data[4]:02X}); frequence={int.from_bytes(data[8:12], 'big')} Hz; canaux={data[7]}; version=0x{data[18]:02X}"

    @classmethod
    def refus_audio(cls, motif, source, original):
        """Prépare une raison complète pour RAPPORT_INJECTION_AFS.csv."""
        return (None, f'{motif}; PS2 [{cls.decrire_audio(source)}]; PC attendu [{cls.decrire_audio(original)}]')

    @classmethod
    def convertir_audio_pour_pc(cls, source, original, nom_source):
        """Convertit WAV/AHX/ADX PS2 selon la cible PC, sans toucher aux originaux."""
        pc = cls.analyser_entete_adx(original)
        if not pc or pc['encodage'] not in (2, 3, 4, 16, 17):
            return cls.refus_audio('Entete CRI PC absente ou encodage non pris en charge', source, original)
        frequence, canaux = (pc['frequence_hz'], pc['canaux'])
        version, mode = (pc['version_adx'], pc['encodage'])
        if not (8000 <= frequence <= 96000 and 1 <= canaux <= 2):
            return cls.refus_audio('Frequence ou nombre de canaux PC non pris en charge', source, original)
        ffmpeg = LSL_MCL_OUTILS.LSL_MCL_Outils.outil('ffmpeg.exe') or LSL_MCL_OUTILS.LSL_MCL_Outils.outil('ffmpeg')
        if not ffmpeg:
            return cls.refus_audio('ffmpeg introuvable dans OUTILS', source, original)
        cri = LSL_MCL_OUTILS.LSL_MCL_Outils.outil('cricodecs.exe') or LSL_MCL_OUTILS.LSL_MCL_Outils.outil('cricodecs')
        vgm = LSL_MCL_OUTILS.LSL_MCL_Outils.outil('vgmstream-cli.exe') or LSL_MCL_OUTILS.LSL_MCL_Outils.outil('vgmstream-cli')
        extension = Path(nom_source).suffix.lower()
        if extension not in ('.adx', '.ahx', '.wav'):
            return cls.refus_audio('Extension audio PS2 inconnue', source, original)
        if mode in (16, 17) and (not cri):
            return cls.refus_audio(f'AHX PC mode 0x{mode:02X} a {frequence} Hz : cricodecs.exe absent dans OUTILS', source, original)
        if mode not in (16, 17) and (mode, version) != (3, 3) and (not cri):
            return cls.refus_audio(f'ADX PC mode {mode} version {version} : cricodecs.exe absent dans OUTILS', source, original)
        with tempfile.TemporaryDirectory(prefix='lsl_audio_') as temp:
            dossier = Path(temp)
            entree = dossier / ('source' + extension)
            wav = dossier / 'source.wav'
            wav_pc = dossier / 'pc.wav'
            cible_ahx = mode in (16, 17)
            encode = dossier / ('pc.ahx' if cible_ahx else 'pc.adx')
            entree.write_bytes(source)
            if extension == '.wav' and source[:4] == b'RIFF' and (source[8:12] == b'WAVE'):
                try:
                    with wave.open(io.BytesIO(source), 'rb') as lecteur:
                        with wave.open(str(wav), 'wb') as sortie:
                            sortie.setparams(lecteur.getparams())
                            sortie.writeframes(lecteur.readframes(lecteur.getnframes()))
                except (wave.Error, EOFError) as erreur_wav:
                    return cls.refus_audio('WAV PS2 invalide : ' + str(erreur_wav), source, original)
                code, erreur = (0, '')
            else:
                source_ahx = len(source) >= 5 and source[:2] == b'\x80\x00' and (source[4] in (16, 17))
                if source_ahx and vgm:
                    code, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande([str(vgm), '-i', '-o', str(wav), str(entree)])
                else:
                    decode = [str(ffmpeg), '-y', '-v', 'error', '-i', str(entree), '-vn', '-c:a', 'pcm_s16le', str(wav)]
                    code, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande(decode)
            if (code != 0 or not wav.is_file() or wav.stat().st_size < 44) and cri and (extension != '.wav'):
                code, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande([str(cri), str(entree), '-o', str(wav)])
            if (code != 0 or not wav.is_file() or wav.stat().st_size < 44) and vgm and (extension != '.wav'):
                code, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande([str(vgm), '-i', '-o', str(wav), str(entree)])
            if code != 0 or not wav.is_file() or wav.stat().st_size < 44:
                return cls.refus_audio('Decodage AHX/ADX impossible : ' + erreur.strip()[-160:], source, original)
            code, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande([str(ffmpeg), '-y', '-v', 'error', '-i', str(wav), '-ar', str(frequence), '-ac', str(canaux), '-c:a', 'pcm_s16le', str(wav_pc)])
            if code != 0 or not wav_pc.is_file():
                return cls.refus_audio('Adaptation frequence/canaux impossible : ' + erreur.strip()[-160:], source, original)
            if cible_ahx and cri:
                commande = [str(cri), '--encode', '-f', 'ahx', str(wav_pc), '-o', str(encode), '--mode', hex(mode), '--profile', str(frequence)]
            elif cible_ahx:
                return cls.refus_audio(f'AHX PC : placer cricodecs.exe dans OUTILS pour encoder le mode 0x{mode:02X} a {frequence} Hz', source, original)
            elif cri:
                commande = [str(cri), '--encode', '-f', 'adx', str(wav_pc), '-o', str(encode), '--mode', str(mode), '--header-version', str(version)]
            elif mode == 3 and version == 3:
                commande = [str(ffmpeg), '-y', '-v', 'error', '-i', str(wav_pc), '-c:a', 'adpcm_adx', '-f', 'adx', str(encode)]
            else:
                return cls.refus_audio(f'ADX PC mode {mode} version {version} : placer cricodecs.exe dans OUTILS pour encoder ce format', source, original)
            code, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande(commande)
            if code != 0 or not encode.is_file():
                return cls.refus_audio('Encodage AHX/ADX impossible : ' + erreur.strip()[-160:], source, original)
            resultat = encode.read_bytes()
            nouveau = cls.analyser_entete_adx(resultat)
            champs = ('encodage', 'canaux', 'frequence_hz')
            if not cible_ahx:
                champs += ('version_adx',)
            if not nouveau or any((nouveau[champ] != pc[champ] for champ in champs)):
                return cls.refus_audio('Audio produit incompatible : ' + cls.decrire_audio(resultat), source, original)
            if nouveau['nombre_echantillons'] == 0:
                return cls.refus_audio('Audio produit sans echantillons', source, original)
            codec = 'AHX' if cible_ahx else 'ADX'
            return (resultat, f'{codec} PC mode 0x{mode:02X} version {version}, {frequence} Hz, {canaux} canal(aux)')

    @classmethod
    def analyser_entete_adx(cls, data):
        """Analyse entete ADX."""
        if len(data) < 20 or data[:2] != b'\x80\x00':
            return None
        try:
            offset_audio = struct.unpack_from('>H', data, 2)[0] + 4
            if offset_audio < 24 or offset_audio > len(data) or data[offset_audio - 6:offset_audio] != b'(c)CRI':
                return None
            canaux = data[7]
            frequence = struct.unpack_from('>I', data, 8)[0]
            echantillons = struct.unpack_from('>I', data, 12)[0]
            version = data[18]
        except Exception:
            return None
        return {'version_adx': version, 'version_adx_hex': f'0x{version:02X}', 'encodage': data[4], 'taille_bloc': data[5], 'bits_echantillon': data[6], 'canaux': canaux, 'frequence_hz': frequence, 'nombre_echantillons': echantillons, 'duree_secondes': round(echantillons / frequence, 6) if frequence > 0 else None, 'offset_audio': offset_audio, 'offset_audio_hex': f'0x{offset_audio:X}', 'entete_adx_valide': True, 'compatibilite_pc': 'a_comparer'}

    @classmethod
    def encoder_audio_taille_pc(cls, ffmpeg, source_ps2, destination, taille_cible, langue_cible='fr', modele_pc=None):
        """Encode audio taille PC."""
        index_audio = cls.trouver_index_audio_langue(ffmpeg, source_ps2, langue_cible)
        pc = modele_pc if isinstance(modele_pc, dict) else cls.analyser_entete_adx(modele_pc or b'')
        if not pc or not 8000 <= pc['frequence_hz'] <= 192000:
            raise RuntimeError('Format audio PC absent ou frequence invalide.')
        taux = pc['frequence_hz']
        echantillons = pc.get('nombre_echantillons', 0)
        duree = f'{echantillons / taux:.9f}' if echantillons else f"{pc.get('duree_secondes', 0):.9f}"
        LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(destination)
        if pc.get('version_adx') == 4 and pc.get('encodage') == 3 and (pc.get('taille_bloc') == 18) and (pc['canaux'] in (1, 2)) and isinstance(modele_pc, bytes):
            source_info = cls.profil_audio_sfd_pc(ffmpeg, source_ps2)
            if not source_info:
                raise RuntimeError('Piste audio absente de la source PS2.')
            cible_duree = echantillons / taux
            vitesse = source_info['duree_secondes'] / cible_duree if source_info['duree_secondes'] else 1.0
            filtres = []
            if 0.5 <= vitesse <= 2.0:
                filtres.append(f'atempo={vitesse:.9f}')
            filtres.extend((f'aresample={taux}', 'apad', f'atrim=end_sample={echantillons}', 'asetpts=N/SR/TB'))
            temporaire = destination.with_name(destination.stem + '_v3.adx')
            rc, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande([ffmpeg, '-y', '-v', 'error', '-i', str(source_ps2), '-map', f'0:a:{index_audio}', '-af', ','.join(filtres), '-ar', str(taux), '-ac', str(pc['canaux']), '-c:a', 'adpcm_adx', '-f', 'adx', str(temporaire)])
            if rc != 0 or not temporaire.is_file():
                raise RuntimeError('Encodage des trames ADX impossible : ' + (erreur or 'sortie absente'))
            brut = temporaire.read_bytes()
            info = cls.analyser_entete_adx(brut)
            debut = info['offset_audio'] if info else 0
            fin = brut.rfind(b'\x80\x01')
            nb_octets = taille_cible - pc['offset_audio'] - 18
            unite_trame = pc['taille_bloc'] * pc['canaux']
            if not info or info['version_adx'] != 3 or info['canaux'] != pc['canaux'] or (info['frequence_hz'] != taux) or (not echantillons <= info['nombre_echantillons'] <= echantillons + 32) or (fin != len(brut) - 18) or (fin < debut) or (fin - debut != nb_octets) or nb_octets % unite_trame:
                raise RuntimeError('Trames ADX incompatibles avec la duree PC.')
            audio = modele_pc[:pc['offset_audio']] + brut[debut:fin] + modele_pc[-18:]
            if len(audio) != taille_cible:
                raise RuntimeError('Taille ADX v4 finale incorrecte.')
            destination.write_bytes(audio)
            LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(temporaire)
            print('[ADX ' + LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper() + ' V4 PC]', source_ps2.name, '|', taux, 'Hz | echantillons :', echantillons, '| octets :', len(audio))
            return destination
        entree = [ffmpeg, '-y', '-loglevel', 'error', '-i', str(source_ps2), '-map', f'0:a:{index_audio}']
        if echantillons:
            entree += ['-af', f'aresample={taux},apad,atrim=end_sample={echantillons},asetpts=N/SR/TB']
        elif float(duree) > 0:
            entree += ['-af', 'apad', '-t', duree]
        entree += ['-ac', str(pc['canaux']), '-ar', str(taux)]
        codec_pc = pc.get('codec_name', 'adpcm_adx')
        formats = {'adpcm_adx': ('adpcm_adx', 'adx'), 'mp2': ('mp2', 'mp2'), 'mp3': ('libmp3lame', 'mp3')}
        if codec_pc not in formats:
            raise RuntimeError(f'Codec audio PC {codec_pc} non pris en charge par ce muxeur.')
        codec, format_sortie = formats[codec_pc]
        if codec_pc == 'adpcm_adx' and pc.get('version_adx', 3) != 3:
            cri = LSL_MCL_OUTILS.LSL_MCL_Outils.outil('cricodecs.exe') or LSL_MCL_OUTILS.LSL_MCL_Outils.outil('cricodecs')
            if not cri:
                raise RuntimeError('Version ADX PC necessite cricodecs dans OUTILS.')
            wav = destination.with_suffix('.wav')
            rc, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande(entree + ['-c:a', 'pcm_s16le', str(wav)])
            if rc != 0 or not wav.exists():
                raise RuntimeError('Preparation WAV impossible : ' + (erreur or 'erreur inconnue'))
            commande = [str(cri), '--encode', '-f', 'adx', str(wav), '-o', str(destination), '--mode', str(pc['encodage']), '--header-version', str(pc['version_adx'])]
        else:
            commande = entree + ['-c:a', codec, '-f', format_sortie, str(destination)]
        rc, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande(commande)
        if rc != 0 or not destination.exists() or (not destination.stat().st_size):
            raise RuntimeError('Encodage ADX impossible : ' + (erreur or 'erreur inconnue'))
        audio = destination.read_bytes()
        if codec_pc == 'adpcm_adx':
            produit = cls.analyser_entete_adx(audio)
            if not produit or produit['frequence_hz'] != taux or produit['canaux'] != pc['canaux']:
                raise RuntimeError('Format ADX encode incompatible avec la piste PC.')
            if echantillons and (not echantillons <= produit['nombre_echantillons'] < echantillons + 32):
                raise RuntimeError('Duree audio cible differente de la piste PC.')
            if 'version_adx' in pc and produit['version_adx'] != pc['version_adx']:
                raise RuntimeError('Version ADX encode differente de la piste PC.')
        print('[AUDIO ' + LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper() + ' PC]', source_ps2.name, '| taux :', taux, 'Hz | canaux :', pc['canaux'], '| codec :', codec_pc, '| duree :', duree, 's | taille :', len(audio), '| capacite PC :', taille_cible)
        return destination

    @classmethod
    def trouver_index_audio_langue(cls, ffmpeg, source, langue_cible):
        """Implémente le traitement interne `trouver_index_audio_langue` utilisé par le pipeline de localisation ou de diagnostic."""
        ffmpeg_path = Path(ffmpeg)
        noms = ('ffprobe.exe', 'ffprobe')
        ffprobe = None
        for nom in noms:
            voisin = ffmpeg_path.with_name(nom)
            if voisin.exists():
                ffprobe = str(voisin)
                break
            candidat = LSL_MCL_OUTILS.LSL_MCL_Outils.outil(nom)
            if candidat:
                ffprobe = candidat
                break
        if ffprobe is None:
            raise RuntimeError("ffprobe absent : impossible d'identifier la langue de la piste audio.")
        rc, sortie, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande([ffprobe, '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index:stream_tags=language,title', '-of', 'json', str(source)])
        if rc != 0:
            raise RuntimeError('Analyse ffprobe impossible : ' + (erreur or 'erreur inconnue'))
        try:
            pistes = json.loads(sortie).get('streams', [])
        except Exception as erreur_json:
            raise RuntimeError('Réponse ffprobe invalide.') from erreur_json
        if not pistes:
            raise RuntimeError('Aucune piste audio dans le SFD PS2_VERSION.')
        if len(pistes) == 1:
            return 0
        correspondantes = []
        for index_audio, piste in enumerate(pistes):
            tags = piste.get('tags', {}) or {}
            description = ' '.join((str(tags.get(cle, '')) for cle in ('language', 'LANGUAGE', 'title', 'TITLE')))
            if LSL_MCL_LANGUAGES.LSL_MCL_Languages.texte_contient_marqueur_langue(description, langue_cible):
                correspondantes.append(index_audio)
        if len(correspondantes) != 1:
            raise RuntimeError(f'SFD PS2_VERSION avec plusieurs pistes : langue {LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper()} absente ou ambiguë dans les métadonnées.')
        return correspondantes[0]

    @classmethod
    def trouver_paquets_audio_sfd(cls, data):
        """Repère les paquets audio CRI dans les données du conteneur SFD."""
        zones = []
        secteur = 2048
        for bloc in range(0, len(data) - secteur + 1, secteur):
            debut = bloc + 12
            if data[bloc:bloc + 4] != b'\x00\x00\x01\xba' or data[debut:debut + 4] != b'\x00\x00\x01\xc0':
                continue
            longueur = int.from_bytes(data[debut + 4:debut + 6], 'big')
            fin = debut + 6 + longueur
            if not longueur or fin > bloc + secteur:
                raise RuntimeError('Paquet audio SFD hors de son secteur.')
            curseur = debut + 6
            if curseur + 3 <= fin and data[curseur] & 192 == 128:
                curseur += 3 + data[curseur + 2]
            else:
                while curseur < fin and data[curseur] == 255:
                    curseur += 1
                if curseur + 2 <= fin and data[curseur] & 192 == 64:
                    curseur += 2
                if curseur >= fin:
                    raise RuntimeError('Entete PES audio SFD tronquee.')
                marqueur = data[curseur] & 240
                if marqueur == 32:
                    curseur += 5
                elif marqueur == 48:
                    curseur += 10
                elif data[curseur] == 15:
                    curseur += 1
            if not debut + 6 <= curseur < fin:
                raise RuntimeError('Charge utile PES audio SFD invalide.')
            zones.append((curseur, fin))
        return zones
