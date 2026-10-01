"""Traitement TraitementSfd des vidéos Larry MCL."""
from pathlib import Path
import hashlib
from LSL_MCL_VIDEO_ECRITURE import publier_sfd
import LSL_MCL_AUDIOS
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES

class TraitementSfd:
    """Services vidéo exposés par LSL_MCL_Videos."""

    @classmethod
    def remuxer_sfd_audio_long(cls, ffmpeg, pc, audio, dossier_temp):
        """Reconstruit le conteneur si la place audio PC est insuffisante.

        Les images MPEG du PC sont copiees sans reencodage et comparees apres mux.
        Le fichier PC n'est remplace qu'apres validation de la video extraite.
        """
        muxer = LSL_MCL_OUTILS.LSL_MCL_Outils.outil('sfd-muxer.exe') or LSL_MCL_OUTILS.LSL_MCL_Outils.outil('sfd-muxer')
        if not muxer:
            raise RuntimeError('sfd-muxer absent dans OUTILS : remux necessaire.')
        dossier_temp = Path(dossier_temp)
        dossier_temp.mkdir(parents=True, exist_ok=True)
        identifiant = hashlib.md5(str(pc).encode('utf-8')).hexdigest()
        video = dossier_temp / (identifiant + '_pc.m1v')
        controle = dossier_temp / (identifiant + '_controle.m1v')
        resultat = dossier_temp / (identifiant + '_nouveau.sfd')
        for fichier in (video, controle, resultat):
            LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(fichier)
        try:

            def extraction(entree, sortie):
                """Construit la commande de copie du premier flux MPEG sans réencodage."""
                return [ffmpeg, '-y', '-loglevel', 'error', '-i', str(entree), '-map', '0:v:0', '-c:v', 'copy', '-f', 'mpeg1video', str(sortie)]
            rc, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande(extraction(pc, video))
            if rc != 0 or not video.is_file() or (not video.stat().st_size):
                raise RuntimeError('Extraction video PC sans reencodage impossible : ' + (erreur or 'flux video absent'))
            rc, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande([muxer, '-y', '-v', str(video), '-a', str(audio), '-o', str(resultat), '-sfd', str(pc)])
            if rc != 0 or not resultat.is_file() or (not resultat.stat().st_size):
                raise RuntimeError('Remultiplexage SFD impossible : ' + (erreur or 'sortie absente'))
            rc, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande(extraction(resultat, controle))
            if rc != 0 or not controle.is_file() or (not cls._videos_identiques(video, controle)):
                raise RuntimeError('Video remultiplexee differente du PC : ' + (erreur or 'comparaison MPEG echouee'))
            profil_original = LSL_MCL_AUDIOS.LSL_MCL_Audios.profil_audio_sfd_pc(ffmpeg, pc)
            profil_resultat = LSL_MCL_AUDIOS.LSL_MCL_Audios.profil_audio_sfd_pc(ffmpeg, resultat)
            if not profil_original or not profil_resultat or any((profil_original[champ] != profil_resultat[champ] for champ in ('codec_name', 'frequence_hz', 'canaux'))):
                raise RuntimeError('Piste audio remultiplexee incompatible avec le PC.')
            duree_pc = profil_original['duree_secondes']
            duree_nouvelle = profil_resultat['duree_secondes']
            if duree_pc and duree_nouvelle and (abs(duree_pc - duree_nouvelle) > 0.5):
                raise RuntimeError('Duree du SFD remultiplexe differente du PC.')
            publier_sfd(pc, source=resultat)
            print('[SFD REMUX]', pc.name, '| video PC conservee | ADX adapte')
            return True
        finally:
            for fichier in (video, controle, resultat):
                LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(fichier)

    @classmethod
    def remplacer_audio_sfd_direct(cls, ffmpeg, pc, ps2, dossier_temp, langue_cible='fr'):
        """
        Remplace audio SFD direct.
    
        Paramètres:
            ffmpeg, pc, ps2, dossier_temp, langue_cible.
    
        Connexions:
            Appelée par : localiser_cinema.
            Appelle : encoder_audio_taille_pc, normaliser_code_langue, trouver_paquets_audio_sfd.
        """
        data_pc = pc.read_bytes()
        zones_pc = LSL_MCL_AUDIOS.LSL_MCL_Audios.trouver_paquets_audio_sfd(data_pc)
        if not zones_pc:
            return False
        profil_pc = LSL_MCL_AUDIOS.LSL_MCL_Audios.profil_audio_sfd_pc(ffmpeg, pc)
        if profil_pc is None:
            return False
        profil_source = LSL_MCL_AUDIOS.LSL_MCL_Audios.profil_audio_sfd_pc(ffmpeg, ps2)
        if profil_source is None:
            print('[SFD SANS PISTE SOURCE]', ps2.name, '| PC conserve')
            return False
        capacite_pc = sum((fin - debut for debut, fin in zones_pc))
        audio_pc = b''.join((data_pc[debut:fin] for debut, fin in zones_pc))
        data_ps2 = ps2.read_bytes()
        zones_ps2 = LSL_MCL_AUDIOS.LSL_MCL_Audios.trouver_paquets_audio_sfd(data_ps2)
        if zones_ps2:
            audio_ps2 = b''.join((data_ps2[debut:fin] for debut, fin in zones_ps2))
            if audio_ps2 == audio_pc:
                print('[SFD AUDIO IDENTIQUE PC/PS2]', pc.name, '| original conserve')
                return True
        position_adx = -1
        for offset in range(min(256, max(0, len(audio_pc) - 19))):
            if LSL_MCL_AUDIOS.LSL_MCL_Audios.analyser_entete_adx(audio_pc[offset:offset + 512]):
                position_adx = offset
                break
        injection_directe = position_adx >= 0 and profil_pc['codec_name'] == 'adpcm_adx'
        entete_pc = audio_pc[position_adx:] if injection_directe else profil_pc
        capacite_adx = capacite_pc - position_adx
        if not injection_directe:
            capacite_adx = capacite_pc
        dossier_temp = Path(dossier_temp)
        dossier_temp.mkdir(parents=True, exist_ok=True)
        identifiant = hashlib.md5(str(pc).encode('utf-8')).hexdigest()
        extension = {'mp2': 'mp2', 'mp3': 'mp3'}.get(profil_pc['codec_name'], 'adx')
        audio_cible = dossier_temp / f'{identifiant}.{extension}'
        LSL_MCL_AUDIOS.LSL_MCL_Audios.encoder_audio_taille_pc(ffmpeg, ps2, audio_cible, capacite_adx, langue_cible, entete_pc)
        donnees_audio = audio_cible.read_bytes()
        if not injection_directe:
            print('[SFD FORMAT PC]', pc.name, '| codec :', profil_pc['codec_name'], '|', profil_pc['frequence_hz'], 'Hz | remultiplexage sans reencodage video')
            return cls.remuxer_sfd_audio_long(ffmpeg, pc, audio_cible, dossier_temp)
        if len(donnees_audio) > capacite_adx or capacite_adx - len(donnees_audio) > 2016:
            print('[SFD CAPACITE PC]', pc.name, '| ADX :', len(donnees_audio), '| place :', capacite_adx, '| remultiplexage sans reencodage')
            return cls.remuxer_sfd_audio_long(ffmpeg, pc, audio_cible, dossier_temp)
        donnees_audio = audio_pc[:position_adx] + donnees_audio + b'\x00' * (capacite_adx - len(donnees_audio))
        sortie = bytearray(data_pc)
        position_audio = 0
        for debut, fin in zones_pc:
            taille = fin - debut
            sortie[debut:fin] = donnees_audio[position_audio:position_audio + taille]
            position_audio += taille
        if len(sortie) != len(data_pc):
            raise RuntimeError('La taille du SFD a change.')
        publier_sfd(pc, donnees=sortie)
        print('[SFD AUDIO ' + LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper() + ']', pc.name, '| paquets :', len(zones_pc), '| octets :', capacite_pc)
        return True

    @staticmethod
    def _videos_identiques(original, controle):
        """Compare les flux MPEG par blocs pour limiter la mémoire utilisée."""
        if original.stat().st_size != controle.stat().st_size:
            return False
        with original.open('rb') as entree, controle.open('rb') as verification:
            while True:
                bloc = entree.read(1024 * 1024)
                if bloc != verification.read(1024 * 1024):
                    return False
                if not bloc:
                    return True
