"""Création des styles individuels et propagation dans les JAM2 préparés."""
from pathlib import Path
import re

def appliquer_polices_par_langue(data_root, profil, langue):
    """Crée les actifs/styles individuels de la langue dans les JAM2, puis les propage.

        Un JAM n'est écrit que si son aller-retour binaire est identique avant
        modification et si tous ses objets et blocs attendus sont présents.
        """
    import LSL_MCL_ACX
    codec = LSL_MCL_ACX.LSL_MCL_Acx
    dossier = Path(data_root) / 'JamFiles' / 'PC'
    principal = (('MenuNew', 'NOUVELLE PARTIE', 'mn_new'), ('MenuLoad', 'CHARGER', 'mn_load'), ('MenuExit', 'QUITTER', 'mn_exit'))
    pause = tuple(((f'PauItm{i:02d}', nom, f'pause_{i}') for i, nom in enumerate(('LIVRE NOIR', 'SAUVEGARDER', 'OPTIONS', 'PHOTOS', 'EXTRAS', 'QUITTER'), 1)))
    titres = (('QUESTS', 'QTITL', 'quete'), ('GIRLDETL', 'ScrTitle', 'fille'), ('COSTUME', 'ScrTitle', 'tenue'), ('INVNTORY', 'ScrTitle', 'objet'), ('STATS', 'ScrTitle', 'stats'))

    def objet(texte, marqueur):
        """Retourne les limites du bloc {...} après un identifiant exact."""
        debut = texte.find(marqueur)
        if debut < 0:
            raise ValueError(f'Objet absent : {marqueur}')
        ouverture = texte.find('{', debut + len(marqueur))
        profondeur = 0
        for fin in range(ouverture, len(texte)):
            if texte[fin] == '{':
                profondeur += 1
            elif texte[fin] == '}':
                profondeur -= 1
                if profondeur == 0:
                    return (debut, fin + 1)
        raise ValueError(f'Bloc incomplet : {marqueur}')

    def ajouter(texte, ouverture_bloc, element):
        """Ajoute une substitution de police au profil en cours."""
        debut, fin = objet(texte, ouverture_bloc)
        compteur = re.search('\\[(\\d+)\\]', texte[debut:fin])
        if compteur is None:
            raise ValueError(f'Compteur absent : {ouverture_bloc}')
        a = debut + compteur.start(1)
        b = debut + compteur.end(1)
        texte = texte[:a] + str(int(compteur.group(1)) + 1) + texte[b:]
        _, fin = objet(texte, ouverture_bloc)
        return texte[:fin - 1] + '\n' + element + '\n' + texte[fin - 1:]

    def remplacer_widget(texte, nom, style, namespace, ancien_style):
        """Remplace le style de police du widget ciblé."""
        debut, fin = objet(texte, f'"Widget" "{nom}"')
        bloc = texte[debut:fin]
        attendu = f'Style "{ancien_style}" "{namespace}"'
        nouveau = f'Style "{style}" "{namespace}"'
        if attendu not in bloc and nouveau not in bloc:
            raise ValueError(f'Style inattendu pour Widget/{nom}')
        if attendu in bloc:
            bloc = bloc.replace(attendu, nouveau, 1)
        return texte[:debut] + bloc + texte[fin:]

    def police(texte, source, nom, valeur):
        """Retourne les paramètres de police du widget."""
        if not 0.01 <= valeur <= 2.0:
            raise ValueError(f'Échelle hors plage : {nom}={valeur}')
        existe = bool(re.search('\\bName\\s+"' + re.escape(nom) + '"', texte))
        marqueur = f'Name "{(nom if existe else source)}"'
        position = texte.find(marqueur)
        if position < 0:
            raise ValueError(f'Actif de police introuvable : {marqueur}')
        ouverture = texte.rfind('{', 0, position)
        if ouverture < 0 or texte[ouverture + 1:position].strip():
            raise ValueError(f'Accolade ouvrante absente pour {nom}')
        profondeur = 0
        fin = None
        for index in range(ouverture, len(texte)):
            if texte[index] == '{':
                profondeur += 1
            elif texte[index] == '}':
                profondeur -= 1
                if profondeur == 0:
                    fin = index + 1
                    break
        if fin is None:
            raise ValueError(f'Accolade fermante absente pour {nom}')
        debut = ouverture
        original = texte[debut:fin]
        copie = original if existe else original.replace(f'Name "{source}"', f'Name "{nom}"', 1)
        copie, nb = re.subn('(\\bScale\\s+)[0-9.]+', lambda m: m.group(1) + f'{valeur:.3f}', copie, count=1)
        if nb != 1:
            raise ValueError(f'Scale absent pour {source}')
        if existe:
            return texte[:debut] + copie + texte[fin:]
        return ajouter(texte, 'Font2DAssets[', copie)

    def style_menu(texte, nom, blanc, gris, jaune):
        """Construit le style de police d’une entrée du menu."""
        if f'Style "{nom}"' in texte:
            return texte
        debut, fin = objet(texte, 'Style "PItem"')
        copie = texte[debut:fin].replace('Style "PItem"', f'Style "{nom}"', 1)
        for ancien, nouveau in (('TITLE_GR', gris), ('TITLE_S', jaune), ('TITLE', blanc)):
            copie = copie.replace(f'Font2DAsset "{ancien}" "Global"', f'Font2DAsset "{nouveau}" "Global"')
        return ajouter(texte, 'Style[', copie)

    def style_liste_filles(texte, nom, blanc, gris, jaune):
        """Duplique ListItem/BBook pour la liste dynamique des filles.

            Le diagnostic PC montre que le texte d'une entrée du Livre noir
            est piloté par ITITLE_G / ITITLE / ITITLE_S dans Style ListItem.
            On crée donc un style dédié au lieu de modifier ces actifs globaux.
            """
        existe = f'Style "{nom}"' in texte
        debut, fin = objet(texte, f'''Style "{(nom if existe else 'ListItem')}"''')
        copie = texte[debut:fin].replace('Style "ListItem"', f'Style "{nom}"', 1)
        for ancien, nouveau in (('ITITLE_G', gris), ('ITITLE_S', jaune), ('ITITLE', blanc)):
            copie = copie.replace(f'Font2DAsset "{ancien}" "Global"', f'Font2DAsset "{nouveau}" "Global"')
        if existe:
            return texte[:debut] + copie + texte[fin:]
        return ajouter(texte, 'Style[', copie)

    def style_texte_filles(texte, nom, principal, secondaire):
        """Duplique TextCC avec ses états et remplace ses références de police."""
        existe = f'Style "{nom}"' in texte
        debut, fin = objet(texte, f'''Style "{(nom if existe else 'TextCC')}"''')
        copie = texte[debut:fin].replace('Style "TextCC"', f'Style "{nom}"', 1)
        copie, nombre = re.subn('Font2DAsset\\s+"[^\\"]+"\\s+"Global"(?:\\s+"[^\\"]+"\\s+"Global")?', f'Font2DAsset "{principal}" "Global"', copie)
        if not nombre:
            raise ValueError(f'Font2DAsset absent dans TextCC/{nom}')
        if existe:
            return texte[:debut] + copie + texte[fin:]
        return ajouter(texte, 'Style[', copie)

    def definir_polices_widget(texte, nom, principal, secondaire):
        """Isole les deux Font2DAsset d'un widget précis de GirlDetl.

            Dans un widget, Font2DAsset contient deux paires nom/namespace.
            Cette syntaxe diffère de la référence dans un style.
            ToknText hérite de TextCC ; ses deux polices sont explicitées.
            """
        debut, fin = objet(texte, f'"Widget" "{nom}"')
        bloc = texte[debut:fin]
        ligne = f'Font2DAsset "{principal}" "Global" "{secondaire}" "Global"'
        motif = re.compile('Font2DAsset\\s+"[^"]+"\\s+"Global"(?:\\s+"[^"]+"\\s+"Global")?')
        if motif.search(bloc):
            bloc = motif.sub(ligne, bloc, count=1)
        else:
            style = re.search('(^[ \\t]*Style\\s+"[^"]+"\\s+"[^"]+"[^\\r\\n]*[\\r\\n]+)', bloc, flags=re.MULTILINE)
            if not style:
                raise ValueError(f'Style introuvable dans Widget/{nom}')
            indentation = re.match('[ \\t]*', style.group(1)).group(0)
            insertion = style.end(1)
            bloc = bloc[:insertion] + indentation + '\t' + ligne + '\n' + bloc[insertion:]
        return texte[:debut] + bloc + texte[fin:]

    def style_titre(texte, nom, actif):
        """Construit le style de police d’un titre."""
        if f'Style "{nom}"' in texte:
            return texte
        debut, fin = objet(texte, 'Style "ScrTitle"')
        copie = texte[debut:fin].replace('Style "ScrTitle"', f'Style "{nom}"', 1)
        copie = copie.replace('Font2DAsset "TITLE" "Global"', f'Font2DAsset "{actif}" "Global"', 1)
        return ajouter(texte, 'Style[', copie)

    def appliquer_namespace(texte, namespace, fonction):
        """Applique une transformation uniquement dans chaque section NameSpace ciblée.

            Important pour les WGG qui embarquent plusieurs écrans/namespaces dans
            un même bloc. Cela évite de modifier le premier Widget homonyme d'un
            autre écran.
            """
        motif = re.compile('(?m)^NameSpace\\s+"' + re.escape(namespace) + '"\\s*$')
        positions = list(motif.finditer(texte))
        if not positions:
            raise ValueError(f'NameSpace absent : {namespace}')
        remplacements = []
        for index, match in enumerate(positions):
            debut = match.start()
            suivant = re.search('(?m)^NameSpace\\s+"[^"]+"\\s*$', texte[match.end():])
            fin = match.end() + suivant.start() if suivant else len(texte)
            section = texte[debut:fin]
            remplacements.append((debut, fin, fonction(section)))
        for debut, fin, section in reversed(remplacements):
            texte = texte[:debut] + section + texte[fin:]
        return texte

    def transformer(jam, modifications):
        """Transforme un style de police selon le profil."""
        if not jam.is_file():
            raise FileNotFoundError(jam)
        archive = codec._jam2_acx_lire(jam)
        if codec._jam2_acx_reconstruire(archive) != archive['raw']:
            raise ValueError(f'Aller-retour JAM2 différent : {jam.name}')
        trouve = set()
        for action in modifications:
            nom, extension, namespace, fonction = action[:4]
            optionnel = len(action) > 4 and bool(action[4])
            marqueur = action[5] if len(action) > 5 else None
            ns_bytes = b'NameSpace "' + namespace.encode('ascii') + b'"'
            if nom == '*' and extension == '*':
                marqueur_bytes = marqueur.encode('latin1') if isinstance(marqueur, str) else marqueur
                candidats = [bloc for bloc in archive['blocs'] if ns_bytes in bloc['data'] and (marqueur_bytes is None or marqueur_bytes in bloc['data'])]
            else:
                candidats = [bloc for bloc in archive['blocs'] if (nom, extension) in bloc['cles'] and ns_bytes in bloc['data'][:350]]
            if not candidats and optionnel:
                continue
            if not candidats:
                raise ValueError(f'{jam.name} : {nom}.{extension}/{namespace} : bloc absent')
            if nom != '*' and len(candidats) != 1:
                raise ValueError(f'{jam.name} : {nom}.{extension}/{namespace} : {len(candidats)} bloc(s), attendu 1')
            for bloc in candidats:
                if bloc['cs'] != bloc['ds']:
                    raise ValueError(f'Bloc compressé : {jam.name}/{nom}.{extension}')
                ancien = bloc['data'].decode('latin1')
                if nom == '*' and extension == '*':
                    nouveau = appliquer_namespace(ancien, namespace, fonction)
                else:
                    nouveau = fonction(ancien)
                bloc['data'] = bytearray(nouveau.encode('latin1'))
            trouve.add((nom, extension, namespace))
        resultat = codec._jam2_acx_reconstruire(archive)
        controle = jam.with_suffix(f'.verification_{langue}.jam')
        try:
            controle.write_bytes(resultat)
            relu = codec._jam2_acx_lire(controle)
            if codec._jam2_acx_reconstruire(relu) != resultat:
                raise ValueError(f'JAM2 reconstruit non stable : {jam.name}')
        finally:
            controle.unlink(missing_ok=True)
        return (resultat, trouve)
    groupes = principal + pause
    for numero, (_, libelle, cle) in enumerate(groupes):
        ecran = 'MENU DÉMARRER' if numero < len(principal) else 'MENU PAUSE'
        print(f"[GEOMETRIE {langue.upper()} TAILLE TEXTE > {ecran} > {libelle}] {cle}_actif_x={profil[f'{cle}_actif_x']} (blanc) | {cle}_gris_x={profil[f'{cle}_gris_x']} (désactivé) | {cle}_jaune_x={profil[f'{cle}_jaune_x']} (survol)")
    for _, (_, _, cle) in enumerate(titres):
        print(f"[GEOMETRIE {langue.upper()} TAILLE TEXTE > LIVRE NOIR > {cle.upper()}] {cle}_titre_actif_x={profil[f'{cle}_titre_actif_x']} (titre blanc, sans état de survol)")
    if all((cle in profil for cle in ('fille_liste_actif_x', 'fille_liste_gris_x', 'fille_liste_jaune_x'))):
        print(f"[GEOMETRIE {langue.upper()} TAILLE TEXTE > LIVRE NOIR > FILLES > LISTE GAUCHE] ITITLE={profil['fille_liste_actif_x']} (normal) | ITITLE_G={profil['fille_liste_gris_x']} (désactivé) | ITITLE_S={profil['fille_liste_jaune_x']} (sélection) | AUW+WGG")
    if 'fille_texte_milieu_gdef_x' in profil:
        print(f"[GEOMETRIE {langue.upper()} TAILLE TEXTE > LIVRE NOIR > FILLES > DROITE] ToknLabl={profil['fille_texte_milieu_gdef_x']}/{profil['fille_texte_milieu_ititle_x']} | ToknText={profil['fille_token_texte_gdef_x']}/{profil['fille_token_texte_ititle_x']}")

    def actifs(texte):
        """Réunit les éléments géométriques actifs du profil."""
        for i, (_, _, cle) in enumerate(groupes):
            for suffixe, source, etat in (('W', 'TITLE', 'actif'), ('G', 'TITLE_GR', 'gris'), ('Y', 'TITLE_S', 'jaune')):
                texte = police(texte, source, f'F{i:02d}{suffixe}', float(profil[f'{cle}_{etat}_x']))
        for i, (_, _, cle) in enumerate(titres):
            texte = police(texte, 'TITLE', f'FB{i:02d}W', float(profil[f'{cle}_titre_actif_x']))
        if all((cle in profil for cle in ('fille_liste_actif_x', 'fille_liste_gris_x', 'fille_liste_jaune_x'))):
            texte = police(texte, 'ITITLE', 'FGLW', float(profil['fille_liste_actif_x']))
            texte = police(texte, 'ITITLE_G', 'FGLG', float(profil['fille_liste_gris_x']))
            texte = police(texte, 'ITITLE_S', 'FGLY', float(profil['fille_liste_jaune_x']))
        if 'fille_texte_milieu_gdef_x' in profil:
            texte = police(texte, 'GDEF_W', 'FGMW', float(profil['fille_texte_milieu_gdef_x']))
            texte = police(texte, 'ITITLE', 'FGMI', float(profil['fille_texte_milieu_ititle_x']))
            texte = police(texte, 'GDEF_W', 'FGBW', float(profil['fille_token_texte_gdef_x']))
            texte = police(texte, 'ITITLE', 'FGBI', float(profil['fille_token_texte_ititle_x']))
        if 'chargement_message_dore_x' in profil:
            texte = police(texte, 'ITITLE_S', 'FLOADMSG', float(profil['chargement_message_dore_x']))
        return texte

    def styles(texte):
        """Retourne les styles du profil géométrique."""
        for i, (_, _, _) in enumerate(groupes):
            texte = style_menu(texte, f'FPI{i:02d}', f'F{i:02d}W', f'F{i:02d}G', f'F{i:02d}Y')
        if 'fille_texte_milieu_gdef_x' in profil:
            texte = style_texte_filles(texte, 'FGMID', 'FGMW', 'FGMI')
            texte = style_texte_filles(texte, 'FGTOKEN', 'FGBW', 'FGBI')
        if 'chargement_message_dore_x' in profil:
            debut, fin = objet(texte, 'Style "LoadFG"')
            bloc, nombre = re.subn('Font2DAsset\\s+"(?:ITITLE_S|FLOADMSG)"\\s+"Global"', 'Font2DAsset "FLOADMSG" "Global"', texte[debut:fin])
            if nombre != 1:
                raise ValueError('Police du message doré LoadFG introuvable.')
            texte = texte[:debut] + bloc + texte[fin:]
        return texte

    def widgets(texte, items, debut_index):
        """Retourne les widgets du profil géométrique."""
        for i, (widget, _, _) in enumerate(items, debut_index):
            texte = remplacer_widget(texte, widget, f'FPI{i:02d}', 'Global', 'PItem')
        return texte
    app = dossier / 'AppInit.JAM'
    intro = dossier / 'IntrFram.JAM'
    actions_app = [('ASSETS', 'AUA', 'Global', actifs), ('STYLES', 'AUS', 'Global', styles), ('PAUSMENU', 'AUW', 'PausMenu', lambda s: widgets(s, pause, len(principal)))]
    actions_intro = [('WIDGETS', 'AUW', 'Intro', lambda s: widgets(s, principal, 0))]
    travaux = [(app, actions_app), (intro, actions_intro)]
    niveaux = sorted(p for p in (dossier / 'Levels').glob('*') if p.is_file() and p.suffix.lower() == '.jam')
    if not niveaux:
        raise FileNotFoundError(f"Aucun niveau à propager : {dossier / 'Levels'}")
    for level in niveaux:

        def styles_livre(s):
            """Isole les styles BBook et applique les polices spécifiques par langue."""
            if 'Style "ScrTitle"' in s:
                for i, _ in enumerate(titres):
                    s = style_titre(s, f'FBT{i:02d}', f'FB{i:02d}W')
            if 'Style "ListItem"' in s and re.search('\\bStyle\\s*\\[\\s*\\d+\\s*\\]\\s*[\\r\\n\\t ]*\\{', s) and all((cle in profil for cle in ('fille_liste_actif_x', 'fille_liste_gris_x', 'fille_liste_jaune_x'))):
                s = style_liste_filles(s, 'ListItem', 'FGLW', 'FGLG', 'FGLY')
                s = style_liste_filles(s, 'FGLIST', 'FGLW', 'FGLG', 'FGLY')
            return s

        def polices_pose(s):
            s = police(s, 'LeadFont', 'LeadFont', float(profil['pose_classement_x']))
            return police(s, 'TimeFont', 'TimeFont', float(profil['pose_chronometre_x']))

        def polices_quarters(s):
            s = police(s, 'FDBKSMAL', 'FDBKSMAL', float(profil['quarters_indice_petit_x']))
            return police(s, 'FDBKBIG', 'FDBKBIG', float(profil['quarters_indice_grand_x']))
        actions = [('*', '*', 'BBook', styles_livre, False, 'Style "ListItem"'), ('ASSETS', 'AUA', 'WndrPose', polices_pose, True), ('ASSETS', 'AUA', 'Quarters', polices_quarters, True)]
        for i, (fichier, widget, _) in enumerate(titres):
            namespace = 'GirlDetl' if fichier == 'GIRLDETL' else 'Invntory' if fichier == 'INVNTORY' else fichier.title() if fichier != 'QUESTS' else 'Quests'
            actions.append(('*', '*', namespace, lambda sec, w=widget, n=i: remplacer_widget(sec, w, f'FBT{n:02d}', 'BBook', 'ScrTitle'), False, f'"Widget" "{widget}"'))
        if all((cle in profil for cle in ('fille_liste_actif_x', 'fille_liste_gris_x', 'fille_liste_jaune_x'))):

            def raccorder_item_livre_noir(sec, nom_widget):
                debut, fin = objet(sec, f'"Widget" "{nom_widget}"')
                bloc = sec[debut:fin]
                motif_style = re.compile('Style\\s+"Screen"\\s+"Global"')
                nouveau = 'Style "FGLIST" "BBook"'
                if nouveau in bloc:
                    return sec
                if not motif_style.search(bloc):
                    raise ValueError(f'Style inattendu dans {nom_widget}')
                bloc = motif_style.sub(nouveau, bloc, count=1)
                return sec[:debut] + bloc + sec[fin:]
            actions.append(('*', '*', 'GirlDetl', lambda sec: raccorder_item_livre_noir(sec, 'GirlItem'), False, '"Widget" "GirlItem"'))
            actions.append(('*', '*', 'GirlHist', lambda sec: raccorder_item_livre_noir(sec, 'GLHItem'), True, '"Widget" "GLHItem"'))
        if 'fille_texte_milieu_gdef_x' in profil:
            actions.append(('*', '*', 'GirlDetl', lambda sec: remplacer_widget(definir_polices_widget(definir_polices_widget(remplacer_widget(sec, 'ToknLabl', 'FGMID', 'Global', 'TextCC'), 'ToknLabl', 'FGMW', 'FGMI'), 'ToknText', 'FGBW', 'FGBI'), 'ToknText', 'FGTOKEN', 'Global', 'TextCC'), False, '"Widget" "ToknLabl"'))
        travaux.append((level, actions))
    sorties = []
    for jam, actions in travaux:
        resultat, trouve = transformer(jam, actions)
        sorties.append((jam, resultat, trouve, actions))
    for jam, resultat, trouve, actions in sorties:
        sections = []
        for action in actions:
            nom, extension, namespace = action[:3]
            if (nom, extension, namespace) not in trouve:
                continue
            if extension == 'AUA' and namespace == 'WndrPose':
                sections.extend(('pose_classement_x', 'pose_chronometre_x'))
            elif extension == 'AUA' and namespace == 'Quarters':
                sections.extend(('quarters_indice_petit_x', 'quarters_indice_grand_x'))
            elif extension == 'AUS' and namespace == 'BBook':
                sections.extend((f'{cle}_titre_actif_x' for _, _, cle in titres))
            elif jam == app and extension == 'AUA':
                sections.extend((f'{cle}_{etat}_x' for _, _, cle in groupes for etat in ('actif', 'gris', 'jaune')))
                if all((cle in profil for cle in ('fille_liste_actif_x', 'fille_liste_gris_x', 'fille_liste_jaune_x'))):
                    sections.extend(('fille_liste_actif_x', 'fille_liste_gris_x', 'fille_liste_jaune_x'))
            elif jam == intro and extension == 'AUW':
                sections.extend((f'{cle}_{etat}_x' for _, _, cle in principal for etat in ('actif', 'gris', 'jaune')))
        if jam.read_bytes() != resultat:
            jam.write_bytes(resultat)
            print(f"[GEOMETRIE {langue.upper()} PROPAGATION > {jam.name}] {len(trouve)} blocs vérifiés ; paramètres : {(', '.join(sections) if sections else 'styles des menus')}")
        else:
            print(f"[GEOMETRIE {langue.upper()} PROPAGATION > {jam.name}] déjà conforme ; paramètres : {(', '.join(sections) if sections else 'styles des menus')}")
