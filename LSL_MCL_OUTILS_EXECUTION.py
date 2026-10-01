"""Services ExecutionOutils pour Larry MCL."""
from pathlib import Path
import shutil
import subprocess
import hashlib
import urllib.request
import time
import LSL_MCL_VARIABLES as V

class ExecutionOutils:
    """Services internes exposés par LSL_MCL_Outils."""

    @classmethod
    def telecharger(cls, url, destination):
        """Télécharge en blocs avec progression, temporisation et fichier atomique.

        Le délai réseau limite chaque attente de connexion/lecture. La durée
        totale est également contrôlée entre les blocs reçus.
        """
        if not V.ACTIVE_TELECHARGEMENT_OUTILS:
            raise RuntimeError('Téléchargement désactivé : telecharger')
        destination = Path(destination)
        temporaire = destination.with_name(destination.name + '.part')
        destination.parent.mkdir(parents=True, exist_ok=True)
        print('[DOWNLOAD]', url, flush=True)
        requete = urllib.request.Request(url, headers={'User-Agent': 'Larry-MCL-All-In-One'})
        debut = time.monotonic()
        limite_secondes = 8 * 60
        recus = 0
        derniere_info = debut
        cls.supprimer(temporaire)
        try:
            with urllib.request.urlopen(requete, timeout=15) as reponse:
                longueur = reponse.headers.get('Content-Length')
                total = int(longueur) if longueur and longueur.isdigit() else None
                print('[DOWNLOAD] Connexion établie ; taille :', f'{total / 1048576:.1f} Mio' if total else 'inconnue', flush=True)
                with temporaire.open('wb') as fichier:
                    while True:
                        if time.monotonic() - debut > limite_secondes:
                            raise TimeoutError('durée maximale de 8 minutes dépassée')
                        bloc = reponse.read(256 * 1024)
                        if not bloc:
                            break
                        fichier.write(bloc)
                        recus += len(bloc)
                        maintenant = time.monotonic()
                        if maintenant - derniere_info >= 1 or (total and recus >= total):
                            taille = f'{recus / 1048576:.1f} Mio'
                            pourcentage = f' / {total / 1048576:.1f} Mio ({recus / total:.1%})' if total else ''
                            print(f'[DOWNLOAD] {taille}{pourcentage}', flush=True)
                            derniere_info = maintenant
            if recus == 0 or (total is not None and recus != total):
                raise IOError(f'Téléchargement incomplet : {recus}/{total} octets')
            temporaire.replace(destination)
            print(f'[DOWNLOAD] Terminé : {recus / 1048576:.1f} Mio', flush=True)
            return destination
        except (OSError, TimeoutError) as erreur:
            raise RuntimeError(f'Téléchargement interrompu : {erreur}') from erreur
        except Exception:
            raise
        finally:
            cls.supprimer(temporaire)

    @staticmethod
    def sha256(data):
        """Renvoie l’empreinte SHA-256 hexadécimale des octets fournis."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def outil(nom):
        """Cherche un outil dans les dossiers du projet puis dans le PATH."""
        candidats = (V.ROOT / nom, V.OUTILS / nom, V.AFSPACKER_DIR / nom, V.SFD_MUXER_C_DIR / nom, V.VENDOR / nom)
        for candidat in candidats:
            if candidat.exists():
                return str(candidat)
        return shutil.which(nom)

    @staticmethod
    def commande(args):
        """Exécute une commande et renvoie son code de sortie, stdout et stderr."""
        resultat = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors='ignore')
        return (resultat.returncode, resultat.stdout, resultat.stderr)
