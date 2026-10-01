"""Géométrie des langues libres : NL, PT, PL, SV et tout autre code valide.

Les 246 paramètres de base proviennent du profil EN. Les changements ci-dessous
appartiennent aux autres langues et ne modifient jamais le profil EN lui-même.
Ajoute un code dans PROFILS_PAR_LANGUE pour régler une langue indépendamment.
"""

import re

from LSL_MCL_GEO_LANGUAGES_EN import PROFIL_GEOMETRIE as PROFIL_PC_EN


# Paramètres communs aux langues traduites hors des cinq profils PS2.
# [AUTRES > MENUS PARTAGÉS] TITLE/PItem : blanc, gris désactivé, jaune survol.
PROFIL_COMMUN = {
    'title_x': 0.34,
    'title_gr_x': 0.34,
    'title_s_x': 0.34,
    # [AUTRES > TITRES DE MENU] STITLE : blanc, jaune survol, gris désactivé.
    'stitle_x': 0.31,
    'stitle_s_x': 0.31,
    'stitle_g_x': 0.31,
    # [AUTRES > SOUS-TITRES] STITLESM : taille horizontale du texte.
    'stitlesm_x': 0.19,
    # [AUTRES > LISTES / QUÊTES] ITITLE : blanc, jaune survol, gris.
    'ititle_x': 0.18,
    'ititle_s_x': 0.18,
    'ititle_g_x': 0.18,
    # [AUTRES > DESCRIPTIONS] DESC_WHT et DESC_GRY : blanc et gris.
    'desc_wht_x': 0.48,
    'desc_gry_x': 0.48,
}

# [AUTRES > LANGUE PRÉCISE] Les clés sont celles du profil EN : rectangles,
# textes individuels (mn_new_actif_x, mn_new_jaune_x, pause_1_actif_x, etc.)
# et styles globaux (gdef_ws_x, gdef_s_x, etc.). Aucun réglage d'une langue
# dans ce dictionnaire ne change les autres langues.
PROFILS_PAR_LANGUE = {
    # 'nl': {'mn_new_actif_x': 0.36, 'mn_new_jaune_x': 0.45},
    # 'pt-br': {'menu_principal_rectangle': (161.0, 250.0, 461.0, 355.0)},
}


def geometrie(code):
    """Retourne un profil complet, neuf et indépendant pour une langue libre."""
    code = str(code or '').strip().lower()
    if not re.fullmatch(r'[a-z]{2,3}(?:-[a-z0-9]{2,8})*', code):
        raise ValueError(f'Code de langue invalide : {code!r}')
    valeurs = PROFILS_PAR_LANGUE.get(code, {})
    inconnues = (set(PROFIL_COMMUN) | set(valeurs)) - set(PROFIL_PC_EN)
    if inconnues:
        raise ValueError(f'Paramètres géométriques inconnus ({code}) : '
                         + ', '.join(sorted(inconnues)))
    profil = PROFIL_PC_EN.copy()
    profil.update(PROFIL_COMMUN)
    profil.update(valeurs)
    profil['edition'] = 'PC_TRANSLATION_' + code.upper()
    return profil
