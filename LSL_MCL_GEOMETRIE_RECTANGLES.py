"""Application des rectangles et tailles globales dans les JAM préparés."""
from pathlib import Path
import re
import LSL_MCL_VARIABLES as V
import LSL_MCL_TEXTES
from LSL_MCL_GEOMETRIE_POLICES import appliquer_polices_par_langue

def remplacer_rectangle_bloc(bloc, ancien, nouveau, nombre):
    """Remplace les coordonnées sans changer la taille binaire du bloc."""
    if len(nouveau) <= len(ancien):
        return bloc.replace(ancien, nouveau.ljust(len(ancien), b' '), nombre)

    motif = re.compile(
        rb'(?m)^([ \t]*)'
        + re.escape(ancien)
        + rb'([ \t]*)(?=\r?$)'
    )
    correspondances = list(motif.finditer(bloc))[:nombre]

    if len(correspondances) != nombre:
        raise ValueError(
            'Rectangle trop long : ligne complète introuvable ; '
            'aucune écriture effectuée.'
        )

    remplacements = []
    for correspondance in correspondances:
        indentation = correspondance.group(1)
        espaces_fin = correspondance.group(2)
        surplus = len(nouveau) - len(ancien)

        if len(indentation) + len(espaces_fin) < surplus:
            raise ValueError(
                'Rectangle trop long : espaces insuffisants sur la ligne ; '
                'aucune écriture effectuée.'
            )

        # Réutiliser d’abord les espaces en fin de ligne.
        retirer_fin = min(surplus, len(espaces_fin))
        espaces_fin = espaces_fin[:len(espaces_fin) - retirer_fin]
        retirer_debut = surplus - retirer_fin
        indentation = indentation[retirer_debut:]

        remplacements.append((
            correspondance.start(),
            correspondance.end(),
            indentation + nouveau + espaces_fin,
        ))

    resultat = bloc
    for debut, fin, remplacement in reversed(remplacements):
        resultat = resultat[:debut] + remplacement + resultat[fin:]

    if len(resultat) != len(bloc):
        raise RuntimeError('Taille du bloc modifiée : remplacement annulé.')

    return resultat

