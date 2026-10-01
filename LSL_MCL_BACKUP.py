"""Sauvegarde du Data PC original et restauration de l'installation du jeu."""

from pathlib import Path
import shutil
import tempfile

import LSL_MCL_VARIABLES as V
import LSL_MCL_ANALISES
import LSL_MCL_COMPUTER
import LSL_MCL_MENU


class LSL_MCL_Backup:
    """Protège la sauvegarde originale et publie uniquement des copies complètes."""

    @staticmethod
    def _marqueurs(data):
        """Renvoie les marqueurs de localisation et d'interdiction présents."""
        noms = {V.MARQUEUR_LOCALISATION_PC, *V.MARQUEURS_BACKUP_DISABLE.values()}
        return [Path(data) / nom for nom in sorted(noms)
                if (Path(data) / nom).exists()]

    @staticmethod
    def _copier_data(source, destination, remplacer=False):
        """Prépare une copie complète avant publication, avec retour arrière.

        L'ancien Data reste disponible jusqu'à publication de la nouvelle copie.
        Si le retour arrière échoue, son chemin est indiqué et il est conservé.
        Une interruption brutale peut laisser un dossier temporaire voisin ;
        celui-ci n'est jamais pris pour une sauvegarde validée.
        """
        source, destination = Path(source), Path(destination)
        if not source.is_dir():
            raise FileNotFoundError(f"Dossier source introuvable : {source}")
        origine, cible = source.resolve(), destination.resolve()
        if origine == cible or origine in cible.parents or cible in origine.parents:
            raise ValueError("La source et la destination doivent être indépendantes.")
        if destination.exists() and not remplacer:
            raise FileExistsError(f"Destination déjà présente : {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        preparation = Path(tempfile.mkdtemp(
            prefix=f".{destination.name}_copie_", dir=destination.parent))
        nouveau, ancien = preparation / "nouveau", preparation / "ancien"
        conserver = False
        try:
            shutil.copytree(source, nouveau)
            if destination.exists():
                destination.rename(ancien)
            try:
                nouveau.rename(destination)
            except OSError:
                if ancien.exists():
                    try:
                        ancien.rename(destination)
                    except OSError as erreur:
                        conserver = True
                        print(f"[ERREUR] Retour arrière impossible : {erreur}")
                        print(f"[RECUPERATION] Ancien Data conservé : {ancien}")
                raise
        finally:
            if not conserver:
                try:
                    shutil.rmtree(preparation)
                except OSError as erreur:
                    print(f"[NETTOYAGE] Dossier temporaire conservé : {preparation}")
                    print(erreur)

    @staticmethod
    def creer_marqueur_backup_disable(data_version, langue):
        """Marque un Data localisé pour interdire sa sauvegarde comme original."""
        nom = V.MARQUEURS_BACKUP_DISABLE.get(langue.lower())
        if nom is None:
            raise RuntimeError(f"Langue inconnue : {langue}")
        marqueur = Path(data_version) / nom
        marqueur.write_text(
            "BACKUP PC INTERDIT\n\n"
            "Ce dossier Data contient une version modifiee "
            "par l'utilitaire de localisation.\n\n"
            "NE PAS utiliser ce dossier comme backup original.\n\n"
            "Pour recreer un backup valide :\n"
            "1. Reinstaller/restaurer le jeu original avec PC.\n"
            "2. Verifier que le dossier Data est propre.\n"
            "3. Relancer l'utilitaire.\n"
            "4. Laisser l'utilitaire creer un nouveau VERSION_BACKUP.\n",
            encoding="utf-8",
        )
        print("[GARDE-FOU] Marqueur cree :", marqueur.name)

    @staticmethod
    def backup_pc(game_root):
        """Crée le backup et la copie de travail sans sauvegarder un Data localisé.

        Un backup existant est conservé. Les copies sont préparées dans un
        dossier temporaire pour éviter de valider une copie interrompue.
        Renvoie le chemin du backup, ou None si son utilisation est refusée.
        """
        source = Path(game_root) / "Data"
        backup = V.PC_VERSION_BACKUP / "Data"
        reference = backup if backup.exists() else source
        marqueurs = LSL_MCL_Backup._marqueurs(reference)
        if marqueurs:
            print("[BACKUP] Sauvegarde originale refusée : Data marqué comme localisé.")
            for marqueur in marqueurs:
                print("[GARDE-FOU] Marqueur détecté :", marqueur)
            contenu = LSL_MCL_ANALISES.LSL_MCL_Analises.lire_marqueur_localisation_pc(reference)
            for ligne in (contenu or "").splitlines():
                if ligne.startswith(("Version installee :", "Edition PS2_VERSION :")):
                    print(ligne)
            print("Restaurez ou réinstallez une version PC anglaise propre.")
            print("[BACKUP] Aucun backup n'a été créé ou remplacé.")
            return None
        if backup.exists():
            if not backup.is_dir():
                raise NotADirectoryError(f"Backup invalide : {backup}")
            print("[BACKUP] Backup original deja present.")
        else:
            print("[BACKUP] Aucun marqueur de localisation detecte.")
            print("[BACKUP] Creation du backup ORIGINAL...")
            LSL_MCL_Backup._copier_data(source, backup)
            print("[BACKUP] Termine.")
        pc_local = V.PC_VERSION / "Data"
        if not pc_local.exists():
            print("[PC_VERSION] Creation de la copie de travail propre...")
            LSL_MCL_Backup._copier_data(backup, pc_local)
        return backup

    @staticmethod
    def restaurer_data_version_backup(game_root):
        """Remplace le Data du jeu par le backup, sans garder les fichiers ajoutés.

        Renvoie True après publication, False si la restauration est refusée
        ou échoue. La préparation nécessite une copie supplémentaire sur disque.
        """
        LSL_MCL_MENU.LSL_MCL_Menu.titre("RESTAURATION DATA PC VERSION BACKUP")
        source = V.PC_VERSION_BACKUP / "Data"
        destination = Path(game_root) / "Data"
        print("[RESTAURATION] Backup :", source)
        print("[RESTAURATION] Vers le jeu PC :", destination)
        if not source.is_dir():
            print("[ERREUR] Backup introuvable :", source)
            return False
        if LSL_MCL_Backup._marqueurs(source):
            print("[ERREUR] Le backup contient un marqueur de localisation.")
            return False
        LSL_MCL_COMPUTER.LSL_MCL_Computer.fermer_larry()
        try:
            LSL_MCL_Backup._copier_data(source, destination, remplacer=True)
        except PermissionError as erreur:
            print("[ERREUR] Accès refusé ou fichier utilisé :", erreur)
            print("Fermez le jeu et vérifiez les droits d'accès avant de recommencer.")
            return False
        except (OSError, ValueError) as erreur:
            print("[ERREUR RESTAURATION]", erreur)
            return False
        print("[RESTAURATION OK] Le Data original a été restauré dans le jeu PC.")
        return True
