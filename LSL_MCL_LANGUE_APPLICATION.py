"""Gestion des langues : ApplicationLangue."""
from collections import Counter
from pathlib import Path
import re
import LSL_MCL_GEOMETRIES
import LSL_MCL_TEXTES
import LSL_MCL_VARIABLES as V

class ApplicationLangue:
    """Services de ApplicationLangue."""

    @classmethod
    def appliquer(cls, data_root, catalogue=None):
        """Injecte les traductions du catalogue dans les JAM PC."""
        import LSL_MCL_TEXTES
        import LSL_MCL_INJECTIONS
        import LSL_MCL_JAMS
        catalogue = catalogue or cls.synchroniser()
        if catalogue is None:
            raise RuntimeError('Source PC originale nécessaire pour les textes anglais.')
        if catalogue['Language'] == 'en':
            return 0
        valeurs = {cls.identite(e): e for e in catalogue['Entries']}
        dossier = data_root / 'JamFiles' / 'PC'
        bilan = Counter()
        for fichier in sorted(dossier.rglob('*')):
            if not fichier.is_file() or fichier.suffix.lower() != '.jam':
                continue
            original = fichier.read_bytes()
            sortie = bytearray(original)
            relatif = fichier.relative_to(dossier).as_posix()
            for bloc in LSL_MCL_TEXTES.LSL_MCL_Textes.blocs_texte(original):
                morceaux = []
                position = 0
                occurrences = Counter()
                modifies = 0
                ancien_bloc = bloc['payload']
                lignes = list(V.ENTRY.finditer(ancien_bloc))
                for ligne in lignes:
                    morceaux.append(ancien_bloc[position:ligne.start()])
                    cle = ligne.group(2).decode('latin1')
                    identifiant = (relatif.casefold(), bloc['chunk_index'], cle, occurrences[cle])
                    occurrences[cle] += 1
                    entree = valeurs.get(identifiant)
                    ancien = ligne.group(4)
                    nouveau = ancien
                    if entree and entree['English'] == ancien.decode('cp1252', errors='replace') and entree['translation']:
                        candidat = entree['translation']
                        avant_normalisation = candidat
                        candidat = cls.normaliser_texte_ais(candidat)
                        candidat = cls.normaliser_glyphes_jeu(candidat)
                        if candidat != avant_normalisation:
                            bilan['guillemets_ais'] += 1
                        if not cls.marqueurs_valides(entree['English'], candidat):
                            bilan['variables'] += 1
                        else:
                            if '"' in candidat:
                                bilan['guillemets_corriges'] += 1
                            if '\n' in candidat or '\r' in candidat:
                                bilan['retours_corriges'] += 1
                            candidat = cls.securiser_delimiteurs(candidat)
                            if '“' in candidat or '”' in candidat:
                                bilan['ais_invalides'] += 1
                                print('[AIS SECURITE] Guillemet invalide refusé :', relatif, '|', cle, '| index', entree.get('index', '?'))
                                candidat = None
                            if candidat is not None:
                                try:
                                    nouveau = candidat.encode('cp1252')
                                    if len(nouveau) > V.MAX_TEXTE_AIS:
                                        nouveau = ancien
                                        bilan['longs'] += 1
                                except UnicodeEncodeError:
                                    nouveau = ancien
                                    bilan['encodage'] += 1
                    modifies += nouveau != ancien
                    cr = b'\r' if ligne.group(0).endswith(b'\r') else b''
                    morceaux.append(b'"' + ligne.group(2) + b'" "' + nouveau + b'"' + cr)
                    position = ligne.end()
                if not modifies:
                    continue
                morceaux.append(ancien_bloc[position:])
                payload = b''.join(morceaux)
                compteur = LSL_MCL_TEXTES.LSL_MCL_Textes._compter_caracteres(payload)
                payload = re.sub(b'ASCIIChar\\s+\\[\\s*\\d+\\s*\\]', f'ASCIIChar   [  {compteur}  ]'.encode(), payload, count=1)
                payload = LSL_MCL_INJECTIONS.LSL_MCL_Injection.appliquer_padding_espaces_jam(payload, len(ancien_bloc))
                if payload is None or not LSL_MCL_TEXTES.LSL_MCL_Textes.payload_ais_est_valide(payload, len(lignes)):
                    bilan['capacite'] += modifies
                    continue
                sortie[bloc['begin']:bloc['end']] = payload
                bilan['appliquees'] += modifies
            sortie = bytes(sortie)
            if sortie != original:
                if len(sortie) != len(original) or LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(sortie) != LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(original):
                    raise RuntimeError(f'{relatif} : structure JAM modifiée')
                LSL_MCL_TEXTES.LSL_MCL_Textes._ecrire_jam(fichier, sortie)
        print('[AUTRE LANGUE] appliquées :', bilan['appliquees'], '| capacité :', bilan['capacite'], '| variables/marqueurs invalides :', bilan['variables'], '| guillemets AIS normalisés :', bilan['guillemets_ais'], '| guillemets corrigés :', bilan['guillemets_corriges'], '| AIS invalides refusés :', bilan['ais_invalides'], '| retours ligne corrigés :', bilan['retours_corriges'], '| texte trop long :', bilan['longs'], '| caractères indisponibles :', bilan['encodage'])
        return bilan['appliquees']

    @classmethod
    def construire_version(cls, game_root, code):
        """Construit et installe la localisation de langue libre."""
        import LSL_MCL_OUTILS
        code = cls.normaliser_code(code)
        V.LANGUE_CIBLE = code
        from LSL_MCL_CONSTRUCTION import ServiceConstruction
        from LSL_MCL_COMPUTER import LSL_MCL_Computer
        if V.ACTIVE_TRADUCTION_TEXTE_JAM:
            cls.selectionner_catalogue(code)
        if V.ACTIVE_TRADUCTION_TEXTE_JAM:
            source = LSL_MCL_OUTILS.LSL_MCL_Outils.obtenir_source_pc_construction(game_root)
        else:
            source = LSL_MCL_OUTILS.LSL_MCL_Outils.obtenir_source_pc_geometrie()
        if source is None:
            raise RuntimeError('Source PC originale absente.')
        if V.ACTIVE_TRADUCTION_TEXTE_JAM:
            catalogue = cls.synchroniser(source / 'JamFiles' / 'PC', code=code)
            if catalogue['Language'].lower() != code.lower():
                raise ValueError('Language du catalogue ne correspond pas à la langue sélectionnée.')
        temporaire = V.PC_VERSION_EDIT_TEMPS / 'Data'
        final = V.PC_VERSION_EDIT_FINI / 'Data'
        if source == temporaire:
            print('[SOURCE GEOMETRIE] Réutilisation des JAM modifiés dans TEMP.')
        else:
            LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(V.PC_VERSION_EDIT_TEMPS)
            temporaire.parent.mkdir(parents=True, exist_ok=True)
            LSL_MCL_OUTILS.LSL_MCL_Outils.copier_arbre_avec_progression(
                source, temporaire, 'CHARGEMENT PC')
        if V.ACTIVE_TRADUCTION_TEXTE_JAM:
            cls.appliquer(temporaire, catalogue)
        else:
            print('[TRADUCTION JAM] Désactivée : textes de la source sélectionnée conservés.')
        if V.ACTIVE_GEOMETRIE:
            LSL_MCL_GEOMETRIES.LSL_MCL_Geometries.patch_geometrie_v3(temporaire, code)
        else:
            print('[GEOMETRIE] Désactivée : rectangles et polices PC conservés.')
        ServiceConstruction._copier_et_publier(
            temporaire, final, 'COMPILATION FINALE', code)
        destination = Path(game_root) / 'Data'
        LSL_MCL_Computer.fermer_larry()
        ServiceConstruction._copier_et_publier(
            final, destination, 'INSTALLATION PC')
