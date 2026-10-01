"""Suivi léger des traitements longs dans la console et ses journaux."""
from datetime import datetime, timedelta
from time import monotonic


class SuiviProgression:
    """Affiche l'avancement en limitant la fréquence des logs intermédiaires."""

    def __init__(self, libelle, total, intervalle=1.0):
        """Initialise un total connu ou None et un délai d'affichage en secondes."""
        self.libelle = libelle
        self.total = total
        self.intervalle = max(0.0, intervalle)
        self.debut = monotonic()
        self.dernier_affichage = None
        self.termine = 0
        self._dernier_nombre_affiche = None
        print(f"[{libelle}] Début : {total} élément(s)" if total is not None
              else f"[{libelle}] Début : nombre d'éléments inconnu")

    def avancer(self, nombre, fichier=None):
        """Enregistre l'avancement et affiche le premier état ou une mise à jour."""
        self.termine = nombre
        self._afficher(nombre, fichier)

    def _afficher(self, nombre, fichier=None, forcer=False):
        """Formate l'état et son estimation sans dépasser la fréquence choisie."""
        maintenant = monotonic()
        fin_atteinte = (self.total is not None and nombre >= self.total
                        and self._dernier_nombre_affiche != nombre)
        if (not forcer and not fin_atteinte and self.dernier_affichage is not None
                and maintenant - self.dernier_affichage < self.intervalle):
            return
        self.dernier_affichage = maintenant
        self._dernier_nombre_affiche = nombre
        if self.total is None:
            etat = f"{nombre} traité(s) | en cours"
        else:
            fraction = max(0.0, min(1.0, nombre / self.total)) if self.total > 0 else 1.0
            largeur = 30
            rempli = round(fraction * largeur)
            barre = "█" * rempli + "░" * (largeur - rempli)
            etat = f"[{barre}] {nombre}/{self.total} {fraction:.1%}"
            if 0 < fraction < 1:
                ecoule = maintenant - self.debut
                fin = datetime.now() + timedelta(seconds=ecoule * (1 / fraction - 1))
                etat += " | fin estimée " + fin.strftime("%H:%M:%S")
        cible = f" | {fichier}" if fichier is not None else ""
        print(f"[{self.libelle}] {etat}{cible}")

    def terminer(self):
        """Affiche l'état final s'il manque, puis la durée totale du traitement."""
        if self.total is not None:
            self.termine = self.total
        if self._dernier_nombre_affiche != self.termine:
            self._afficher(self.termine, forcer=True)
        print(f"[{self.libelle}] Terminé en {monotonic() - self.debut:.1f} s")
