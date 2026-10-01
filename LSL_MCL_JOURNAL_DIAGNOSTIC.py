"""Journaux spécialisés des diagnostics de Larry MCL."""
from pathlib import Path

class JournalDiagnostic:
    """Centralise les logs, avertissements et erreurs du diagnostic."""

    def __init__(self, dossier):
        """Prépare les journaux spécialisés et initialise les compteurs du diagnostic."""
        dossier = Path(dossier)
        from datetime import datetime
        self.dossier = dossier
        self.logs = dossier / 'Logs'
        self.logs.mkdir(parents=True, exist_ok=True)
        self.date_debut = datetime.now()
        self.erreurs = []
        self.avertissements = []
        self.sections = {'execution': '00_EXECUTION_COMPLETE.log', 'environnement': '01_ENVIRONNEMENT.log', 'pc': '02_INVENTAIRE_PC.log', 'ps2': '03_INVENTAIRE_PS2.log', 'comparaison': '04_CORRESPONDANCES_PC_PS2.log', 'structure': '05_STRUCTURE_DOSSIERS.log', 'jam': '06_CARTE_BINAIRE_JAM.log', 'textes': '07_TEXTES.log', 'polices': '08_POLICES.log', 'menus': '09_MENUS_INTERFACES.log', 'images': '10_IMAGES.log', 'palettes': '11_PALETTES.log', 'adx': '12_AUDIO_ADX.log', 'afs': '13_ARCHIVES_AFS.log', 'sfd': '14_CINEMATIQUES_SFD.log', 'sous_titres': '15_SOUS_TITRES_DIALOGUES.log', 'liaisons': '16_LIAISONS_RESSOURCES.log', 'compatibilite': '17_COMPATIBILITE.log', 'erreurs': '18_ERREURS_AVERTISSEMENTS.log', 'injection': '19_PLAN_INJECTION.log', 'reconstruction': '20_PLAN_RECONSTRUCTION.log'}
        for fichier in self.sections.values():
            (self.logs / fichier).write_text('', encoding='utf-8')
        self.ecrire('execution', 'DEMARRAGE DU DIAGNOSTIC COMPLET')

    def attention(self, section, message):
        """Consigne un avertissement dans la section et dans le journal des erreurs."""
        self.ecrire(section, message, 'ATTENTION')

    def ecrire(self, section, message, niveau='INFO'):
        """Affiche une fois le message et l'ajoute aux journaux concernés."""
        from datetime import datetime
        if section not in self.sections:
            section = 'execution'
        heure = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ligne = f'[{heure}] [{niveau}] {message}'
        print(ligne)
        with (self.logs / self.sections[section]).open('a', encoding='utf-8') as flux:
            flux.write(ligne + '\n')
        if section != 'execution':
            with (self.logs / self.sections['execution']).open('a', encoding='utf-8') as flux:
                flux.write(f'[{section.upper()}] {ligne}\n')
        if niveau in ('ERREUR', 'ATTENTION'):
            cible = self.erreurs if niveau == 'ERREUR' else self.avertissements
            cible.append(ligne)
            if section != 'erreurs':
                with (self.logs / self.sections['erreurs']).open('a', encoding='utf-8') as flux:
                    flux.write(ligne + '\n')

    def entete(self, section, titre_section):
        """Ajoute un titre et ses séparateurs dans la section choisie."""
        separation = '=' * 70
        self.ecrire(section, f'\n{separation}\n{titre_section}\n{separation}')

    def erreur(self, section, message):
        """Consigne une erreur dans la section et dans le journal des erreurs."""
        self.ecrire(section, message, 'ERREUR')

    def terminer(self):
        """Consigne la durée et le nombre d’erreurs et d’avertissements."""
        from datetime import datetime
        date_fin = datetime.now()
        duree = (date_fin - self.date_debut).total_seconds()
        self.entete('execution', 'FIN DU DIAGNOSTIC COMPLET')
        self.ecrire('execution', f'Duree : {duree:.2f} secondes')
        self.ecrire('execution', f'Erreurs : {len(self.erreurs)}')
        self.ecrire('execution', f'Avertissements : {len(self.avertissements)}')
