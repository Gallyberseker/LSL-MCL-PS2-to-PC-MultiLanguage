"""Gestion des langues : DetectionLangues."""
from pathlib import Path
import re
import json
import LSL_MCL_VARIABLES as V
import LSL_MCL_COMPUTER
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES

class DetectionLangues:
    """Services de DetectionLangues."""

    @staticmethod
    def detecter_langues_ps2():
        """Détecte la langue PS2 depuis son édition et les chaînes AppInit, sans rapport disque."""
        data_ps2 = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(V.PS2_VERSION, 'DATA')
        resultat = {'version': None, 'langues': [], 'scores': {}, 'appinit': None}
        executable_ps2 = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(V.PS2_VERSION)
        version_reelle = executable_ps2.name.upper() if executable_ps2 is not None else None
        if version_reelle is not None:
            resultat['version'] = version_reelle
        profil_source = V.PS2_VERSION / 'SOURCE_PS2.json'
        if profil_source.exists():
            try:
                informations = json.loads(profil_source.read_text(encoding='utf-8'))
                if resultat['version'] is None:
                    resultat['version'] = informations.get('executable_ps2')
            except Exception:
                pass
        edition_reelle = V.EDITIONS_PS2.get(resultat['version'], {})
        langue_reelle = edition_reelle.get('langue')
        if langue_reelle in V.PROFILS_LANGUES:
            resultat['langues'] = [langue_reelle]
        if data_ps2 is None or not data_ps2.exists() or (not data_ps2.is_dir()):
            return resultat
        appinit = next((fichier for fichier in data_ps2.rglob('*') if fichier.is_file() and fichier.name.lower() == 'appinit.jam'), None)
        if appinit is None:
            return resultat
        resultat['appinit'] = str(appinit)
        victoires = {code: 0 for code in V.PROFILS_LANGUES if code in ('fr', 'en', 'de', 'es', 'it')}
        scores_totaux = {code: 0 for code in victoires}
        for bloc in LSL_MCL_TEXTES.LSL_MCL_Textes.blocs_texte(appinit.read_bytes()):
            valeurs = LSL_MCL_TEXTES.LSL_MCL_Textes.parse_chaines(bloc['payload'])
            if len(valeurs) < 5:
                continue
            scores = {code: LSL_MCL_TEXTES.LSL_MCL_Textes.score_langue(valeurs, code) for code in victoires}
            classement = sorted(scores.items(), key=lambda element: element[1], reverse=True)
            meilleur_code, meilleur_score = classement[0]
            deuxieme_score = classement[1][1]
            if meilleur_score >= 6 and meilleur_score >= deuxieme_score + 2:
                victoires[meilleur_code] += 1
                scores_totaux[meilleur_code] += meilleur_score
        resultat['langues'] = [code for code in ('fr', 'en', 'de', 'es', 'it') if victoires.get(code, 0) > 0]
        resultat['scores'] = {code: {'blocs_detectes': victoires[code], 'score_total': scores_totaux[code]} for code in victoires}
        edition = V.EDITIONS_PS2.get(resultat['version'], {})
        langue_edition = edition.get('langue')
        if langue_edition in V.PROFILS_LANGUES:
            resultat['langues'] = [langue_edition]
        return resultat

    @staticmethod
    def texte_contient_marqueur_langue(texte, langue_cible):
        """Vérifie les marqueurs de langue dans un nom de fichier ou un chemin."""
        import LSL_MCL_AUDIOS
        morceaux = set(re.findall('[a-zA-ZÀ-ÿ0-9]+', str(texte).lower()))
        return any((marqueur in morceaux for marqueur in LSL_MCL_AUDIOS.LSL_MCL_Audios.marqueurs_audio_langue(langue_cible)))

    @classmethod
    def trouver_fichier_langue(cls, dossier, nom, langue_cible):
        """Choisit une source localisée unique, ou le fichier générique correspondant."""
        if not dossier.exists():
            return None
        nom_demande = nom.lower()
        suffixe = Path(nom).suffix.lower()
        candidats = [fichier for fichier in dossier.rglob('*') if fichier.is_file() and fichier.suffix.lower() == suffixe]
        localises = [fichier for fichier in candidats if cls.texte_contient_marqueur_langue(fichier.relative_to(dossier), langue_cible) and (fichier.name.lower() == nom_demande or Path(nom).stem.lower() in fichier.stem.lower())]
        if len(localises) == 1:
            print('[SOURCE AUDIO LANGUE]', LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper(), ':', localises[0])
            return localises[0]
        if len(localises) > 1:
            raise RuntimeError(f'Plusieurs sources {nom} correspondent a la langue {LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper()} : ' + ', '.join((str(fichier) for fichier in localises)))
        return LSL_MCL_OUTILS.LSL_MCL_Outils.trouver_fichier_ci(dossier, nom)
