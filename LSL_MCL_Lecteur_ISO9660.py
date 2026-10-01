"""Fonctions du domaine ISO pour Larry MCL."""
from pathlib import Path
import struct
import os
import tempfile
import LSL_MCL_VARIABLES as V
from LSL_MCL_SUIVI import SuiviProgression

class LSL_MCL_Lecteur_ISO9660:
    """Lit et extrait les fichiers des images ISO 9660 PS2."""

    def __init__(self, chemin_iso):
        """Initialise les ressources et paramètres de cette instance."""
        self.chemin_iso = Path(chemin_iso)
        self.fichier = None
        self.racine = None

    def __enter__(self):
        """Ouvre et retourne le lecteur comme gestionnaire de contexte."""
        self.fichier = open(self.chemin_iso, 'rb')
        try:
            self._charger_volume()
        except BaseException:
            self.fichier.close()
            self.fichier = None
            raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ferme le lecteur à la sortie du contexte."""
        if self.fichier:
            self.fichier.close()
            self.fichier = None
            self.racine = None

    def _lire_secteur(self, secteur, nombre=1):
        """Lit un secteur de l’image ISO."""
        self.fichier.seek(secteur * V.SECTOR_SIZE)
        return self.fichier.read(V.SECTOR_SIZE * nombre)

    def _charger_volume(self):
        """Charge les métadonnées du volume ISO 9660."""
        secteur = 16
        while True:
            bloc = self._lire_secteur(secteur)
            if len(bloc) < V.SECTOR_SIZE:
                raise ValueError('ISO9660 invalide.')
            type_volume = bloc[0]
            identifiant = bloc[1:6]
            if identifiant != b'CD001':
                raise ValueError('Ce fichier ne semble pas etre une ISO ISO9660.')
            if type_volume == 1:
                self.racine = self._lire_entree(bloc[156:])
                return
            if type_volume == 255:
                break
            secteur += 1
        raise ValueError('Primary Volume Descriptor ISO9660 introuvable.')

    def _lire_entree(self, donnees):
        """Décode une entrée de répertoire ISO."""
        if not donnees:
            return None
        longueur = donnees[0]
        if longueur == 0:
            return None
        if longueur < 34 or longueur > len(donnees):
            raise ValueError('Entrée ISO 9660 tronquée ou invalide.')
        entree = donnees[:longueur]
        secteur = struct.unpack_from('<I', entree, 2)[0]
        taille = struct.unpack_from('<I', entree, 10)[0]
        flags = entree[25]
        longueur_nom = entree[32]
        if longueur_nom == 0 or 33 + longueur_nom > longueur:
            raise ValueError('Nom de fichier ISO 9660 tronqué.')
        nom_brut = entree[33:33 + longueur_nom]
        if nom_brut == b'\x00':
            nom = '.'
        elif nom_brut == b'\x01':
            nom = '..'
        else:
            nom = nom_brut.decode('ascii', errors='replace')
            if ';' in nom:
                nom = nom.split(';', 1)[0]
        if nom not in ('.', '..') and ('/' in nom or '\\' in nom or ':' in nom or '\x00' in nom):
            raise ValueError('Nom de fichier ISO 9660 invalide.')
        return {'nom': nom, 'secteur': secteur, 'taille': taille, 'dossier': bool(flags & 2)}

    def lister_dossier(self, entree):
        """Énumère les entrées directes du dossier ISO."""
        if not entree['dossier']:
            raise ValueError("L'entree demandee n'est pas un dossier.")
        self.fichier.seek(entree['secteur'] * V.SECTOR_SIZE)
        donnees = self.fichier.read(entree['taille'])
        if len(donnees) != entree['taille']:
            raise OSError('Répertoire ISO tronqué.')
        resultat = []
        position = 0
        while position < len(donnees):
            longueur = donnees[position]
            if longueur == 0:
                position = (position // V.SECTOR_SIZE + 1) * V.SECTOR_SIZE
                continue
            if position % V.SECTOR_SIZE + longueur > V.SECTOR_SIZE:
                raise ValueError('Entrée ISO traversant une limite de secteur.')
            entree_fichier = self._lire_entree(donnees[position:position + longueur])
            position += longueur
            if not entree_fichier:
                continue
            if entree_fichier['nom'] in ('.', '..'):
                continue
            resultat.append(entree_fichier)
        return resultat

    def trouver(self, chemin):
        """Localise une entrée dans l’arborescence ISO."""
        morceaux = [x for x in str(chemin).replace('\\', '/').split('/') if x]
        courant = self.racine
        for morceau in morceaux:
            trouve = None
            for entree in self.lister_dossier(courant):
                if entree['nom'].casefold() == morceau.casefold():
                    trouve = entree
                    break
            if trouve is None:
                return None
            courant = trouve
        return courant

    def lire_fichier(self, entree):
        """Lit le contenu binaire du fichier ISO ciblé."""
        if entree['dossier']:
            raise ValueError('Impossible de lire un dossier comme fichier.')
        self.fichier.seek(entree['secteur'] * V.SECTOR_SIZE)
        donnees = self.fichier.read(entree['taille'])
        if len(donnees) != entree['taille']:
            raise OSError('Fichier ISO tronqué.')
        return donnees

    def extraire_fichier(self, entree, destination):
        """Extrait un fichier par blocs, puis remplace la destination après succès."""
        if entree['dossier']:
            raise ValueError('Impossible d’extraire un dossier comme fichier.')
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        self.fichier.seek(entree['secteur'] * V.SECTOR_SIZE)
        restant = entree['taille']
        descripteur, nom = tempfile.mkstemp(prefix='.iso_', dir=destination.parent)
        temporaire = Path(nom)
        try:
            with os.fdopen(descripteur, 'wb') as sortie:
                while restant > 0:
                    bloc = self.fichier.read(min(1024 * 1024, restant))
                    if not bloc:
                        raise OSError('Fin inattendue de l’ISO.')
                    sortie.write(bloc)
                    restant -= len(bloc)
            os.replace(temporaire, destination)
        finally:
            temporaire.unlink(missing_ok=True)

    def extraire_dossier(self, entree, destination, suivi=None, compteur=None):
        """Extrait un dossier ISO et suit les fichiers traités."""
        principal = suivi is None
        if principal:

            def compter(courant):
                """Compte les fichiers ISO pour calculer une progression exacte."""
                total = 0
                for element in self.lister_dossier(courant):
                    total += compter(element) if element['dossier'] else 1
                return total
            suivi = SuiviProgression('EXTRACTION ISO', compter(entree))
            compteur = [0]
        if compteur is None:
            compteur = [0]
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        for element in self.lister_dossier(entree):
            cible = destination / element['nom']
            if element['dossier']:
                self.extraire_dossier(element, cible, suivi, compteur)
            else:
                self.extraire_fichier(element, cible)
                compteur[0] += 1
                suivi.avancer(compteur[0], cible.name)
        if principal:
            suivi.terminer()

    def detecter_version_ps2(self):
        """Identifie la version PS2 depuis le nom de son exécutable."""
        for entree in self.lister_dossier(self.racine):
            nom = entree['nom'].upper()
            if nom in V.EDITIONS_PS2:
                return nom
        return None
