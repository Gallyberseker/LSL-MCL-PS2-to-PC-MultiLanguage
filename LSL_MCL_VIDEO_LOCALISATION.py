"""Traitement LocalisationCinema des vidéos Larry MCL."""
from pathlib import Path
import LSL_MCL_VARIABLES as V
import LSL_MCL_LANGUAGES
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES

class LocalisationCinema:
    """Services vidéo exposés par LSL_MCL_Videos."""

    @classmethod
    def localiser_cinema(cls, data_root, langue_cible='fr'):
        """Sélectionne les SFD PS2 de la langue cible et localise leur audio sans réencoder la vidéo."""
        ffmpeg = LSL_MCL_OUTILS.LSL_MCL_Outils.outil('ffmpeg.exe') or LSL_MCL_OUTILS.LSL_MCL_Outils.outil('ffmpeg')
        if not ffmpeg:
            print('[CINEMA] FFmpeg absent.')
            return 0
        pc_root = data_root / 'Cinema' / 'FMV'
        code_langue = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible)
        racines = getattr(V, 'PS2_VERSIONS', {})
        racine_ps2 = (racines.get(code_langue) if isinstance(racines, dict) else None) or V.PS2_VERSION
        ps2_root = Path(racine_ps2) / 'Data' / 'Cinema' / 'FMV'
        if not pc_root.exists():
            print('[CINEMA] Dossier PC absent.')
            return 0
        if not ps2_root.exists():
            print('[CINEMA] Dossier PS2_VERSION absent.')
            return 0
        index_ps2 = {}
        par_nom = {}
        for fichier in ps2_root.rglob('*'):
            if not fichier.is_file() or fichier.suffix.lower() != '.sfd':
                continue
            cle = str(fichier.relative_to(ps2_root)).replace('\\', '/').lower()
            index_ps2[cle] = fichier
            par_nom.setdefault(fichier.name.lower(), []).append(fichier)
        LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(V.SFD_TEMP)
        V.SFD_TEMP.mkdir(parents=True, exist_ok=True)
        changes = 0
        refuses = 0
        sans_audio = 0
        for pc in pc_root.rglob('*'):
            if not pc.is_file() or pc.suffix.lower() != '.sfd':
                continue
            cle = str(pc.relative_to(pc_root)).replace('\\', '/').lower()
            if pc.name.lower() in V.SFD_NON_VOCAUX:
                print('[SFD ORIGINAL CONSERVE]', cle)
                continue
            homonymes = par_nom.get(pc.name.lower(), ())
            candidats_langue = [fichier for fichier in homonymes if LSL_MCL_LANGUAGES.LSL_MCL_Languages.texte_contient_marqueur_langue(fichier.relative_to(ps2_root), langue_cible)]
            if len(candidats_langue) > 1:
                print('[SFD REFUS - SOURCE AMBIGUE]', cle, LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper())
                refuses += 1
                continue
            ps2 = candidats_langue[0] if candidats_langue else index_ps2.get(cle) if len(homonymes) <= 1 else None
            if ps2 and any((LSL_MCL_LANGUAGES.LSL_MCL_Languages.texte_contient_marqueur_langue(ps2.relative_to(ps2_root), autre) for autre in V.PROFILS_LANGUES if autre != code_langue)):
                print('[SFD REFUS - LANGUE SOURCE]', cle, code_langue)
                refuses += 1
                continue
            if ps2 is None:
                continue
            try:
                succes = cls.remplacer_audio_sfd_direct(ffmpeg, pc, ps2, V.SFD_TEMP, langue_cible)
                if not succes:
                    sans_audio += 1
                    continue
                changes += 1
                print('[SFD ' + LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper() + ']', cle)
            except Exception as erreur:
                refuses += 1
                print('[SFD REFUS]', cle, ':', erreur)
        print()
        print('[CINEMA] SFD audio ' + LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper() + ' :', changes)
        print('[CINEMA] SFD refuses :', refuses)
        print('[CINEMA] SFD sans audio PC :', sans_audio)
        return changes
