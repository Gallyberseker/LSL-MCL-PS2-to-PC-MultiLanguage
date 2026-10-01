"""Localisation audio des cinématiques SFD en conservant la vidéo PC."""
from LSL_MCL_VIDEO_SFD import TraitementSfd
from LSL_MCL_VIDEO_LOCALISATION import LocalisationCinema


class LSL_MCL_Videos(TraitementSfd, LocalisationCinema):
    """Expose la sélection des sources PS2 et le traitement SFD avec l’interface du projet."""
