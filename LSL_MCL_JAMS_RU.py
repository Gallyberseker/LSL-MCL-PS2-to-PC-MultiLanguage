"""Construction des JAM PC depuis les JAM PS2 russes correspondants."""

from pathlib import Path

import LSL_MCL_VARIABLES as V
from LSL_MCL_CONSTRUCTION_RU import ConstructeurAppInitRusse
from LSL_MCL_SUIVI import SuiviProgression
from LSL_MCL_ECRITURE_JAM import publier_jam
from LSL_MCL_TEXTES import LSL_MCL_Textes


class ConstructionJamsRusses:
    """Écrit les JAM russes dans une arborescence PC de sortie isolée."""

    @staticmethod
    def choisir_source_pc(game_root, source_initiale):
        """Choisit parmi les sources prévues celle qui conserve les textes PC à traduire."""
        ps2 = next((p for p in (V.PS2_VERSION / "Data").rglob("*")
                    if p.is_file() and p.name.casefold() == "appinit.jam"
                    and "ps2" in (x.casefold() for x in p.parts)), None)
        if ps2 is None:
            raise FileNotFoundError("AppInit.JAM PS2 russe introuvable.")
        russe = ps2.read_bytes()
        candidats = (Path(source_initiale), V.PC_VERSION_BACKUP / "Data",
                    V.PC_VERSION / "Data", Path(game_root) / "Data")
        scores = []
        for data in dict.fromkeys(candidats):
            appinit = data / "JamFiles" / "PC" / "AppInit.JAM"
            if not appinit.is_file():
                continue
            try:
                _, nombre = ConstructeurAppInitRusse.construire(
                    appinit.read_bytes(), russe, inclure_polices=True)
            except (OSError, ValueError, RuntimeError) as erreur:
                print(f"[RU SOURCE] {data} : incompatible ({erreur})")
                continue
            scores.append((nombre, data))
            print(f"[RU SOURCE] {data} : {nombre} chaînes à transférer")
        if not scores:
            raise RuntimeError("Aucune source PC compatible avec APPINIT russe.")
        nombre, data = max(scores, key=lambda candidat: candidat[0])
        if nombre < len(ConstructeurAppInitRusse._textes(russe)) // 4:
            raise RuntimeError(
                "Les sources PC semblent déjà localisées : seulement "
                f"{nombre} chaînes APPINIT à transférer. Restaurer une copie "
                "PC anglaise propre dans PC_VERSION_BACKUP ou PC_VERSION.")
        print("[RU SOURCE PC RETENUE]", data)
        return data

    @staticmethod
    def _indexer(racine, edition):
        """Indexe les JAM selon leur chemin à partir de PC ou PS2."""
        edition = edition.casefold()
        index = {}
        for chemin in sorted(Path(racine).rglob("*")):
            if not chemin.is_file() or chemin.suffix.casefold() != ".jam":
                continue
            parties = chemin.relative_to(racine).parts
            positions = [i for i, nom in enumerate(parties)
                         if nom.casefold() == edition]
            if positions:
                identifiant = tuple(p.casefold() for p in parties[positions[-1] + 1:])
                if identifiant in index:
                    raise ValueError(f"Nom JAM dupliqué : {chemin}")
                index[identifiant] = chemin
        return index


    @staticmethod
    def construire(source_pc, source_ru, destination):
        """Génère les JAM russes appariés et affiche les résultats en console.

        Retourne (nombre de JAM créés, chaînes transférées, erreurs).
        """
        source_pc, source_ru = Path(source_pc), Path(source_ru)
        destination = Path(destination)
        index_pc = ConstructionJamsRusses._indexer(source_pc, "pc")
        index_ru = ConstructionJamsRusses._indexer(source_ru, "ps2")
        if not index_pc or not index_ru:
            raise RuntimeError("JAM PC ou PS2 absents des dossiers Data.")
        progression = SuiviProgression("JAM RUSSES", len(index_ru))
        reussis = ignores = erreurs = 0
        par_nom = {}
        for identifiant, chemin in index_pc.items():
            par_nom.setdefault(identifiant[-1], []).append(chemin)
        total = 0
        for numero, (identifiant, ps2) in enumerate(sorted(index_ru.items()), 1):
            candidats = par_nom.get(identifiant[-1], ())
            pc = index_pc.get(identifiant)
            if pc is None and len(candidats) == 1:
                pc = candidats[0]
            try:
                if pc is None:
                    ignores += 1
                    print(f"[RU IGNORE] {ps2.name} : aucun JAM PC correspondant")
                    continue
                source = ps2.read_bytes()
                if not LSL_MCL_Textes.blocs_texte(source):
                    ignores += 1
                    print(f"[RU IGNORE] {ps2.name} : aucun bloc de texte reconnu")
                    continue
                resultat, nombre = ConstructeurAppInitRusse.construire(
                    pc.read_bytes(), source,
                    inclure_polices=pc.name.casefold() == "appinit.jam")
                if nombre == 0:
                    ignores += 1
                    print(f"[RU IGNORE] {ps2.name} : aucune clé de texte commune")
                    continue
                relatif = pc.relative_to(source_pc)
                sortie = destination / relatif
                sortie.parent.mkdir(parents=True, exist_ok=True)
                publier_jam(sortie, resultat)
                reussis += 1
                print(f"[RU JAM] {relatif} : {nombre} chaînes")
                total += nombre
            except (OSError, ValueError, RuntimeError) as erreur:
                erreurs += 1
                print(f"[RU ERREUR] {ps2.name} : {erreur}")
            finally:
                progression.avancer(numero, ps2.name)
        progression.terminer()
        print(f"[RU BILAN] {reussis} JAM créés ; {total} chaînes ; "
              f"{ignores} ignorés ; {erreurs} erreurs.")
        return reussis, total, erreurs
