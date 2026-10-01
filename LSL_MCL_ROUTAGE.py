"""Résolution différée des opérations optionnelles accessibles au menu."""
from importlib import import_module

_OPERATIONS = {
    "injecter_langue_ps2": ("LSL_MCL_INJECTIONS", "LSL_MCL_Injection"),
    "diagnostiquer_videos_audio": ("LSL_MCL_DIAGNOSTICS", "LSL_MCL_Diagnostics"),
    "diagnostiquer_textes_jam": ("LSL_MCL_DIAGNOSTICS", "LSL_MCL_Diagnostics"),
    "diagnostiquer_menus_interfaces": ("LSL_MCL_DIAGNOSTICS", "LSL_MCL_Diagnostics"),
}


class LSL_MCL_Routages:
    """Charge seulement le service demandé par le contrôleur."""

    @staticmethod
    def resoudre_option(nom):
        """Renvoie une opération connue ou None ; une liaison cassée lève une erreur."""
        destination = _OPERATIONS.get(nom)
        if destination is None:
            return None
        module, classe = destination
        return getattr(getattr(import_module(module), classe), nom)