def patch_geometrie_v3(data_root, langue_cible=None):
    """
        Géométrie PC entièrement réglable PAR LANGUE : EN / FR / DE / ES / IT / RU.

        Cette version conserve le nom patch_geometrie_v3() pour ne casser aucun appel.
        Tous les réglages visibles sont regroupés dans `profils` et séparés par menu,
        sous-menu et onglet. Pour modifier une langue, modifier UNIQUEMENT son bloc.

        Sécurité : aucun fichier JAM n'est écrit si sa taille binaire change.
        """
    data_root = Path(data_root)
    pc_root = data_root / 'JamFiles' / 'PC'
    langue = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible if langue_cible is not None else V.LANGUE_CIBLE)
    from importlib import import_module
    if langue in {'en', 'fr', 'de', 'es', 'it', 'ru'}:
        module = import_module(f'LSL_MCL_GEO_LANGUAGES_{langue.upper()}')
        p = getattr(module, f'LSL_MCL_Language_{langue}').geometrie()
    else:
        from LSL_MCL_GEO_LANGUAGES_OTHERS import geometrie
        p = geometrie(langue)
    edition = p['edition']
    styles_globaux = {'TITLE': ('title_x', 'BLANC / ACTIF', 'PItem / Enabled'), 'TITLE_GR': ('title_gr_x', 'GRIS / DESACTIVE', 'PItem / Disabled'), 'TITLE_S': ('title_s_x', 'JAUNE / SURVOL', 'PItem / EnabledArmed')}
    cibles_polices = {'title_x': ('MENUS PItem', 'lignes normales des menus utilisant PItem', 'BLANC'), 'title_gr_x': ('MENUS PItem', 'lignes désactivées des menus utilisant PItem', 'GRIS'), 'title_s_x': ('MENUS PItem', 'lignes sélectionnées des menus utilisant PItem', 'JAUNE'), 'gdef_ws_x': ('CHARGER / SAUVEGARDER', 'lignes normales de la liste de fichiers (LoadItem)', 'BLANC'), 'gdef_s_x': ('CHARGER / SAUVEGARDER', 'lignes sélectionnées et boutons utilisant GDEF_S', 'JAUNE'), 'gdef_w_x': ('CHARGEMENT + SAUVEGARDES', 'chargement et pourcentage ; informations de sauvegarde ; autres textes GDEF_W', 'BLANC'), 'gdef_gy_x': ('OPTIONS + MINI-JEUX', 'valeurs d’options OnOffCC ; résultats de mini-jeux', 'GRIS'), 'gdef_rd_x': ('MINI-JEUX', 'valeurs de résultats avec GDEF_RD', 'ROUGE'), 'gdef_gn_x': ('MINI-JEUX', 'valeurs de résultats avec GDEF_GN', 'VERT'), 'title_rd_x': ('MINI-JEUX', 'titres de résultats avec TITLE_RD', 'ROUGE'), 'title_gn_x': ('MINI-JEUX', 'titres de résultats avec TITLE_GN', 'VERT'), 'title_gy_x': ('MINI-JEUX', 'titres de résultats avec TITLE_GY', 'GRIS'), 'ititle_s_x': ('CHARGER + LIVRE NOIR', 'titre Choisir un fichier et lignes utilisant ITITLE_S', 'JAUNE'), 'ititle_x': ('MENUS ITITLE', 'lignes utilisant ITITLE', 'BLANC'), 'ititle_g_x': ('ACTIF SANS ÉCRAN CONFIRMÉ', 'actif ITITLE_G ; widget non identifié', 'GRIS'), 'desc_wht_x': ('DESCRIPTIONS', 'descriptions utilisant DESC_WHT', 'BLANC'), 'desc_gry_x': ('DESCRIPTIONS', 'descriptions utilisant DESC_GRY', 'GRIS')}
    compteurs = {'PATCH': 0, 'DEJA_OK': 0, 'INTROUVABLE': 0, 'AMBIGU': 0}
    print()
    print('=' * 70)
    print('PATCH GEOMETRIE V3 COMPLETE PAR LANGUE')
    print('Edition :', edition)
    print('Langue  :', langue.upper())
    print('=' * 70)

    def sauver(fichier, original, data):
        """Enregistre les données géométriques modifiées."""
        if data == original:
            return False
        if len(data) != len(original):
            raise RuntimeError(f'[GEOMETRIE SECURITE] {fichier.name} : taille modifiee ({len(original)} -> {len(data)} octets). Ecriture annulee.')
        fichier.write_bytes(data)
        return True

    def encoder_nombre_meme_taille(ancien, cible):
        """Encode un nombre dans exactement le même nombre d'octets."""
        taille = len(ancien)
        for decimales in range(max(0, taille - 2), -1, -1):
            candidat = f'{float(cible):.{decimales}f}'.encode('ascii')
            if len(candidat) <= taille:
                return candidat.ljust(taille, b' ')
        raise RuntimeError(f'Valeur {cible!r} impossible dans {taille} octet(s).')

    def encoder_rectangle(rect):
        """Encode les coordonnées du rectangle au format attendu."""
        return 'Rectangle ' + ' '.join((f'{float(v):.1f}' for v in rect))

    def remplacer_style(data, nom, cible_x, etiquette, cle=None):
        """Modifie un style dans les données géométriques."""
        motif = re.compile(b'(Name\\s+"' + re.escape(nom.encode('ascii')) + b'".{0,600}?\\bScale\\s+)([0-9]+\\.[0-9]+)(\\s+)([0-9]+\\.[0-9]+)', re.DOTALL)
        matches = list(motif.finditer(data))
        if not matches:
            compteurs['INTROUVABLE'] += 1
            print('[INTROUVABLE]', etiquette)
            return data
        if len(matches) > 1:
            compteurs['AMBIGU'] += 1
            print('[AMBIGU]', etiquette, ':', len(matches))
            return data
        m = matches[0]
        nouvelle_x = encoder_nombre_meme_taille(m.group(2), cible_x)
        if m.group(2).strip() == nouvelle_x.strip():
            compteurs['DEJA_OK'] += 1
            return data
        remplacement = m.group(1) + nouvelle_x + m.group(3) + m.group(4)
        compteurs['PATCH'] += 1
        if cle:
            ecran, element, couleur = cibles_polices.get(cle, ('ACTIF SANS ÉCRAN CONFIRMÉ', f'actif {nom} ; widget non identifié', 'ÉTAT NON CONFIRMÉ'))
            print(f'[GEOMETRIE {langue.upper()} TAILLE TEXTE > {ecran}] {element} | {couleur} | {cle} | AppInit.JAM/Global/{nom} | horizontal : {m.group(2).decode().strip()} -> {nouvelle_x.decode().strip()}')
        else:
            print('[TAILLE TEXTE]', etiquette, '| horizontal :', m.group(2).decode().strip(), '->', nouvelle_x.decode().strip())
        return data[:m.start()] + remplacement + data[m.end():]

    def bloc_namespace(data, namespace):
        """
            Retourne toute la zone logique d'un NameSpace JAM.

            IMPORTANT :
            Un même NameSpace peut être déclaré plusieurs fois de suite dans
            un fichier JAM pour séparer ses ImageAssets, Styles, Widgets, etc.

            Exemple réel dans IntrFram.JAM :
                NameSpace "Intro"   -> ImageAssets
                NameSpace "Intro"   -> Style
                NameSpace "Intro"   -> Widgets

            L'ancienne version s'arrêtait au NameSpace suivant, même lorsque
            celui-ci portait exactement le même nom. Elle ne voyait donc pas
            les objets MenuLst, MenuNew, MenuLoad, MenuExit et MenuStrt.

            Cette version regroupe toutes les déclarations CONSECUTIVES du même
            NameSpace et s'arrête seulement lorsqu'un NameSpace différent commence.
            """
        marqueur = ('NameSpace "' + namespace + '"').encode('latin-1')
        debut = data.find(marqueur)
        if debut < 0:
            return None
        position = debut + len(marqueur)
        while True:
            suivant = data.find(b'NameSpace "', position)
            if suivant < 0:
                return (debut, len(data))
            debut_nom = suivant + len(b'NameSpace "')
            fin_nom = data.find(b'"', debut_nom)
            if fin_nom < 0:
                return (debut, len(data))
            nom_suivant = data[debut_nom:fin_nom].decode('latin-1', errors='replace')
            if nom_suivant.lower() == namespace.lower():
                position = fin_nom + 1
                continue
            return (debut, suivant)

    def blocs_objets_namespace(data, namespace):
        """
            Cartographie les objets réels d'un NameSpace JAM.

            Retour :
                type  = Widget / ListBox / StateBtn / etc.
                name  = nom technique exact
                debut = offset début de l'objet
                fin   = offset fin de l'objet
            """
        limites = bloc_namespace(data, namespace)
        if limites is None:
            return []
        debut_ns, fin_ns = limites
        bloc = data[debut_ns:fin_ns]
        motif = re.compile(
            rb'"([^"\r\n]+)"\s+"([^"\r\n]+)"'
            rb'(?:\s|//[^\r\n]*(?:\r?\n|$))*\{'
        )
        objets = []
        for match in motif.finditer(bloc):
            type_objet = match.group(1).decode('latin1', errors='replace')
            nom_objet = match.group(2).decode('latin1', errors='replace')
            ouverture = bloc.find(b'{', match.start(), match.end())
            if ouverture < 0:
                continue
            profondeur = 0
            fermeture = None
            for position in range(ouverture, len(bloc)):
                if bloc[position] == 123:
                    profondeur += 1
                elif bloc[position] == 125:
                    profondeur -= 1
                    if profondeur == 0:
                        fermeture = position + 1
                        break
            if fermeture is None:
                continue
            objets.append({'type': type_objet, 'name': nom_objet, 'debut': debut_ns + match.start(), 'fin': debut_ns + fermeture})
        return objets
    objets_affiches = set()

    def afficher_patch_rectangle(etiquette, quantite, ancien, nouveau, objets):
        """Affiche la cible une fois et une ligne courte par JAM modifié."""
        fichier, cle = etiquette.split(' / ', 1)
        cle = cle.removeprefix(f'{langue.upper()} ')
        noms = ', '.join((f"{o['type']}/{o['name']}" for o in objets))
        if cle not in objets_affiches and noms:
            print(f'[GEOMETRIE {langue.upper()} OBJETS > {cle}] {noms}')
            objets_affiches.add(cle)
        valeurs_apres = nouveau.decode('ascii').removeprefix('Rectangle ')
        print(f"[GEOMETRIE {langue.upper()} PATCH {fichier}] > ({cle} x {quantite}) {ancien.decode('ascii')} -> {valeurs_apres}")

    def remplacer_rectangle_namespace(data, namespace, ancien_rect, nouveau_rect, attendu, etiquette, nom_objet=None, type_objet=None):
        """
            Moteur V3 solide.

            Priorité :
                fichier -> NameSpace -> Type -> Name -> Rectangle.

            Une règle sans Name reste compatible, mais le moteur travaille
            maintenant objet par objet. Si plusieurs objets sont possibles pour
            une cible unique, il REFUSE de choisir au hasard.
            """
        limites = bloc_namespace(data, namespace)
        if limites is None:
            compteurs['INTROUVABLE'] += 1
            print('[INTROUVABLE]', etiquette, '- namespace', namespace)
            return data
        ancien = encoder_rectangle(ancien_rect).encode('ascii')
        nouveau_txt = encoder_rectangle(nouveau_rect).encode('ascii')

        nouveau = nouveau_txt.ljust(len(ancien), b' ')
        objets = blocs_objets_namespace(data, namespace)
        if nom_objet is not None:
            candidats = [objet for objet in objets if objet['name'].lower() == nom_objet.lower() and (type_objet is None or objet['type'].lower() == type_objet.lower())]
            if len(candidats) != 1:
                compteurs['INTROUVABLE'] += 1
                print('[INTROUVABLE OBJET]', etiquette, '| namespace =', namespace, '| type =', type_objet or '*', '| name =', nom_objet, '| trouve =', len(candidats))
                return data
            objet = candidats[0]
            bloc = data[objet['debut']:objet['fin']]
            nb_old = bloc.count(ancien)
            nb_new = bloc.count(nouveau)
            if ancien_rect == nouveau_rect or (nb_old == 0 and nb_new >= attendu):
                compteurs['DEJA_OK'] += 1
                return data
            if nb_old != attendu:
                compteurs['INTROUVABLE'] += 1
                print('[INTROUVABLE RECTANGLE]', etiquette, '| objet =', f"{objet['type']}/{objet['name']}", '| attendu =', attendu, '| trouve =', nb_old)
                return data
            bloc = remplacer_rectangle_bloc(
                bloc, ancien, nouveau_txt, attendu
            )
            data = data[:objet['debut']] + bloc + data[objet['fin']:]
            compteurs['PATCH'] += attendu
            afficher_patch_rectangle(etiquette, attendu, ancien, nouveau_txt, [objet])
            return data
        candidats_old = []
        candidats_new = []
        for objet in objets:
            if type_objet is not None and objet['type'].lower() != type_objet.lower():
                continue
            bloc = data[objet['debut']:objet['fin']]
            if ancien in bloc:
                candidats_old.append(objet)
            if nouveau in bloc:
                candidats_new.append(objet)
        if ancien_rect == nouveau_rect or (not candidats_old and len(candidats_new) >= attendu):
            compteurs['DEJA_OK'] += 1
            return data
        if len(candidats_old) < attendu:
            compteurs['INTROUVABLE'] += 1
            print('[INTROUVABLE]', etiquette, '| namespace =', namespace, '| attendu =', attendu, '| objets trouves =', len(candidats_old))
            return data
        if attendu == 1 and len(candidats_old) != 1:
            compteurs['AMBIGU'] += 1
            print('[AMBIGU]', etiquette, '| namespace =', namespace, '| Rectangle partagé par', len(candidats_old), 'objets')
            print('    [CANDIDATS]', ', '.join((f"{x['type']}/{x['name']}" for x in candidats_old)))
            return data
        cibles = candidats_old[:attendu]
        for objet in sorted(cibles, key=lambda x: x['debut'], reverse=True):
            bloc = data[objet['debut']:objet['fin']]
            bloc = remplacer_rectangle_bloc(
                bloc, ancien, nouveau_txt, 1
            )
            data = data[:objet['debut']] + bloc + data[objet['fin']:]
        compteurs['PATCH'] += len(cibles)
        afficher_patch_rectangle(etiquette, len(cibles), ancien, nouveau_txt, cibles if len(cibles) <= 8 else [])
        return data

    def lire_cible_rectangle(cible):
        """
            Compatibilité avec les anciens nommages.

            Ancien :
                (fichier, namespace, rectangle, attendu)

            Solide :
                (fichier, namespace, rectangle, attendu, name, type)
            """
        return (cible[0], cible[1], cible[2], cible[3], cible[4] if len(cible) >= 5 else None, cible[5] if len(cible) >= 6 else None)
    CIBLES_RECTANGLES = {
            'menu_principal_rectangle': ('IntrFram.JAM', 'Intro', (201.0, 250.0, 421.0, 355.0), 1, 'MenuLst', 'ListBox'),
            'menu_principal_nouvelle_partie_rectangle': ('IntrFram.JAM', 'Intro', (0.0, 0.0, 220.0, 35.0), 1, 'MenuNew', 'Widget'),
            'menu_principal_charger_rectangle': ('IntrFram.JAM', 'Intro', (0.0, 0.0, 220.0, 35.0), 1, 'MenuLoad', 'Widget'),
            'menu_principal_quitter_rectangle': ('IntrFram.JAM', 'Intro', (0.0, 0.0, 220.0, 35.0), 1, 'MenuExit', 'Widget'),
            'menu_principal_texte_demarrer_rectangle': ('IntrFram.JAM', 'Intro', (84.0, 285.0, 576.0, 320.0), 1, 'MenuStrt', 'Widget'),
            'menu_pause_ecran_rectangle': ('AppInit.JAM', 'PausMenu', (160.0, 101.0, 480.0, 379.0), 1, 'PauseSc', 'Widget'),
            'menu_pause_liste_rectangle': ('AppInit.JAM', 'PausMenu', (50.0, 32.0, 270.0, 243.0), 1, 'PauseLst', 'ListBox'),
            'menu_pause_bouton_1_rectangle': ('AppInit.JAM', 'PausMenu', (0.0, 0.0, 220.0, 35.0), 1, 'PauItm01', 'Widget'),
            'menu_pause_bouton_2_rectangle': ('AppInit.JAM', 'PausMenu', (0.0, 0.0, 220.0, 35.0), 1, 'PauItm02', 'Widget'),
            'menu_pause_bouton_3_rectangle': ('AppInit.JAM', 'PausMenu', (0.0, 0.0, 220.0, 35.0), 1, 'PauItm03', 'Widget'),
            'menu_pause_bouton_4_rectangle': ('AppInit.JAM', 'PausMenu', (0.0, 0.0, 220.0, 35.0), 1, 'PauItm04', 'Widget'),
            'menu_pause_bouton_5_rectangle': ('AppInit.JAM', 'PausMenu', (0.0, 0.0, 220.0, 35.0), 1, 'PauItm05', 'Widget'),
            'menu_pause_bouton_6_rectangle': ('AppInit.JAM', 'PausMenu', (0.0, 0.0, 220.0, 35.0), 1, 'PauItm06', 'Widget'),
            'menu_pause_aide_haut_bas_rectangle': ('AppInit.JAM', 'PausMenu', (-80.0, 288.0, 86.0, 318.0), 1),
            'menu_pause_aide_retour_rectangle': ('AppInit.JAM', 'PausMenu', (87.0, 288.0, 233.0, 318.0), 1),
            'menu_pause_aide_selection_rectangle': ('AppInit.JAM', 'PausMenu', (234.0, 288.0, 400.0, 318.0), 1),
            'livre_noir_fond_rectangle': ('Levels/*.JAM', 'BBook', (64.0, 63.0, 576.0, 407.0), 1),
            'onglet_quete_inactif_rectangle': ('Levels/*.JAM', 'BBook', (55.0, -29.0, 83.0, 2.0), 1),
            'onglet_filles_inactif_rectangle': ('Levels/*.JAM', 'BBook', (87.0, -29.0, 115.0, 2.0), 1),
            'onglet_tenue_inactif_rectangle': ('Levels/*.JAM', 'BBook', (118.0, -29.0, 146.0, 2.0), 1),
            'onglet_objet_inactif_rectangle': ('Levels/*.JAM', 'BBook', (148.0, -29.0, 176.0, 2.0), 1),
            'onglet_stats_inactif_rectangle': ('Levels/*.JAM', 'BBook', (180.0, -29.0, 208.0, 2.0), 1),
            'quete_titre_rectangle': ('Levels/*.JAM', 'Quests', (280.0, -40.0, 460.0, 10.0), 1),
            'quete_titre_icone_rectangle': ('Levels/*.JAM', 'Quests', (470.0, -31.0, 502.0, 1.0), 1),
            'fille_titre_rectangle': ('Levels/*.JAM', 'GirlDetl', (280.0, -40.0, 460.0, 10.0), 1),
            'fille_titre_icone_rectangle': ('Levels/*.JAM', 'GirlDetl', (470.0, -31.0, 502.0, 1.0), 1),
            'tenue_titre_rectangle': ('Levels/*.JAM', 'Costume', (280.0, -40.0, 460.0, 10.0), 1),
            'tenue_titre_icone_rectangle': ('Levels/*.JAM', 'Costume', (470.0, -31.0, 502.0, 1.0), 1),
            'objet_titre_rectangle': ('Levels/*.JAM', 'Invntory', (280.0, -40.0, 460.0, 10.0), 1),
            'objet_titre_icone_rectangle': ('Levels/*.JAM', 'Invntory', (470.0, -31.0, 502.0, 1.0), 1),
            'stats_titre_rectangle': ('Levels/*.JAM', 'Stats', (280.0, -40.0, 460.0, 10.0), 1),
            'stats_titre_icone_rectangle': ('Levels/*.JAM', 'Stats', (470.0, -31.0, 502.0, 1.0), 1),
            'livre_noir_item_rectangle': ('Levels/*.JAM', 'BBook', (0.0, 0.0, 234.0, 28.0), 160),
            'livre_noir_item_icone_rectangle': ('Levels/*.JAM', 'BBook', (0.0, 4.0, 20.0, 24.0), 1),
            'livre_noir_item_texte_marge_rectangle': ('Levels/*.JAM', 'BBook', (25.0, 0.0, 25.0, 0.0), 1),
            'quete_onglet_actif_rectangle': ('Levels/*.JAM', 'Quests', (38.0, -29.0, 101.0, 2.0), 1),
            'quete_liste_rectangle': ('Levels/*.JAM', 'Quests', (38.0, 32.0, 272.0, 286.0), 1),
            'quete_description_rectangle': ('Levels/*.JAM', 'Quests', (261.0, 75.0, 482.0, 350.0), 1),
            'quete_sous_titre_rectangle': ('Levels/*.JAM', 'Quests', (280.0, 25.0, 460.0, 65.0), 1),
            'quete_scroll_haut_rectangle': ('Levels/*.JAM', 'Quests', (16.0, 52.0, 36.0, 72.0), 1),
            'quete_scroll_bas_rectangle': ('Levels/*.JAM', 'Quests', (16.0, 250.0, 36.0, 271.0), 1),
            'quete_aide_page_rectangle': ('Levels/*.JAM', 'Quests', (0.0, 353.0, 170.0, 385.0), 1),
            'quete_aide_haut_bas_rectangle': ('Levels/*.JAM', 'Quests', (171.0, 353.0, 340.0, 385.0), 1),
            'quete_aide_retour_rectangle': ('Levels/*.JAM', 'Quests', (341.0, 353.0, 512.0, 385.0), 1),
            'fille_onglet_actif_rectangle': ('Levels/*.JAM', 'GirlDetl', (70.0, -29.0, 133.0, 2.0), 1),
            'fille_liste_rectangle': ('Levels/*.JAM', 'GirlDetl', (38.0, 32.0, 272.0, 286.0), 1),
            'fille_image_principale_rectangle': ('Levels/*.JAM', 'GirlDetl', (311.0, 22.0, 439.0, 150.0), 1),
            'fille_texte_milieu_rectangle': ('Levels/*.JAM', 'GirlDetl', (311.0, 175.0, 439.0, 205.0), 1),
            'fille_icone_rectangle': ('Levels/*.JAM', 'GirlDetl', (343.0, 210.0, 407.0, 274.0), 1),
            'fille_token_texte_rectangle': ('Levels/*.JAM', 'GirlDetl', (311.0, 285.0, 439.0, 315.0), 1),
            'fille_scroll_haut_rectangle': ('Levels/*.JAM', 'GirlDetl', (16.0, 52.0, 36.0, 72.0), 1),
            'fille_scroll_bas_rectangle': ('Levels/*.JAM', 'GirlDetl', (16.0, 250.0, 36.0, 271.0), 1),
            'fille_aide_page_rectangle': ('Levels/*.JAM', 'GirlDetl', (0.0, 353.0, 123.0, 385.0), 1),
            'fille_aide_haut_bas_rectangle': ('Levels/*.JAM', 'GirlDetl', (124.0, 353.0, 251.0, 385.0), 1),
            'fille_aide_selection_rectangle': ('Levels/*.JAM', 'GirlDetl', (252.0, 353.0, 390.0, 385.0), 1),
            'fille_aide_retour_rectangle': ('Levels/*.JAM', 'GirlDetl', (391.0, 353.0, 507.0, 385.0), 1),
            'fille_historique_fond_rectangle': ('Levels/*.JAM', 'GirlHist', (48.0, 36.0, 592.0, 377.0), 1),
            'fille_historique_titre_rectangle': ('Levels/*.JAM', 'GirlHist', (335.0, 90.0, 463.0, 110.0), 1),
            'fille_historique_image_rectangle': ('Levels/*.JAM', 'GirlHist', (335.0, 120.0, 463.0, 248.0), 1),
            'fille_historique_liste_titre_rectangle': ('Levels/*.JAM', 'GirlHist', (38.0, 30.0, 272.0, 55.0), 1),
            'fille_historique_liste_rectangle': ('Levels/*.JAM', 'GirlHist', (38.0, 70.0, 272.0, 295.0), 1),
            'fille_historique_scroll_haut_rectangle': ('Levels/*.JAM', 'GirlHist', (16.0, 90.0, 36.0, 110.0), 1),
            'fille_historique_scroll_bas_rectangle': ('Levels/*.JAM', 'GirlHist', (16.0, 260.0, 36.0, 280.0), 1),
            'tenue_onglet_actif_rectangle': ('Levels/*.JAM', 'Costume', (101.0, -29.0, 164.0, 2.0), 1),
            'tenue_liste_rectangle': ('Levels/*.JAM', 'Costume', (38.0, 32.0, 272.0, 286.0), 1),
            'tenue_sous_titre_rectangle': ('Levels/*.JAM', 'Costume', (291.0, 247.0, 495.0, 262.0), 1),
            'tenue_accessoire_1_rectangle': ('Levels/*.JAM', 'Costume', (291.0, 262.0, 336.0, 314.0), 1),
            'tenue_accessoire_2_rectangle': ('Levels/*.JAM', 'Costume', (344.0, 262.0, 389.0, 314.0), 1),
            'tenue_accessoire_3_rectangle': ('Levels/*.JAM', 'Costume', (397.0, 262.0, 442.0, 314.0), 1),
            'tenue_accessoire_4_rectangle': ('Levels/*.JAM', 'Costume', (450.0, 262.0, 495.0, 314.0), 1),
            'tenue_scroll_haut_rectangle': ('Levels/*.JAM', 'Costume', (16.0, 52.0, 36.0, 72.0), 1),
            'tenue_scroll_bas_rectangle': ('Levels/*.JAM', 'Costume', (16.0, 250.0, 36.0, 271.0), 1),
            'tenue_aide_page_rectangle': ('Levels/*.JAM', 'Costume', (0.0, 353.0, 170.0, 385.0), 1, 'HlpLtRt', 'Widget'),
            'tenue_aide_haut_bas_rectangle': ('Levels/*.JAM', 'Costume', (171.0, 353.0, 340.0, 385.0), 1, 'HlpUpDn', 'Widget'),
            'tenue_aide_retour_rectangle': ('Levels/*.JAM', 'Costume', (341.0, 353.0, 512.0, 385.0), 1, 'HlpExit', 'Widget'),
            'objet_onglet_actif_rectangle': ('Levels/*.JAM', 'Invntory', (131.0, -29.0, 194.0, 2.0), 1),
            'objet_liste_rectangle': ('Levels/*.JAM', 'Invntory', (38.0, 32.0, 272.0, 286.0), 1),
            'objet_image_rectangle': ('Levels/*.JAM', 'Invntory', (343.0, 54.0, 407.0, 118.0), 1),
            'objet_description_rectangle': ('Levels/*.JAM', 'Invntory', (280.0, 130.0, 460.0, 400.0), 1),
            'objet_scroll_haut_rectangle': ('Levels/*.JAM', 'Invntory', (16.0, 52.0, 36.0, 72.0), 1),
            'objet_scroll_bas_rectangle': ('Levels/*.JAM', 'Invntory', (16.0, 250.0, 36.0, 271.0), 1),
            'objet_aide_page_rectangle': ('Levels/*.JAM', 'Invntory', (0.0, 353.0, 123.0, 385.0), 1),
            'objet_aide_haut_bas_rectangle': ('Levels/*.JAM', 'Invntory', (124.0, 353.0, 251.0, 385.0), 1),
            'objet_aide_detail_rectangle': ('Levels/*.JAM', 'Invntory', (252.0, 353.0, 390.0, 385.0), 1),
            'objet_aide_retour_rectangle': ('Levels/*.JAM', 'Invntory', (391.0, 353.0, 507.0, 385.0), 1),
            'stats_onglet_actif_rectangle': ('Levels/*.JAM', 'Stats', (163.0, -29.0, 226.0, 2.0), 1),
            'stats_liste_gauche_rectangle': ('Levels/*.JAM', 'Stats', (38.0, 32.0, 272.0, 285.0), 1),
            'stats_item_gauche_rectangle': ('Levels/*.JAM', 'Stats', (0.0, 0.0, 234.0, 28.0), 1),
            'stats_liste_droite_rectangle': ('Levels/*.JAM', 'Stats', (270.0, 32.0, 490.0, 286.0), 1),
            'stats_item_droite_rectangle': ('Levels/*.JAM', 'Stats', (0.0, 0.0, 220.0, 24.0), 1),
            'stats_scroll_haut_rectangle': ('Levels/*.JAM', 'Stats', (16.0, 52.0, 36.0, 72.0), 1),
            'stats_scroll_bas_rectangle': ('Levels/*.JAM', 'Stats', (16.0, 250.0, 36.0, 271.0), 1),
            'stats_aide_page_rectangle': ('Levels/*.JAM', 'Stats', (0.0, 353.0, 170.0, 385.0), 1),
            'stats_aide_haut_bas_rectangle': ('Levels/*.JAM', 'Stats', (171.0, 353.0, 340.0, 385.0), 1),
            'stats_aide_retour_rectangle': ('Levels/*.JAM', 'Stats', (341.0, 353.0, 512.0, 385.0), 1),
            'option_ecran_rectangle': ('AppInit.JAM', 'Options', (128.0, 92.0, 512.0, 316.0), 1),
            'option_liste_rectangle': ('AppInit.JAM', 'Options', (-32.0, 32.0, 416.0, 206.0), 1),
            'option_item_rectangle': ('AppInit.JAM', 'Options', (0.0, 0.0, 448.0, 40.0), 4),
            'option_aide_haut_bas_rectangle': ('AppInit.JAM', 'Options', (-30.0, 234.0, 118.0, 264.0), 1),
            'option_aide_retour_rectangle': ('AppInit.JAM', 'Options', (119.0, 234.0, 266.0, 264.0), 1),
            'option_aide_selection_rectangle': ('AppInit.JAM', 'Options', (267.0, 234.0, 414.0, 264.0), 1),
            'audio_ecran_rectangle': ('AppInit.JAM', 'Audio', (130.0, 92.0, 510.0, 313.0), 1),
            'audio_liste_rectangle': ('AppInit.JAM', 'Audio', (30.0, 50.0, 150.0, 171.0), 1),
            'audio_item_rectangle': ('AppInit.JAM', 'Audio', (0.0, 0.0, 120.0, 40.0), 3),
            'audio_fleche_gauche_1_rectangle': ('AppInit.JAM', 'Audio', (165.0, 63.0, 181.0, 79.0), 1),
            'audio_fleche_gauche_2_rectangle': ('AppInit.JAM', 'Audio', (165.0, 103.0, 181.0, 119.0), 1),
            'audio_fleche_gauche_3_rectangle': ('AppInit.JAM', 'Audio', (165.0, 143.0, 181.0, 159.0), 1),
            'audio_fleche_droite_1_rectangle': ('AppInit.JAM', 'Audio', (329.0, 63.0, 345.0, 79.0), 1),
            'audio_fleche_droite_2_rectangle': ('AppInit.JAM', 'Audio', (329.0, 103.0, 345.0, 119.0), 1),
            'audio_fleche_droite_3_rectangle': ('AppInit.JAM', 'Audio', (329.0, 143.0, 345.0, 159.0), 1),
            'audio_aide_gauche_droite_rectangle': ('AppInit.JAM', 'Audio', (-86.0, 231.0, 190.0, 261.0), 1),
            'audio_aide_retour_rectangle': ('AppInit.JAM', 'Audio', (191.0, 231.0, 319.0, 261.0), 1),
            'audio_aide_selection_rectangle': ('AppInit.JAM', 'Audio', (320.0, 231.0, 468.0, 261.0), 1),
            'controleur_ecran_rectangle': ('AppInit.JAM', 'Cntrller', (48.0, 132.0, 592.0, 328.0), 1),
            'controleur_liste_rectangle': ('AppInit.JAM', 'Cntrller', (105.0, 70.0, 245.0, 154.0), 1),
            'controleur_item_rectangle': ('AppInit.JAM', 'Cntrller', (0.0, 0.0, 140.0, 28.0), 3),
            'controleur_aide_haut_bas_rectangle': ('AppInit.JAM', 'Cntrller', (0.0, 206.0, 136.0, 236.0), 1),
            'controleur_aide_cycle_rectangle': ('AppInit.JAM', 'Cntrller', (137.0, 206.0, 273.0, 236.0), 1),
            'controleur_aide_retour_rectangle': ('AppInit.JAM', 'Cntrller', (274.0, 206.0, 409.0, 236.0), 1),
            'controleur_aide_selection_rectangle': ('AppInit.JAM', 'Cntrller', (410.0, 206.0, 545.0, 236.0), 1),
            'vibration_ecran_rectangle': ('AppInit.JAM', 'Rumble', (130.0, 92.0, 510.0, 233.0), 1),
            'vibration_liste_rectangle': ('AppInit.JAM', 'Rumble', (30.0, 60.0, 150.0, 101.0), 1),
            'vibration_item_rectangle': ('AppInit.JAM', 'Rumble', (0.0, 0.0, 120.0, 40.0), 1),
            'vibration_fleche_gauche_rectangle': ('AppInit.JAM', 'Rumble', (165.0, 73.0, 181.0, 89.0), 1),
            'vibration_fleche_droite_rectangle': ('AppInit.JAM', 'Rumble', (329.0, 73.0, 345.0, 89.0), 1),
            'vibration_aide_gauche_droite_rectangle': ('AppInit.JAM', 'Rumble', (-30.0, 151.0, 116.0, 181.0), 1),
            'vibration_aide_retour_rectangle': ('AppInit.JAM', 'Rumble', (117.0, 151.0, 264.0, 181.0), 1),
            'vibration_aide_selection_rectangle': ('AppInit.JAM', 'Rumble', (265.0, 151.0, 410.0, 181.0), 1),
            'difficulte_ecran_rectangle': ('AppInit.JAM', 'Diffclty', (130.0, 92.0, 510.0, 233.0), 1),
            'difficulte_liste_rectangle': ('AppInit.JAM', 'Diffclty', (30.0, 60.0, 150.0, 101.0), 1),
            'difficulte_item_rectangle': ('AppInit.JAM', 'Diffclty', (0.0, 0.0, 120.0, 40.0), 1),
            'difficulte_fleche_gauche_rectangle': ('AppInit.JAM', 'Diffclty', (165.0, 73.0, 181.0, 89.0), 1),
            'difficulte_fleche_droite_rectangle': ('AppInit.JAM', 'Diffclty', (329.0, 73.0, 345.0, 89.0), 1),
            'difficulte_aide_gauche_droite_rectangle': ('AppInit.JAM', 'Diffclty', (-30.0, 151.0, 116.0, 181.0), 1),
            'difficulte_aide_retour_rectangle': ('AppInit.JAM', 'Diffclty', (117.0, 151.0, 264.0, 181.0), 1),
            'difficulte_aide_selection_rectangle': ('AppInit.JAM', 'Diffclty', (265.0, 151.0, 410.0, 181.0), 1),
            'photo_menu_ecran_rectangle': ('AppInit.JAM', 'PhotoOpt', (128.0, 128.0, 512.0, 272.0), 1),
            'photo_menu_liste_rectangle': ('AppInit.JAM', 'PhotoOpt', (-32.0, 32.0, 416.0, 128.0), 1),
            'photo_menu_item_rectangle': ('AppInit.JAM', 'PhotoOpt', (0.0, 0.0, 448.0, 40.0), 2),
            'photo_menu_aide_haut_bas_rectangle': ('AppInit.JAM', 'PhotoOpt', (-20.0, 154.0, 128.0, 184.0), 1),
            'photo_menu_aide_retour_rectangle': ('AppInit.JAM', 'PhotoOpt', (129.0, 154.0, 256.0, 184.0), 1),
            'photo_menu_aide_selection_rectangle': ('AppInit.JAM', 'PhotoOpt', (257.0, 154.0, 404.0, 184.0), 1),
            'photo_album_ecran_rectangle': ('AppInit.JAM', 'PhotoAlb', (64.0, 64.0, 576.0, 384.0), 1),
            'photo_album_titre_rectangle': ('AppInit.JAM', 'PhotoAlb', (52.0, 43.0, 466.0, 73.0), 1),
            'photo_album_scroll_gauche_rectangle': ('AppInit.JAM', 'PhotoAlb', (22.0, 30.0, 38.0, 46.0), 1),
            'photo_album_scroll_droite_rectangle': ('AppInit.JAM', 'PhotoAlb', (475.0, 30.0, 491.0, 46.0), 1),
            'photo_album_scroll_haut_rectangle': ('AppInit.JAM', 'PhotoAlb', (30.0, 78.0, 46.0, 94.0), 1),
            'photo_album_scroll_bas_rectangle': ('AppInit.JAM', 'PhotoAlb', (30.0, 232.0, 46.0, 248.0), 1),
            'photo_album_photo_1_rectangle': ('AppInit.JAM', 'PhotoAlb', (72.0, 68.0, 190.0, 158.0), 1),
            'photo_album_photo_2_rectangle': ('AppInit.JAM', 'PhotoAlb', (200.0, 68.0, 318.0, 158.0), 1),
            'photo_album_photo_3_rectangle': ('AppInit.JAM', 'PhotoAlb', (328.0, 68.0, 446.0, 158.0), 1),
            'photo_album_photo_4_rectangle': ('AppInit.JAM', 'PhotoAlb', (72.0, 168.0, 190.0, 258.0), 1),
            'photo_album_photo_5_rectangle': ('AppInit.JAM', 'PhotoAlb', (200.0, 168.0, 318.0, 258.0), 1),
            'photo_album_photo_6_rectangle': ('AppInit.JAM', 'PhotoAlb', (328.0, 168.0, 446.0, 258.0), 1),
            'photo_album_aide_navigation_rectangle': ('AppInit.JAM', 'PhotoAlb', (32.0, 330.0, 190.0, 360.0), 1),
            'photo_album_aide_zoom_rectangle': ('AppInit.JAM', 'PhotoAlb', (201.0, 330.0, 318.0, 360.0), 1),
            'photo_album_aide_retour_rectangle': ('AppInit.JAM', 'PhotoAlb', (318.0, 330.0, 447.0, 360.0), 1),
            'extra_ecran_rectangle': ('AppInit.JAM', 'Extras', (64.0, 128.0, 576.0, 352.0), 1),
            'extra_liste_rectangle': ('AppInit.JAM', 'Extras', (32.0, 32.0, 480.0, 195.0), 1),
            'extra_item_rectangle': ('AppInit.JAM', 'Extras', (0.0, 0.0, 448.0, 40.0), 4),
            'extra_aide_haut_bas_rectangle': ('AppInit.JAM', 'Extras', (0.0, 236.0, 170.0, 264.0), 1),
            'extra_aide_retour_rectangle': ('AppInit.JAM', 'Extras', (171.0, 236.0, 340.0, 264.0), 1),
            'extra_aide_selection_rectangle': ('AppInit.JAM', 'Extras', (341.0, 236.0, 512.0, 264.0), 1),
            'bonus_ecran_rectangle': ('AppInit.JAM', 'BonusOpt', (110.0, 72.0, 530.0, 253.0), 1),
            'bonus_liste_rectangle': ('AppInit.JAM', 'BonusOpt', (30.0, 60.0, 190.0, 141.0), 1),
            'bonus_item_rectangle': ('AppInit.JAM', 'BonusOpt', (0.0, 0.0, 160.0, 40.0), 2),
            'bonus_aide_gauche_droite_rectangle': ('AppInit.JAM', 'BonusOpt', (0.0, 191.0, 140.0, 221.0), 1),
            'bonus_aide_retour_rectangle': ('AppInit.JAM', 'BonusOpt', (141.0, 191.0, 280.0, 221.0), 1),
            'bonus_aide_selection_rectangle': ('AppInit.JAM', 'BonusOpt', (281.0, 191.0, 420.0, 221.0), 1),
            'sauvegarde_ecran_rectangle': ('AppInit.JAM', 'LoadGame', (64.0, 79.0, 576.0, 401.0), 1),
            'sauvegarde_liste_rectangle': ('AppInit.JAM', 'LoadGame', (55.0, 113.0, 457.0, 281.0), 1),
            'sauvegarde_fleche_gauche_rectangle': ('AppInit.JAM', 'LoadGame', (23.0, 30.0, 55.0, 62.0), 1),
            'sauvegarde_fleche_droite_rectangle': ('AppInit.JAM', 'LoadGame', (457.0, 30.0, 489.0, 62.0), 1),
            'sauvegarde_fleche_haut_rectangle': ('AppInit.JAM', 'LoadGame', (31.0, 121.0, 46.0, 137.0), 1),
            'sauvegarde_fleche_bas_rectangle': ('AppInit.JAM', 'LoadGame', (31.0, 257.0, 46.0, 273.0), 1),
            'sauvegarde_info_rectangle': ('AppInit.JAM', 'LoadGame', (-42.0, 50.0, 554.0, 70.0), 1),
            'sauvegarde_espace_libre_rectangle': ('AppInit.JAM', 'LoadGame', (50.0, 281.0, 346.0, 309.0), 1),
            'sauvegarde_bouton_sauver_rectangle': ('AppInit.JAM', 'LoadGame', (0.0, 332.0, 170.0, 362.0), 1),
            'sauvegarde_bouton_supprimer_rectangle': ('AppInit.JAM', 'LoadGame', (171.0, 332.0, 384.0, 362.0), 1),
            'sauvegarde_bouton_annuler_rectangle': ('AppInit.JAM', 'LoadGame', (385.0, 332.0, 512.0, 362.0), 1),
        }

    app = pc_root / 'AppInit.JAM'
    if app.exists():
        original = app.read_bytes()
        data = original
        for nom, cle in (('TITLE', 'title_x'), ('TITLE_GR', 'title_gr_x'), ('TITLE_S', 'title_s_x'), ('STITLE', 'stitle_x'), ('STITLE_S', 'stitle_s_x'), ('STITLE_G', 'stitle_g_x'), ('STITLESM', 'stitlesm_x'), ('ITITLE', 'ititle_x'), ('ITITLE_S', 'ititle_s_x'), ('ITITLE_G', 'ititle_g_x'), ('GDEF_W', 'gdef_w_x'), ('GDEF_S', 'gdef_s_x'), ('GDEF_GY', 'gdef_gy_x'), ('DESC_WHT', 'desc_wht_x'), ('DESC_GRY', 'desc_gry_x')):
            detail = styles_globaux.get(nom)
            etiquette = f'{langue.upper()} / AppInit.JAM / Global / {nom}' + (f' / {detail[1]} / {detail[2]} / partage par tous les menus' if detail else ' / style global partage')
            data = remplacer_style(data, nom, p[cle], etiquette, cle)
        for nom, cle in (('GDEF_WS', 'gdef_ws_x'), ('GDEF_WSB', 'gdef_wsb_x'), ('GDEF_WSC', 'gdef_wsc_x'), ('GDEF_WSM', 'gdef_wsm_x'), ('GDEF_RD', 'gdef_rd_x'), ('GDEF_GN', 'gdef_gn_x'), ('TITLE_RD', 'title_rd_x'), ('TITLE_GN', 'title_gn_x'), ('TITLE_GY', 'title_gy_x')):
            data = remplacer_style(data, nom, p[cle], f'{langue.upper()} / AppInit.JAM / Global / {nom} / clé {cle}', cle)
        for cle, cible in CIBLES_RECTANGLES.items():
            scope, ns, ancien, attendu, nom_objet, type_objet = lire_cible_rectangle(cible)
            if scope.lower() == 'appinit.jam':
                data = remplacer_rectangle_namespace(data, ns, ancien, p[cle], attendu, f'{app.name} / {langue.upper()} {cle}', nom_objet, type_objet)
        sauver(app, original, data)
    else:
        print('[INTROUVABLE] AppInit.JAM')
    intr = pc_root / 'IntrFram.JAM'
    if intr.exists():
        original = intr.read_bytes()
        data = original
        for cle, cible in CIBLES_RECTANGLES.items():
            scope, ns, ancien, attendu, nom_objet, type_objet = lire_cible_rectangle(cible)
            if scope.lower() == 'intrfram.jam':
                data = remplacer_rectangle_namespace(data, ns, ancien, p[cle], attendu, f'{intr.name} / {langue.upper()} {cle}', nom_objet, type_objet)
        sauver(intr, original, data)
    else:
        print('[INTROUVABLE] IntrFram.JAM')
    levels = pc_root / 'Levels'
    if levels.exists():
        for fichier in sorted(p for p in levels.iterdir() if p.is_file() and p.suffix.lower() == '.jam'):
            original = fichier.read_bytes()
            data = original
            for cle, cible in CIBLES_RECTANGLES.items():
                scope, ns, ancien, attendu, nom_objet, type_objet = lire_cible_rectangle(cible)
                if scope.lower() == 'levels/*.jam':
                    data = remplacer_rectangle_namespace(data, ns, ancien, p[cle], attendu, f'{fichier.name} / {cle}', nom_objet, type_objet)
            sauver(fichier, original, data)
    else:
        print('[INTROUVABLE] Levels')
    appliquer_polices_par_langue(data_root, p, langue)
    print('-' * 70)
    print('[V3]', edition, langue.upper(), '| PATCH =', compteurs['PATCH'], '| DEJA_OK =', compteurs['DEJA_OK'], '| INTROUVABLE =', compteurs['INTROUVABLE'], '| AMBIGU =', compteurs['AMBIGU'])
    print('-' * 70)
